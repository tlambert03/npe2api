import os
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from .core import github_org_repo

PluginName = str

query = gql(
    """
query getRepository($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 1) {
            nodes {
              message
              committedDate
              authoredDate
              author {
                name
                user {
                  login
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
)


headers = {}
if GITHUB_API_TOKEN := os.environ.get("GITHUB_API_TOKEN"):
    headers["Authorization"] = f"bearer {GITHUB_API_TOKEN}"

transport = RequestsHTTPTransport("https://api.github.com/graphql", headers)
gql_client = Client(transport=transport, fetch_schema_from_transport=False)


def github_graphql(name: PluginName) -> dict:
    """Return github graphql data."""

    if not (result := github_org_repo(name)):
        raise ValueError(f"No github repo for {name}")

    owner, name = result
    variables = {"owner": owner, "name": name}
    return gql_client.execute(query, variables)["repository"]
