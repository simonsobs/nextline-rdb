import json
from datetime import timezone
from pathlib import Path
from unittest.mock import Mock

from apluggy import PluginManager
from hypothesis import Phase, given, settings

from nextline import Nextline
from nextline.events import (
    OnEndPrompt,
    OnEndRun,
    OnEndTrace,
    OnEndTraceCall,
    OnStartPrompt,
    OnStartRun,
    OnStartTrace,
    OnStartTraceCall,
    OnWriteStdout,
)
from nextline.plugin import spec
from nextline.spawned import RunArg
from nextline.types import (
    PromptNo,
    RunNo,
    Statement,
    TaskNo,
    ThreadNo,
    TraceCallNo,
    TraceNo,
)
from nextline_rdb.db import DB
from nextline_rdb.models import (
    CurrentScript,
    Model,
    Prompt,
    Run,
    Script,
    Stdout,
    Trace,
    TraceCall,
)
from nextline_rdb.models.strategies import st_model_instance_list
from nextline_rdb.utils import load_all
from nextline_rdb.write import register


def mock_hook() -> PluginManager:
    hook = PluginManager(spec.PROJECT_NAME)
    hook.add_hookspecs(spec)
    return hook


def mock_nextline(hook: PluginManager) -> Nextline:
    nextline = Mock(spec=Nextline)
    nextline.register.side_effect = lambda plugin: hook.register(plugin)
    return nextline


@settings(phases=(Phase.generate,))  # Avoid shrinking
@given(
    instances=st_model_instance_list(
        min_size=0, max_size=5, allow_run_started_at_none=False
    )
)
async def test_write(instances: list[Model]) -> None:
    hook = mock_hook()
    nextline = mock_nextline(hook)
    async with DB(use_migration=False, model_base_class=Model) as db:
        register(nextline, db)

        context = spec.Context(
            nextline=nextline, hook=hook, pubsub=Mock(spec=spec.PubSub)
        )
        for instance in instances:
            match instance:
                case Script():
                    await _handle_script(context=context, script=instance)
                case Run():
                    await _handle_run(context=context, run=instance)
                case _:
                    raise ValueError(f'Unknown instance: {instance!r}')

        async with db.session() as session:
            loaded = await load_all(session, Model)
            loaded = [m for m in loaded if not isinstance(m, CurrentScript)]
            loaded = [m for m in loaded if not isinstance(m, Script)]
            actual = [repr(m) for m in loaded]

    async with DB(use_migration=False, model_base_class=Model) as db:
        async with db.session.begin() as session:
            session.add_all(instances)
        async with db.session() as session:
            loaded = await load_all(session, Model)
            loaded = [m for m in loaded if not isinstance(m, CurrentScript)]
            loaded = [m for m in loaded if not isinstance(m, Script)]
            expected = [repr(m) for m in loaded]

    assert len(actual) == len(expected)

    # TODO: Assert the content. For now, only check the length
    # diff = DeepDiff(expected, actual)


async def _handle_script(context: spec.Context, script: Script) -> None:
    if script.runs:
        return

    # Use Path() as something not str
    statement: Statement = Path() if script is None else script.script
    run_arg = RunArg(run_no=RunNo(0), statement=statement)
    context.run_arg = run_arg

    await context.hook.ahook.on_initialize_run(context=context)


async def _handle_run(context: spec.Context, run: Run) -> None:
    script = run.script

    # Use Path() as something not str
    statement: Statement = Path() if script is None else script.script
    run_arg = RunArg(run_no=RunNo(run.run_no), statement=statement)
    context.run_arg = run_arg

    await context.hook.ahook.on_initialize_run(context=context)

    run_started_at = run.started_at
    if run_started_at is None:
        return

    on_start_run = OnStartRun(
        started_at=run_started_at.replace(tzinfo=timezone.utc),
        run_no=RunNo(run.run_no),
        statement=statement,
    )

    # ic(run_started_at)
    # ic(run.started_at == run_started_at.replace(tzinfo=None))

    await context.hook.ahook.on_start_run(context=context, event=on_start_run)
    run.state = 'running'

    for trace in run.traces:
        await _handle_trace(context=context, trace=trace)

    for stdout in run.stdouts:
        await _handle_stdout(context=context, stdout=stdout)

    run_ended_at = run.ended_at
    if run_ended_at is None:
        run.exception = None
        return

    raised = run.exception = run.exception or ''

    on_end_run = OnEndRun(
        ended_at=run_ended_at.replace(tzinfo=timezone.utc),
        run_no=RunNo(run.run_no),
        returned=json.dumps(None),
        raised=raised,
    )

    await context.hook.ahook.on_end_run(context=context, event=on_end_run)
    run.state = 'finished'


async def _handle_trace(context: spec.Context, trace: Trace) -> None:
    on_start_trace = OnStartTrace(
        run_no=RunNo(trace.run.run_no),
        trace_no=TraceNo(trace.trace_no),
        thread_no=ThreadNo(trace.thread_no),
        task_no=None if trace.task_no is None else TaskNo(trace.task_no),
        started_at=trace.started_at,
    )
    await context.hook.ahook.on_start_trace(context=context, event=on_start_trace)
    trace.state = 'running'

    for trace_call in trace.trace_calls:
        await _handle_trace_call(context=context, trace_call=trace_call)

    trace_ended_at = trace.ended_at
    if trace_ended_at is None:
        return
    on_end_trace = OnEndTrace(
        run_no=RunNo(trace.run.run_no),
        trace_no=TraceNo(trace.trace_no),
        ended_at=trace_ended_at,
    )
    await context.hook.ahook.on_end_trace(context=context, event=on_end_trace)
    trace.state = 'finished'


async def _handle_trace_call(context: spec.Context, trace_call: TraceCall) -> None:
    started_at = trace_call.started_at
    file_name = trace_call.file_name = trace_call.file_name or ''
    line_no = trace_call.line_no = trace_call.line_no or 0
    on_start_trace_call = OnStartTraceCall(
        started_at=started_at,
        run_no=RunNo(trace_call.run.run_no),
        trace_no=TraceNo(trace_call.trace.trace_no),
        trace_call_no=TraceCallNo(trace_call.trace_call_no),
        file_name=file_name,
        line_no=line_no,
        frame_object_id=0,
        event=trace_call.event,
    )
    await context.hook.ahook.on_start_trace_call(
        context=context, event=on_start_trace_call
    )

    for prompt in trace_call.prompts:
        await _handle_prompt(context=context, prompt=prompt)

    if (ended_at := trace_call.ended_at) is None:
        return

    on_end_trace_call = OnEndTraceCall(
        ended_at=ended_at,
        run_no=RunNo(trace_call.run.run_no),
        trace_no=TraceNo(trace_call.trace.trace_no),
        trace_call_no=TraceCallNo(trace_call.trace_call_no),
    )
    await context.hook.ahook.on_end_trace_call(context=context, event=on_end_trace_call)


async def _handle_prompt(context: spec.Context, prompt: Prompt) -> None:
    started_at = prompt.started_at
    file_name = prompt.trace_call.file_name or ''
    line_no = prompt.trace_call.line_no or 0
    stdout = prompt.stdout = prompt.stdout or ''
    on_start_prompt = OnStartPrompt(
        started_at=started_at,
        run_no=RunNo(prompt.run.run_no),
        trace_no=TraceNo(prompt.trace.trace_no),
        trace_call_no=TraceCallNo(prompt.trace_call.trace_call_no),
        prompt_no=PromptNo(prompt.prompt_no),
        prompt_text=stdout,
        file_name=file_name,
        line_no=line_no,
        frame_object_id=0,
        event=prompt.trace_call.event,
    )
    await context.hook.ahook.on_start_prompt(context=context, event=on_start_prompt)
    prompt.open = True

    if (ended_at := prompt.ended_at) is None:
        prompt.command = None
        return
    command = prompt.command = prompt.command or ''

    on_end_prompt = OnEndPrompt(
        ended_at=ended_at,
        run_no=RunNo(prompt.run.run_no),
        trace_no=TraceNo(prompt.trace.trace_no),
        trace_call_no=TraceCallNo(prompt.trace_call.trace_call_no),
        prompt_no=PromptNo(prompt.prompt_no),
        command=command,
    )
    await context.hook.ahook.on_end_prompt(context=context, event=on_end_prompt)
    prompt.open = False


async def _handle_stdout(context: spec.Context, stdout: Stdout) -> None:
    if (written_at := stdout.written_at) is None:
        return
    text = stdout.text = stdout.text or ''

    on_write_stdout = OnWriteStdout(
        written_at=written_at,
        run_no=RunNo(stdout.run.run_no),
        trace_no=TraceNo(stdout.trace.trace_no),
        text=text,
    )
    await context.hook.ahook.on_write_stdout(context=context, event=on_write_stdout)
