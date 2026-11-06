<!-- Author: Nicola Antonello -->

# ADR-0002: A small service in this repository as the workload

- Status: accepted
- Date: 2026-11-05

## Context

The platform needs a workload: an application it builds, signs, deploys and
defends. Two of the project's rules constrain the choice. An attack proves a
control only if it succeeds with the control off, so application attacks need
something that can really be exploited. And only images built by this repository's
CI may run in the cluster, so the workload's build has to happen here.

## Options

| Option | Why not |
|---|---|
| **A small new service in this repository** | Chosen |
| An existing, larger application | An application designed to resist these attacks gives application attacks little to succeed against unless it is weakened. Its build would also have to move into this repository's CI, which ties this project to another project's schedule. |
| A ready-made vulnerable application, such as OWASP Juice Shop | Custom SAST rules could not target the project's own code, and a pipeline around a known vulnerable application is a common portfolio project, which this one tries not to be. |

## Decision

The workload is one small HTTP service in this repository, with real
authentication, authorization and input handling. Its language is a separate
decision.

This project depends on no application outside this repository.

## Consequences

- There is one more service to write and maintain. It stays small, because it is
  not what the project is showing.
- It has to contain real weaknesses for application attacks to succeed with the
  control off. How a weakness can exist without being left open in what ships is
  not decided yet.
- A small service can look like a toy. The README has to say that the platform is
  the subject, not the service.
- Nothing here proves the platform works on a larger service. Onboarding one later
  could show that, but it is not planned, and it would need its own record.
