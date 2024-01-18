from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'queries'
QUERY_RDB_CONNECTIONS = (sub / 'RDBConnections.gql').read_text()
QUERY_RDB_RUNS = (sub / 'RDBRuns.gql').read_text()
QUERY_RDB_RUN = (sub / 'RDBRun.gql').read_text()

sub = pwd / 'mutations'
MUTATE_RDB_DELETE_RUNS = (sub / 'RDBDeleteRuns.gql').read_text()


# sub = pwd / 'subscriptions'
