from typing import Optional

from hypothesis import strategies as st

from .. import Model


@st.composite
def st_model_instance_list(
    draw: st.DrawFn,
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> list[Model]:
    '''A strategy for a list of `Model` instances.

    Instances of `Script` and `Run` models are explicitly generated.  Instances of other
    models will be generated as related models of `Script` and `Run` models.
    '''
    from .st_run import st_model_run_list
    from .st_script import st_model_script_list

    # Generate a list of `Script` models
    scripts = draw(st_model_script_list(min_size=min_size, max_size=max_size))

    # Adjust min_size and max_size
    size = len(scripts)
    min_size = max(0, min_size - size)
    max_size = max_size - size if max_size is not None else None

    # Generate a list of `Run` models
    runs = draw(
        st_model_run_list(
            generate_traces=True,
            min_size=min_size,
            max_size=max_size,
            scripts=scripts,
        )
    )

    ret: list[Model] = list(scripts) + list(runs)
    return ret
