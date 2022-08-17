"""This file includes python functions for accessing the public data.

Currently, it's not used anywhere, just for local interactive convenience.
"""

from __future__ import annotations
import os
import json
import re
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Optional, Tuple

if TYPE_CHECKING:
    from typing import TypedDict

    from npe2 import PluginManifest

    Version = str
    PluginName = str

    class Plugins(TypedDict):
        active: dict[PluginName, list[Version]]
        withdrawn: dict[PluginName, list[Version]]
        deleted: dict[PluginName, list[Version]]


PUBLIC = Path(__file__).parent.parent.parent / "public"
GITHUB_RE = re.compile(r"https://github\.com/([^/]+)/([^/#@]+)")


def plugins() -> Plugins:
    """Return a dict of active, withdrawn, and deleted plugins."""
    return json.loads((PUBLIC / "classifiers.json").read_text())


def active_plugins() -> list[PluginName]:
    """Return a list of active plugins."""
    return plugins()["active"]


def github_org_repo(name: PluginName) -> Optional[Tuple[str, str]]:
    """Return the link to the public repo."""
    try:
        info: dict = pypi_info(name)["info"]
    except KeyError:
        return None

    links = chain(
        [info.get("home_page"), info.get("package_url"), info.get("project_url")],
        (info.get("project_urls") or {}).values(),
    )
    for link in links:
        if match := GITHUB_RE.match(link):
            org, repo = match.groups()
            if repo.endswith(".git"):
                repo = repo[:-4]
            return org, repo


GITHUB_ENDPOINTS = Literal[
    "assignees",
    "branches",
    "commits",
    "commits/HEAD",
    "contents",
    "contributors",
    "forks",
    "events",
    "issues",
    "languages",
    "license",
    "pulls",
    "readme",
    "releases",
    "stargazers",
    "subscribers",
    "tags",
    "teams",
]


def github_info(name: PluginName, endpoint: str = "") -> dict:
    """Fetch information from github api."""
    import requests

    if not (github_info := github_org_repo(name)):
        raise ValueError(f"No github repo for {name}")

    endpoint = f"/{endpoint}" if endpoint else ""
    url = "https://api.github.com/repos/{}/{}{}".format(*github_info, endpoint)
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_API_TOKEN := os.environ.get("GITHUB_API_TOKEN"):
        headers["Authorization"] = f"token {GITHUB_API_TOKEN}"
    return requests.get(url, headers=headers).json()


def manifest(name: PluginName) -> PluginManifest:
    """Return the npe2 manifest for a plugin."""
    from npe2 import PluginManifest

    if not (file := PUBLIC / "manifest" / f"{name}.json").exists():
        raise FileNotFoundError(f"No manifest at {file}")
    return PluginManifest.from_file(file)


def pypi_info(name: PluginName) -> dict:
    """Return the PyPI info for a plugin."""
    if not (file := PUBLIC / "pypi" / f"{name}.json").exists():
        raise FileNotFoundError(f"No pypi info at {file}")
    return json.loads(file.read_text())


def conda_info(name: PluginName) -> dict:
    """Return conda info for a plugin."""
    if not (file := PUBLIC / "conda" / f"{name}.json").exists():
        raise FileNotFoundError(f"No conda info at {file}")
    return json.loads(file.read_text())
