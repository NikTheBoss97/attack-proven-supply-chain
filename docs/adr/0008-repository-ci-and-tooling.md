<!-- Author: Nicola Antonello -->

# ADR-0008: The repository, CI and tooling

- Status: accepted
- Date: 2026-11-05

## Context

Development needs a public home, a protected main branch, a CI layout and a way to
install a long list of command-line tools at pinned versions. The owner's machine
runs Windows, CI runs on Linux, and anyone else may use anything. The project's
rules already require pull requests, pinned actions, read-only tokens and tools with
verified checksums.

## Options

The repository's name:

| Option | Why not |
|---|---|
| **`attack-proven-supply-chain`** | Chosen. It says what the project is when someone sees it in a list. Keywords such as `devsecops` go in the repository's topics. |
| `supply-chain-gauntlet` | It is more memorable, but less literal. |
| `devsecops-platform` | It is generic, and says nothing about what makes the project different. |

Visibility:

| Option | Why not |
|---|---|
| **Public** | Chosen. Reviewers need to see it. Standard GitHub-hosted runners are free there, with 4 CPUs and 16 GB of RAM. |
| Private | Reviewers could not see it, and runners have 2 CPUs and 8 GB of RAM. |

The license:

| Option | Why not |
|---|---|
| **Apache-2.0** | Chosen. It is the license of Kyverno, Cosign, Trivy, Argo CD and kind. |
| MIT | It is shorter, but it has no explicit patent grant. |

Pull request approvals on `main`:

| Option | Why not |
|---|---|
| **A pull request with zero approvals** | Chosen. It enforces that every change lands through a pull request, and the required checks do the gating. |
| A required approval | There is one maintainer, and an author cannot approve their own pull request. |

How tools get installed:

| Option | Why not |
|---|---|
| **One pinned toolbox image** | Chosen. `tools/Dockerfile` installs every command-line tool at a pinned version with a verified checksum, and the owner's machine and CI run the same image. Docker is the only prerequisite, so anyone on any OS can run one command. |
| An install script on the host | It needs no Docker socket mount, but it needs checksums per OS and installs things on the reader's machine. On the owner's, that means WSL. |
| A tool manager such as mise | One file lists all the versions, but it is one more tool to trust and to install first. Its checksum support was not checked. |

How Python dependencies are locked:

| Option | Why not |
|---|---|
| **`pip-compile --generate-hashes`, installed with `--require-hashes --only-binary :all:`** | Chosen. It uses pip's own controls, which ADR-0003 relies on. |
| `pip lock` | Its documentation marks it experimental, and its lock file is only guaranteed for the current Python version and platform. |
| `uv` | Its default index strategy is designed to prevent dependency confusion. That is good in production, but the attack ADR-0003 chose Python for would not work against it by default. |

When CI runs:

| Option | Why not |
|---|---|
| **On every pull request and every push to `main`, with no path filters** | Chosen. Even docs-only pull requests run everything, at no cost on a public repository. |
| Path filters that skip docs-only changes | GitHub's documentation says a required check skipped by a filter stays pending and blocks the merge. |

## Decision

- The repository is `attack-proven-supply-chain`, public, under Apache-2.0. Creating
  it is the first development step.
- The first commit goes straight to `main`, before the ruleset exists. Everything
  after it goes through pull requests.
- A ruleset with no bypass protects `main`: a pull request with zero approvals, up-to-date
  required checks, linear history, no force pushes and no deletions. Merges are rebase
  only, and merged branches are deleted automatically.
- `tools/Dockerfile` builds the toolbox image, and one wrapper script runs it on the
  owner's machine and in CI.
- `ci.yml` has two required jobs, `gates` and `attacks`. Later phases add their own
  workflows.
- Python dependencies are locked with `pip-compile --generate-hashes` and installed with
  `--require-hashes --only-binary :all:`. They are not claimed as controls until their
  attack exists.

## Consequences

- With zero approvals, the required checks are the only gate on a merge. No second
  person reviews a change.
- kind needs the Docker socket mounted in the toolbox, which gives the container full
  control of the host's Docker. Docker's documentation says only trusted users should
  have that, so running the toolbox means trusting this repository's code.
- A kind maintainer says a container must also join kind's Docker network to reach the
  cluster. That has not been tried here on Windows, so it is the first thing Phase 1
  tests. If it fails, the fallback is the install script in WSL, under a new record.
- Runners have 14 GB of disk, which may be tight once images pile up. Phase 1 measures
  it.
- GitHub's table lists `pip-compile`, Docker and Actions for version updates. Its
  security column is drawn as icons, and reading it gave conflicting results. So the
  rule that security updates skip the cooldown is unconfirmed for Python until it is
  seen on the real repository.
- As far as this record knows, Dependabot does not update tools downloaded with `curl`
  in a Dockerfile, so the toolbox's versions move by hand. That is not confirmed.

## References

- GitHub Docs, [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets), [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks), [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) and [Dependabot supported ecosystems](https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories).
- Docker documentation, [Docker Engine security](https://docs.docker.com/engine/security/).
- kind, [Access kind cluster from a container outside of cluster](https://github.com/kubernetes-sigs/kind/issues/2148) (issue #2148).
- pip-tools documentation, [pip-tools](https://pip-tools.pypa.io/en/stable/).
- pip documentation, [`pip lock`](https://pip.pypa.io/en/stable/cli/pip_lock/).
- uv documentation, [Package indexes](https://docs.astral.sh/uv/concepts/indexes/).

## Amendments

- 2026-11-08: what Phase 1 measured. The toolbox drives a `kind` cluster from Git
  Bash and from WSL, on Windows 11 with Docker Desktop, once its container joins
  kind's Docker network, so the install script in WSL was not needed
  ([ADR-0010](0010-how-tests-reach-the-service.md)). Disk was not tight: the
  `ubuntu-24.04` runner's root filesystem had 145 GB, 86 GB of it free, and a run
  of the attack suite used about 3 GB, so the 14 GB this record assumed did not
  hold for the disk the job actually got. Each CI job spends about 35 seconds
  building the toolbox, whose image is 1.5 GB.
