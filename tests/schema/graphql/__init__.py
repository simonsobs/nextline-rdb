from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'queries'
QUERY_HISTORY = (sub / 'History.gql').read_text()
QUERY_HISTORY_RUN = (sub / 'HistoryRun.gql').read_text()
QUERY_HISTORY_RUNS = (sub / 'HistoryRuns.gql').read_text()

sub = pwd / 'mutations'
MUTATE_RDB_DELETE_RUNS = (sub / 'RDBDeleteRuns.gql').read_text()


# sub = pwd / 'subscriptions'
