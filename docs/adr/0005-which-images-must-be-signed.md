<!-- Author: Nicola Antonello -->

# ADR-0005: Which images must be signed

- Status: accepted
- Date: 2026-11-05

## Context

The project's image rule said that only images built by this repository's CI, signed
and carrying valid provenance, run in the cluster. That cannot be true as written:
the admission tool, the GitOps tool and the runtime tools are third-party images in
the same cluster. ADR-0004 added another, because PostgreSQL's image is not built
here either.

A digest is a hash of an image's exact contents. Pinning one fixes which bytes run,
but it says nothing about who built them or how.

## Options

Where the rule applies:

| Option | Why not |
|---|---|
| **Every namespace except a fixed list of the platform's own** | Chosen. A namespace nobody thought about is covered by default, so a forgotten one fails closed. |
| Only a listed set of workload namespaces | It is simpler to state, but a new namespace stays unprotected until someone remembers to add it. |
| Every namespace, with no exception | It cannot be met without rebuilding every platform tool here, which is work out of proportion to what it proves. |

How PostgreSQL's image fits:

| Option | Why not |
|---|---|
| **Rebuild it in this repository's CI from a pinned upstream digest** | Chosen. It goes through the same scanning, signing and provenance as the service, so the rule needs no exception. Deploying the upstream image directly must then be blocked, which gives the suite a ready-made attack. |
| Docker's hardened image, verified with Docker's key | Docker's page says its free tier includes a signature, SLSA Build L3 provenance and OpenVEX data, which is stronger evidence about upstream. But the policy would gain a second source of trust, and Docker's verification steps require logging in to two of its registries, so the cluster would probably need those credentials. |
| The upstream image, pinned by digest, as a listed exception | It is the least work, but it leaves a hole in the rule next to the workloads, with no signature or provenance check. |

## Decision

- The image rule applies to every namespace except the platform's own: `kube-system`
  and those of the platform tools, kept in one list.
- Platform tools are pinned by digest, and the threat model records them as an
  accepted risk.
- PostgreSQL's image is a short Dockerfile in this repository, built from a pinned
  upstream digest and signed like the service's image.

## Consequences

- The signature on the PostgreSQL image says this repository's CI built it from that
  digest. It does not say the upstream contents are good. The service's base image
  is trusted the same way.
- There are two images to keep current, each with digest updates and base-image
  findings to triage.
- This rule does not catch a compromised platform tool. What stops someone deploying
  into a platform namespace is access control, which needs its own threat and attack.
- A hardened image can still become the base under this rebuild. That is a later
  decision about base images.
- How the rule is expressed depends on the admission tool, chosen when its phase
  starts. Nothing here has been tested yet.

## References

- Google, [Binary Authorization for Borg](https://docs.cloud.google.com/docs/security/binary-authorization-for-borg) (Google Cloud documentation).
- Docker, [Hardened Images](https://www.docker.com/products/hardened-images/) and [Verify a Docker Hardened Image or chart](https://docs.docker.com/dhi/how-to/verify/).
- Docker Official Images, [postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md).
- J. H. Saltzer, M. D. Schroeder, [The Protection of Information in Computer Systems](https://web.mit.edu/Saltzer/www/publications/protection/) (Proceedings of the IEEE, 1975).
