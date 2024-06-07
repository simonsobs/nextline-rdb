from pathlib import Path

from graphql import parse, print_ast


def read_gql(path: Path | str) -> str:
    '''Load a GraphQL query from a file while checking its syntax.'''

    text = Path(path).read_text()
    parsed = parse(text)
    reformatted = print_ast(parsed)
    return reformatted


pwd = Path(__file__).resolve().parent

sub = pwd / 'queries'
QUERY_RDB_CONNECTIONS = read_gql(sub / 'RDBConnections.gql')
QUERY_RDB_RUNS = read_gql(sub / 'RDBRuns.gql')
QUERY_RDB_RUN = read_gql(sub / 'RDBRun.gql')

sub = pwd / 'mutations'
MUTATE_RDB_DELETE_RUNS = read_gql(sub / 'RDBDeleteRuns.gql')


# sub = pwd / 'subscriptions'
