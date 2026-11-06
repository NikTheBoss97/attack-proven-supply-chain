<!-- Author: Nicola Antonello -->

# Engineering practice

Continuous integration and recording decisions. Part of the [reading list](README.md).

## Continuous integration

- GitHub, [Available rules for rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) (GitHub Docs). What each rule on a protected branch enforces: pull requests, status checks, linear history, force pushes and deletions.
- GitHub, [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks) (GitHub Docs). Why a required check skipped by a path filter stays pending and blocks the merge.
- Docker, [Docker Engine security](https://docs.docker.com/engine/security/) (Docker documentation). Why control of the Docker daemon amounts to control of the host.
- GitHub, [REST API endpoints for rules](https://docs.github.com/en/rest/repos/rules) (GitHub Docs). The ruleset API, including `integration_id`, which ties a required status check to one GitHub App so that no other token can satisfy it.
- zizmor, [Usage](https://docs.zizmor.sh/usage/) (zizmor documentation). How it audits workflows offline or online, and what each mode leaves out.
- Ruff, [Rules](https://docs.astral.sh/ruff/rules/) (Ruff documentation). Every lint rule, which ones are on by default, and the security rules among them.

## Recording decisions

- ★ Michael Nygard, [Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (Cognitect, 2011). The original ADR format: a title, context, decision, status and consequences, with a reversed decision kept and marked superseded.
- Georg Buchgeher et al., [Using Architecture Decision Records in Open Source Projects—An MSR Study on GitHub](https://doi.org/10.1109/ACCESS.2023.3287654) (IEEE Access, 2023). ADR adoption on GitHub is low but rising, about half of the repositories with ADRs hold only one to five, and most follow Nygard's template.
- J. Tyree, A. Akerman, [Architecture Decisions: Demystifying Architecture](https://doi.org/10.1109/MS.2005.27) (IEEE Software, 2005). An earlier template for documenting a decision with its options and reasoning.
- A. Jansen, J. Bosch, [Software Architecture as a Set of Architectural Design Decisions](https://doi.org/10.1109/WICSA.2005.61) (WICSA, 2005). The idea that an architecture is the decisions behind it, and that their reasoning is lost unless recorded.
