<!-- Author: Nicola Antonello -->

# Software supply chain

How dependencies and build tools get attacked, and what stops it. Part of the [reading list](README.md).

## Package managers

- ★ pip, [Secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) (pip documentation). Hash-checking mode, why hashes supplied by the index do not guard against tampering, and why to disallow source distributions.
- uv, [Package indexes](https://docs.astral.sh/uv/concepts/indexes/) (uv documentation). How a default that stops at the first index containing a package prevents dependency confusion, and why best-match resolution across indexes exposes it.
- pip-tools, [pip-tools](https://pip-tools.pypa.io/en/stable/) (pip-tools documentation). Compiling a lock file, and `--generate-hashes` for pip's hash-checking mode.
- Filippo Valsorda, [How Go Mitigates Supply Chain Attacks](https://go.dev/blog/supply-chain) (The Go Blog, 2022). A package manager designed so that neither fetching nor building a dependency runs its code: the comparison point for what pip does by default.
- Ruian Duan et al., [Towards Measuring Supply Chain Attacks on Package Managers for Interpreted Languages](https://doi.org/10.14722/ndss.2021.23055) (NDSS, 2021). Compares how registries for interpreted languages handle security, and finds new malicious packages using metadata, static and dynamic analysis.

## Build inputs

- Docker, [Dockerfile reference: `ADD --checksum`](https://docs.docker.com/reference/dockerfile/#add---checksum) (Docker documentation). Verifying a downloaded file against a checksum written in the Dockerfile, so the build fails if a single byte differs.

## Images and admission

- Google, [Binary Authorization for Borg](https://docs.cloud.google.com/docs/security/binary-authorization-for-borg) (Google Cloud documentation). The clearest statement of the idea: Borg checks a job against its policy and starts it only if the job satisfies it, acting as an admission controller.
- J. H. Saltzer, M. D. Schroeder, [The Protection of Information in Computer Systems](https://web.mit.edu/Saltzer/www/publications/protection/) (Proceedings of the IEEE, 1975). The origin of fail-safe defaults: what nobody listed stays denied rather than open.
