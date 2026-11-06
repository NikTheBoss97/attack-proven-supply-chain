<!-- Author: Nicola Antonello -->

# ADR-0009: The toolbox's contents and quality gates

- Status: accepted
- Date: 2026-11-06

## Context

ADR-0008 chose one pinned toolbox image, run on the owner's machine and in CI alike,
and left open what goes in it. Phase 1 needs tools to build images, drive a `kind`
cluster, run the service's tests and check every change before it merges. Every tool
in the image runs next to the Docker socket, so each one has to be pinned to exact
bytes, and each one is something to keep up to date. The checks also have to become
required on `main` without blocking the pull requests that create them.

## Options

What the toolbox holds:

| Option | Why not |
|---|---|
| **Only what Phase 1 runs** | Chosen. The docker CLI with buildx, kind, kubectl, Python 3.14 with pytest, httpx and pip-tools, and the gate tools gitleaks, actionlint, zizmor, hadolint, shellcheck, kubeconform and ruff. Each later phase adds its own. |
| Every candidate tool now: Trivy, Syft, Cosign, Checkov, Terraform and Kyverno | No attack uses them yet, so they would change no result, and each one needs updates. |

The Python gate:

| Option | Why not |
|---|---|
| **pytest, `ruff check` and `ruff format --check`, with ruff's default rules** | Chosen. Choosing a SAST tool is Phase 2's decision, so no security rules are added on top of the defaults. |
| pytest alone | Nothing catches unused code or style drift. |
| A type checker on top | More setup than a few hundred lines of service need. |

How tool downloads are verified:

| Option | Why not |
|---|---|
| **Every input pinned to bytes named in the repository** | Chosen. The base is `python:3.14-trixie` by digest, which already includes git, so nothing comes from apt. A tool whose project publishes a SHA-256 for its release is fetched with `ADD --checksum`, with that value written in the Dockerfile: kind, kubectl, gitleaks, actionlint, kubeconform, hadolint and buildx. A tool whose project publishes none is copied from its official image by digest: shellcheck and the docker CLI. Python tools come from a hash-locked requirements file. The image is built for linux/amd64 only. |
| Downloading the checksum file at build time | It catches a corrupted download but not a replaced release, since both files come from the same place. |
| The slim base with `apt-get install git` | The package can change under a pinned base. |

How CI gets the toolbox:

| Option | Why not |
|---|---|
| **Each job builds it from `tools/Dockerfile`** | Chosen. There is no registry before Phase 2. |
| Pushing it to GitHub's container registry | It needs `packages: write`, and makes Phase 2's registry decision early. |

Which checks `main` requires:

| Option | Why not |
|---|---|
| **None at first, then each job once it exists** | Chosen. `gates` becomes required when the pull request that adds it merges, and `attacks` when the pull request that adds it merges. Each is tied to the GitHub Actions app, so a status posted by any other app or token cannot satisfy it. |
| Both jobs required from the start | No pull request could merge before both jobs existed. |

## Decision

- The toolbox holds only the tools Phase 1 runs, listed above. A later phase adds a
  tool together with the attack that needs it.
- `tools/run.sh gates` runs the gates in order and stops at the first failure:
  gitleaks on the history and on the staged changes, actionlint, zizmor in offline
  mode, hadolint, shellcheck, then `ruff check` and `ruff format --check`. Later work
  appends its own checks, such as the database and service tests.
- Every download is pinned as described above, and the build fails if any byte
  differs.
- Each CI job builds the toolbox itself.
- The ruleset starts with no required checks. Each job becomes required once it
  exists, as a check that must come from the GitHub Actions app (`integration_id`
  15368).

## Consequences

- The toolbox runs as root, because it holds the Docker socket, which already amounts
  to root on the host (ADR-0008).
- It is built for linux/amd64 only, and `tools/run.sh` passes `--platform linux/amd64`.
  Apple Silicon runs it emulated, which is untested.
- A pinned value proves the bytes are the ones pinned, not that the release was good.
  It moves trust to the moment of pinning. `ADD --checksum` was tried on 2026-11-06
  with one wrong digit, and the build stopped with `digest mismatch`.
- kubeconform downloads its schemas at run time, from a GitHub repository. Offline, it
  fails closed: tried on 2026-11-06 with networking off, it reported an error and
  exited 1.
- zizmor runs offline, so no token reaches the toolbox, and its audits that need
  GitHub's API do not run.
- Ruff's default rule set is large. In ruff 0.17.4 it has about 400 rules, including
  three of flake8-bandit's security rules (S102, S110 and S112). They stay on as part
  of the defaults, but ruff is not claimed as a security control, because no attack
  tests it.
- Every CI job spends time building the toolbox. Phase 1 measures how long.
- Versions move by hand until Phase 2.
- A check tied to one app has to be updated in the ruleset if CI moves elsewhere.

## References

- Docker documentation, [Dockerfile reference](https://docs.docker.com/reference/dockerfile/#add---checksum) (`ADD --checksum`).
- pip documentation, [Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/).
- GitHub Docs, [REST API endpoints for rules](https://docs.github.com/en/rest/repos/rules) (`integration_id`).
- zizmor documentation, [Usage](https://docs.zizmor.sh/usage/) (operating modes).
- kubeconform, [README](https://github.com/yannh/kubeconform).
- Ruff documentation, [Rules](https://docs.astral.sh/ruff/rules/).
