"""Read-only GitHub App access for repository review."""

import base64
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

from .models import Commit
from .repository import RepositoryError, snapshot_from_files

API = "https://api.github.com"


class GitHubApp:
    def __init__(self, auth="app"):
        self.auth = auth
        self.app_id = os.getenv("SPEC_REVIEW_GITHUB_APP_ID", "")
        self.private_key = os.getenv("SPEC_REVIEW_GITHUB_PRIVATE_KEY", "").replace(
            "\\n", "\n"
        )
        self._tokens = {}

    @property
    def configured(self):
        return (self.auth == "gh" and bool(self._gh_token())) or bool(
            self.app_id and self.private_key
        )

    def _gh_token(self):
        if not hasattr(self, "_cli_token"):
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

    def _jwt(self):
        if not self.configured:
            raise RepositoryError(
                "GitHub App is not configured (set SPEC_REVIEW_GITHUB_APP_ID and SPEC_REVIEW_GITHUB_PRIVATE_KEY)"
            )
        now = int(time.time())

        def enc(value):
            return base64.urlsafe_b64encode(value).rstrip(b"=").decode()

        head = enc(
            json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode()
        )
        body = enc(
            json.dumps(
                {"iat": now - 30, "exp": now + 540, "iss": self.app_id},
                separators=(",", ":"),
            ).encode()
        )
        message = f"{head}.{body}".encode()
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", prefix="spec-review-github-"
            ) as key_file:
                key_file.write(self.private_key)
                key_file.flush()
                signed = subprocess.run(
                    ["openssl", "dgst", "-sha256", "-sign", key_file.name],
                    input=message,
                    capture_output=True,
                    check=True,
                    timeout=10,
                )
                signature = signed.stdout
        except (OSError, subprocess.SubprocessError) as exc:
            raise RepositoryError(
                f"Unable to sign GitHub App JWT (OpenSSL required): {exc}"
            ) from exc
        return f"{head}.{body}.{enc(signature)}"

    def _request(self, path, token=None, method="GET", payload=None):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "spec-review",
        }
        if payload is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(
            API + path, data=data, headers=headers, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RepositoryError(f"GitHub API {exc.code}: {detail[:500]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RepositoryError(f"GitHub request failed: {exc}") from exc

    def installations(self):
        if self.auth == "gh":
            user = self._request("/user", self._gh_token())
            return [
                {
                    "id": "gh",
                    "account": {"login": user["login"], "type": "GitHub CLI"},
                }
            ]
        return self._request("/app/installations", self._jwt())

    def token(self, installation_id):
        if self.auth == "gh":
            token = self._gh_token()
            if not token:
                raise RepositoryError(
                    "GitHub CLI is not authenticated; run `gh auth login`"
                )
            return token
        cached = self._tokens.get(str(installation_id))
        if cached and cached[1] > time.time() + 60:
            return cached[0]
        result = self._request(
            f"/app/installations/{urllib.parse.quote(str(installation_id))}/access_tokens",
            self._jwt(),
            "POST",
            {},
        )
        self._tokens[str(installation_id)] = (
            result["token"],
            datetime.fromisoformat(
                result["expires_at"].replace("Z", "+00:00")
            ).timestamp(),
        )
        return result["token"]

    def get(self, installation_id, path):
        return self._request(path, self.token(installation_id))

    def repos(self, installation_id):
        result, page = [], 1
        while True:
            path = (
                f"/user/repos?affiliation=owner%2Ccollaborator%2Corganization_member&sort=full_name&per_page=100&page={page}"
                if self.auth == "gh"
                else f"/installation/repositories?per_page=100&page={page}"
            )
            data = self.get(installation_id, path)
            rows = data if isinstance(data, list) else data.get("repositories", [])
            result.extend(rows)
            if not rows or (
                not isinstance(data, list) and len(result) >= data.get("total_count", 0)
            ):
                return result
            page += 1

    def branches(self, installation_id, owner, repo):
        return self.get(
            installation_id,
            f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/branches?per_page=100",
        )

    def pull_requests(self, installation_id, owner, repo):
        return self.get(
            installation_id,
            f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/pulls?state=all&per_page=100",
        )

    def commits(self, installation_id, owner, repo, ref=""):
        query = urllib.parse.urlencode(
            {"per_page": 100, **({"sha": ref} if ref else {})}
        )
        rows = self.get(
            installation_id,
            f"/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/commits?{query}",
        )
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

    def snapshot(self, installation_id, owner, repo, revision, spec_dir="spec"):
        owner, repo = urllib.parse.quote(owner), urllib.parse.quote(repo)
        path = f"/repos/{owner}/{repo}/git/trees/{urllib.parse.quote(revision, safe='')}?recursive=1"
        tree = self.get(installation_id, path)
        if tree.get("truncated"):
            raise RepositoryError("GitHub tree is too large to review in one request")
        files = []
        for entry in tree.get("tree", []):
            name = entry["path"]
            if entry["type"] != "blob" or not (
                name.startswith(f"{spec_dir}/artifacts/")
                or name.startswith(f"{spec_dir}/generated/")
            ):
                continue
            suffix = name.rsplit(".", 1)[-1].lower() if "." in name else ""
            if not (
                name.startswith(f"{spec_dir}/artifacts/")
                and suffix in {"yaml", "yml"}
                or name.startswith(f"{spec_dir}/generated/")
                and suffix == "md"
            ):
                continue
            blob = self.get(
                installation_id, f"/repos/{owner}/{repo}/git/blobs/{entry['sha']}"
            )
            try:
                value = base64.b64decode(blob["content"]).decode("utf-8")
            except (ValueError, UnicodeError):
                value = "\0READ ERROR: GitHub blob is not UTF-8 text"
            files.append((name, value))
        return snapshot_from_files(revision, files, spec_dir)
