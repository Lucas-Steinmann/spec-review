"""Opt-in, read-only integration checks against GitHub.com through gh."""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import pytest

pytestmark = pytest.mark.live_github


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOKEN_ENV_VARS = (
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "GH_ENTERPRISE_TOKEN",
    "GITHUB_ENTERPRISE_TOKEN",
)


@pytest.fixture(scope="module")
def live_github_environment(tmp_path_factory):
    if os.getenv("SPEC_REVIEW_LIVE_GITHUB") != "1":
        pytest.skip("set SPEC_REVIEW_LIVE_GITHUB=1 to enable live GitHub checks")

    config_value = os.getenv("SPEC_REVIEW_LIVE_GH_CONFIG_DIR")
    expected_login = os.getenv("SPEC_REVIEW_LIVE_GH_LOGIN")
    if not config_value or not expected_login:
        pytest.fail(
            "live GitHub checks require SPEC_REVIEW_LIVE_GH_CONFIG_DIR and "
            "SPEC_REVIEW_LIVE_GH_LOGIN"
        )

    config_dir = Path(config_value).expanduser().resolve()
    if not config_dir.is_dir():
        pytest.fail("SPEC_REVIEW_LIVE_GH_CONFIG_DIR must be an existing directory")

    env = os.environ.copy()
    for name in TOKEN_ENV_VARS:
        env.pop(name, None)
    env["GH_CONFIG_DIR"] = str(config_dir)
    env["GH_HOST"] = "github.com"

    status = subprocess.run(
        ["gh", "auth", "status", "--hostname", "github.com"],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if status.returncode:
        pytest.fail(
            "The isolated gh config is not authenticated to github.com. "
            "Run `GH_CONFIG_DIR=<path> gh auth login --hostname github.com` "
            "for the test account."
        )

    return env, expected_login


@pytest.fixture(scope="module")
def live_github_api(live_github_environment, tmp_path_factory):
    env, _ = live_github_environment
    server_dir = tmp_path_factory.mktemp("live-github-api")
    cache_dir = server_dir / "cache"
    cache_dir.mkdir()
    env["XDG_CACHE_HOME"] = str(cache_dir)

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "spec_review.cli",
            "--web",
            "--repo",
            str(server_dir),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    root_url = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            pytest.fail("the local WebUI process exited before it became ready")
        try:
            with urlopen(f"{root_url}/api/status", timeout=1) as response:
                if response.status == 200:
                    break
        except (OSError, URLError):
            time.sleep(0.1)
    else:
        process.terminate()
        process.wait(timeout=5)
        pytest.fail("the local WebUI did not become ready")

    def get_json(path, params=None):
        url = f"{root_url}{path}"
        if params:
            url += "?" + urlencode(params)
        try:
            with urlopen(url, timeout=90) as response:
                return json.loads(response.read())
        except HTTPError as exc:
            message = exc.read().decode(errors="replace")
            pytest.fail(f"{path} returned HTTP {exc.code}: {message}")

    try:
        yield get_json
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_live_github_account_and_repository_listing(live_github_api, live_github_environment):
    get_json = live_github_api
    _, expected_login = live_github_environment

    account = get_json("/api/gh/account")
    assert account["login"].casefold() == expected_login.casefold()

    repositories = get_json("/api/gh/repos")
    assert isinstance(repositories, list)
    assert all({"full_name", "default_branch", "private"} <= row.keys() for row in repositories)


def test_live_github_repository_read_routes(live_github_api, live_github_environment):
    get_json = live_github_api
    _, expected_login = live_github_environment
    full_name = os.getenv("SPEC_REVIEW_LIVE_GH_REPO")
    if not full_name:
        pytest.skip("set SPEC_REVIEW_LIVE_GH_REPO to an isolated test repository")
    parts = full_name.split("/")
    if len(parts) != 2 or not all(parts):
        pytest.fail("SPEC_REVIEW_LIVE_GH_REPO must be owner/repository")
    owner, repository = parts
    if owner.casefold() != expected_login.casefold():
        pytest.fail("SPEC_REVIEW_LIVE_GH_REPO must belong to the expected test account")
    query = {"owner": owner, "repo": repository}
    accessible_repositories = get_json("/api/gh/repos")
    assert any(
        row["full_name"].casefold() == full_name.casefold()
        for row in accessible_repositories
    ), "the configured fixture repository is not visible to the test account"

    branches = get_json("/api/gh/branches", query)
    pulls = get_json("/api/gh/pulls", query)
    commits = get_json("/api/gh/commits", query)
    overview = get_json("/api/gh/overview", query)
    assert isinstance(branches, list)
    assert isinstance(pulls, list)
    assert isinstance(commits, list) and commits
    assert isinstance(overview, list)

    revision = commits[0]["sha"]
    snapshot = get_json("/api/gh/snapshot", {**query, "ref": revision})
    assert snapshot["revision"].startswith(revision[:12])
    assert isinstance(snapshot["documents"], dict)

    comparison = get_json(
        "/api/gh/compare", {**query, "base": revision, "target": revision}
    )
    assert comparison["base"]["revision"] == snapshot["revision"]
    assert comparison["target"]["revision"] == snapshot["revision"]
    assert isinstance(comparison["changes"], dict)
