# Specification kit setup and updates

The kit is a committed copy of specification instructions, references, and skills.
The reviewer is installed separately; a spec-review submodule is optional. Use an
installed `spec-review` command, or invoke it from a checkout with
`uv run --project /path/to/spec-review spec-review`.

## Set up a project

For a new project folder:

```sh
spec-review init --repo /path/to/new-project --dry-run
spec-review init --repo /path/to/new-project
```

For an existing repository, run `spec-review init --repo .` and inspect the diff.
The command preserves existing root instructions, appends a marked instruction
block, and installs docs under `docs/spec-review/`, workflows under `skills/`, and
an empty specification scaffold under `spec/`. It creates missing directories but
does not initialize Git, install dependencies, or import application documentation.
Conflicting existing kit files stop initialization before writes. Reconcile them
explicitly before retrying. Repeated initialization does not upgrade an installed kit.

Use `--spec-dir planning/spec` for a different relative specification directory.
Pass the same directory to subsequent review, validation, and update commands.
Instructions are referenced by file path; no global or agent-specific skill
installation is required. Start authoring through `skills/spec-authoring/SKILL.md`.
The first authoring instructions link to the authoritative
[canonical storage layout and type-folder mapping](artifact-authoring.md#canonical-storage-layout).
Create new artifacts at `spec/artifacts/<type-folder>/<id>.yaml`, one YAML mapping
per file with the exact artifact `id` as its filename stem, for example
`spec/artifacts/requirements/REQ-001.yaml` or
`spec/artifacts/ui-design/UI-001.yaml`. Select folders by current `type`, not ID
prefix. Keep `spec/sources/`, `spec/views/`, and `spec/mockups/` separate from
canonical artifacts. The scaffold starts empty; create type folders as needed.
Existing flat or differently nested artifacts and custom types remain readable;
initialization and updates do not migrate or delete them to impose the convention.

Existing documents can be adopted with provenance; code observations alone do not
establish new user requirements.

```sh
spec-review validate --repo .
spec-review --repo .
```

## Update the kit

The installed tool supplies the target kit. Install the desired tool version
separately, then preview and apply its kit:

```sh
spec-review update --repo . --dry-run
spec-review update --repo .
```

`docs/spec-review/.kit/state.json` stores the kit version, upstream file baselines,
and any pending update. Commit this metadata with kit changes. Project artifacts,
provenance, and views are starter content and are never replaced by upgrades.
Only the marked root `AGENTS.md` block belongs to the kit.

Updates replace unmodified upstream files and retain local edits when upstream
has not changed. When both sides changed, the command retains the local file,
reports a conflict, and exits with status 1. The pending metadata holds each
conflict's old (`base`), current (`local`), and new (`incoming`) text; null denotes
absence. Use `skills/spec-kit-update/SKILL.md` to integrate changes while preserving
project customizations. A local deletion can intentionally remain a deletion.

For a requested cleanup of superseded artifacts and stale references, use
`skills/spec-supersession-cleanup/SKILL.md`.

After reviewing and resolving every conflict, explicitly acknowledge each path:

```sh
spec-review update --repo . --accept-merge \
  --resolved skills/spec-authoring/SKILL.md
```

Repeat `--resolved` for every reported conflict. This records the new upstream
baseline without overwriting the chosen local result. It verifies the pending
target kit and rejects unresolved merge markers. Keep the original target tool
available until a pending update is finished. Interrupted updates can be resumed:
a journal is saved before file writes and each write uses atomic replacement.
External changes to a file awaiting journal replay stop the update for inspection.

Dry runs write nothing. Review, validation, terminal navigation, and browser
navigation remain read-only. Initialization and updates are explicit write commands.
