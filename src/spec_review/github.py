"""GitHub review through the authenticated gh CLI and a local Git mirror."""

import base64
import hashlib
import json
import os
import re
import subprocess
import urllib.parse
from pathlib import Path

from .models import Commit
from .repository import Repository, RepositoryError


class GitHubCLI:
    @property
    def configured(self):
        return bool(self._gh_token())

    def _gh_token(self):
        if not getattr(self, "_cli_token", ""):
            try:
                result = subprocess.run(
                    ["gh", "auth", "token"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                self._cli_token = result.stdout.strip()
            except (OSError, subprocess.SubprocessError):
                self._cli_token = ""
        return self._cli_token

    def token(self):
        token = self._gh_token()
        if not token:
            raise RepositoryError(
                "GitHub CLI is not authenticated; run `gh auth login`"
            )
        return token

    def _request(self, path):
        self.token()
        try:
            result = subprocess.run(
                ["gh", "api", path],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as exc:
            raise RepositoryError(
                f"GitHub CLI request failed: {exc.stderr.strip()[:500]}"
            ) from exc
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            raise RepositoryError(f"GitHub CLI request failed: {exc}") from exc

    def account(self):
        return self._request("/user")["login"]

    def repos(self):
        result, page = [], 1
        while True:
            rows = self._request(
                f"/user/repos?affiliation=owner%2Ccollaborator%2Corganization_member&sort=full_name&per_page=100&page={page}"
            )
            result.extend(rows)
            if len(rows) < 100:
                return result
            page += 1

    @staticmethod
    def _repo_path(owner, repo):
        if not all(re.fullmatch(r"[A-Za-z0-9_.-]+", part) for part in (owner, repo)):
            raise RepositoryError("Invalid GitHub repository name")
        return f"/repos/{owner}/{repo}"

    def branches(self, owner, repo):
        return self._request(f"{self._repo_path(owner, repo)}/branches?per_page=100")

    def pull_requests(self, owner, repo):
        return self._request(
            f"{self._repo_path(owner, repo)}/pulls?state=all&per_page=100"
        )

    def open_pull_requests(self, owner, repo):
        return self._request(
            f"{self._repo_path(owner, repo)}/pulls?state=open&per_page=100"
        )

    def check_runs(self, owner, repo, ref):
        return self._request(
            f"{self._repo_path(owner, repo)}/commits/{urllib.parse.quote(ref, safe='')}/check-runs?per_page=100"
        )

    def commits(self, owner, repo, ref=""):
        query = urllib.parse.urlencode(
            {"per_page": 100, **({"sha": ref} if ref else {})}
        )
        rows = self._request(f"{self._repo_path(owner, repo)}/commits?{query}")
        return [
            Commit(
                row["sha"],
                (
                    row["commit"].get("author") or row["commit"].get("committer") or {}
                ).get("date", "")[:10],
                row["commit"]["message"].splitlines()[0],
            )
            for row in rows
        ]

    def mirror_path(self, owner, repo):
        self._repo_path(owner, repo)
        cache_root = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
        identity = hashlib.sha256(f"{owner}/{repo}".encode()).hexdigest()[:24]
        return cache_root / "spec-review" / "github" / f"{identity}.git"

    def snapshot(self, owner, repo, revision, spec_dir="spec"):
        # Git's pack protocol transfers all needed objects in a small number of
        # requests. The former tree + one-blob-request-per-file approach made
        # opening large specifications take many seconds.
        self._repo_path(owner, repo)
        if (
            not re.fullmatch(
                r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}|[A-Za-z0-9_./-]+", revision
            )
            or revision.startswith("-")
            or ".." in revision
        ):
            raise RepositoryError("Invalid GitHub revision")
        mirror = self.mirror_path(owner, repo)
        mirror.parent.mkdir(parents=True, exist_ok=True)
        remote = f"https://github.com/{owner}/{repo}.git"
        complete_marker = mirror / "spec-review-complete-objects-v1"
        if not (mirror / "HEAD").exists():
            mirror.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(
                    ["git", "init", "--bare", str(mirror)],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
                subprocess.run(
                    ["git", "-C", str(mirror), "remote", "add", "origin", remote],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                raise RepositoryError(
                    f"Unable to initialize GitHub cache: {exc}"
                ) from exc
        # Older mirrors used a blobless filter. Force a complete fetch once
        # before trusting any commits already present in those mirrors.
        complete_cache = complete_marker.exists()
        cached = False
        if (
            len(revision) in (40, 64)
            and all(c in "0123456789abcdefABCDEF" for c in revision)
            and complete_cache
        ):
            try:
                Repository(mirror, spec_dir).resolve_commit(revision)
                cached = True
            except RepositoryError:
                pass
        if not cached:
            token = self.token()
            auth = base64.b64encode(f"x-access-token:{token}".encode()).decode()
            try:
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(mirror),
                        "-c",
                        f"http.{remote}.extraheader=AUTHORIZATION: basic {auth}",
                        "fetch",
                        "--refetch",
                        "--no-tags",
                        "origin",
                        revision,
                    ],
                    check=True,
                    capture_output=True,
                    timeout=60,
                )
            except subprocess.CalledProcessError as exc:
                detail = exc.stderr.decode(errors="replace").strip()
                raise RepositoryError(
                    f"Unable to fetch GitHub revision: {detail}"
                ) from exc
            except (OSError, subprocess.SubprocessError) as exc:
                raise RepositoryError(
                    f"Unable to fetch GitHub revision: {exc}"
                ) from exc
            complete_marker.touch()
        return Repository(mirror, spec_dir).load(revision)
