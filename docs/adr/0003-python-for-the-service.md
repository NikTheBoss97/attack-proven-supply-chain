<!-- Author: Nicola Antonello -->

# ADR-0003: Python for the service

- Status: accepted
- Date: 2026-11-05

## Context

ADR-0002 chose a small service and left its language open. The language decides
which dependency attacks can succeed at all. An attack proves a control only if it
succeeds with the control off, so a toolchain that already stops an attack leaves
the suite nothing to prove about it. The language also decides how much the
scanners can say about the code, and how long each run of the suite takes.

## Options

| Option | Why not |
|---|---|
| **Python** | Chosen. pip's documentation says its default behaviour involves "running arbitrary code from distributions", and warns that `--extra-index-url` allows dependency confusion, because it searches indexes with no priority. So both attacks can really succeed, and pip's own `--require-hashes` and `--only-binary :all:` are controls that can stop them. Semgrep Code lists 710+ rules for Python, the most of these options, and CodeQL supports it. |
| Go | The strongest alternative. `govulncheck` reports only the vulnerabilities the code actually calls, and Kyverno, Cosign, Trivy, Argo CD and Syft are written mainly in Go. But it is "an explicit security design goal" that "neither fetching nor building code will let that code execute", and a checksum database fixes each dependency's contents. The suite would have less to attack at the dependency level, and would partly be proving that Go's defaults work. Semgrep Code lists 80+ rules for it. |
| Rust | Cargo compiles and runs a package's `build.rs` just before building it, so a build-time attack could succeed. But each run of the suite would likely spend longer compiling (not measured), and Semgrep Code lists 40+ rules for it. |

## Decision

The service is written in Python. Four related choices stay open: the Python
version, the web framework, how dependencies are locked, and the language of the
attack harness.

## Consequences

- Dependency confusion and install-time code execution can be real attacks in the
  suite, always against a local registry.
- pip's protections are off by default, so turning them on becomes this project's
  job, and each one needs its attack.
- Reachability has to be shown by hand, with code search and tests. No equivalent of
  `govulncheck` is known to this record, but none was searched for.
- Images will likely be larger than a Go binary, with more base-image findings to
  triage (not measured).
- These facts come from each project's documentation, read on 2026-11-05. None has
  been tried here yet, so the first attack on each is also the first test of the
  claim.

## References

- pip documentation, [Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) and [`pip install`](https://pip.pypa.io/en/stable/cli/pip_install/) (`--extra-index-url`).
- Filippo Valsorda, [How Go Mitigates Supply Chain Attacks](https://go.dev/blog/supply-chain) (The Go Blog, 2022).
- Go documentation, [Go Vulnerability Management](https://go.dev/doc/security/vuln/) (`govulncheck`).
- The Cargo Book, [Build Scripts](https://doc.rust-lang.org/cargo/reference/build-scripts.html).
- Semgrep documentation, [Supported languages](https://docs.semgrep.dev/supported-languages).
- CodeQL, [Supported languages and frameworks](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/).
- Ruian Duan et al., [Towards Measuring Supply Chain Attacks on Package Managers for Interpreted Languages](https://doi.org/10.14722/ndss.2021.23055) (NDSS, 2021).
