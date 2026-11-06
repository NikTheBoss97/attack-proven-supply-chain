<!-- Author: Nicola Antonello -->

# ADR-0004: A bookmarks API on FastAPI and PostgreSQL

- Status: accepted
- Date: 2026-11-05

## Context

ADR-0002 chose a small service and ADR-0003 chose Python. The service still has to
do something, and what it does decides which application attacks exist. The scope
asks for broken object-level authorization, injection and SSRF. An attack on a
feature that exists only to be attacked teaches little, so each attack should come
from an ordinary feature.

## Options

What the service does:

| Option | Why not |
|---|---|
| **A read-later bookmarks API** | Chosen. Users save links, the service fetches each link's page title, and users search their own bookmarks. Bookmarks that belong to a user invite broken object-level authorization, first in the OWASP API Security Top 10 (2023). Fetching a saved URL invites SSRF, seventh on that list. Search invites SQL injection. |
| Notes with file attachments | It adds path traversal, but SSRF would be bolted on. |
| A webhook relay | It is strong on SSRF, with little for authorization or injection. |

The framework:

| Option | Why not |
|---|---|
| **FastAPI** | Chosen. It validates requests with Pydantic and is based on OpenAPI, and ZAP's API scan accepts an OpenAPI definition, so the DAST phase can start from the service's own list of endpoints. CodeQL lists it as supported, and Semgrep names it under Semgrep Code. |
| Flask | It is smaller, with fewer dependencies, and CodeQL and Semgrep name it too. As far as this record knows, it needs an extension or a hand-written definition for the same scan (not checked). |

The data store:

| Option | Why not |
|---|---|
| **PostgreSQL** | Chosen. It is a separate server with its own credentials, network path and roles, so the threat model covers more than a file inside the service's pod. Its roles decide how far an injection can reach: `COPY ... PROGRAM` runs a command on the server, and only superusers or roles granted a specific privilege may use it. Row-level security is available as a second control behind the service's own check. More than one replica of the service can share it. |
| SQLite | It is simpler: it needs no separate server and adds no third-party image. But a file inside one pod limits the service to one replica, and it has no network path or roles to defend. |

## Decision

The service is a read-later bookmarks API on FastAPI, storing its data in
PostgreSQL. Its version and driver stay open.

## Consequences

- PostgreSQL's image is not built by this repository's CI, which the project's
  image rule requires. That needs its own decision.
- A database password now exists. It is a new asset in the threat model and must
  never reach git.
- The driver affects what scanners can see. CodeQL lists `psycopg`, `psycopg2` and
  `asyncpg`. Semgrep's Python page names `psycopg2` and does not name `psycopg`. So
  coverage of the chosen driver has to be tested, with a planted injection, before a
  clean scan means anything.
- Semgrep's framework-specific analysis belongs to Semgrep Code. Its documentation
  warns that many of those rules return no findings on the Community Edition, which
  matters when the SAST tool is chosen.
- Each run of the suite starts one more component and waits for it (not measured).
- PostgreSQL has to run as a non-root user with a read-only root filesystem, like
  every container here. The image's documentation says it supports an arbitrary user
  who owns `PGDATA`, but it lists no writable directories, so this has to be shown
  on its first deployment.
- Row-level security does not bind superusers or `BYPASSRLS` roles, and table owners
  bypass it unless it is forced. It only works as a second control if the service
  connects with a role it applies to.

## References

- OWASP, [API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10).
- FastAPI documentation, [Features](https://fastapi.tiangolo.com/features/).
- ZAP documentation, [API Scan](https://www.zaproxy.org/docs/docker/api-scan/).
- CodeQL, [Supported languages and frameworks](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/).
- Semgrep documentation, [Python](https://docs.semgrep.dev/languages/python).
- PostgreSQL 18 documentation, [COPY](https://www.postgresql.org/docs/18/sql-copy.html) and [Row Security Policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html).
- Docker Official Images, [postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md).
- Psycopg 3 documentation, [Passing parameters to SQL queries](https://www.psycopg.org/psycopg3/docs/basic/params.html).
- Python documentation, [sqlite3](https://docs.python.org/3/library/sqlite3.html).
