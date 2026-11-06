<!-- Author: Nicola Antonello -->

# ADR-0006: The service's API, authentication and data layer

- Status: accepted
- Date: 2026-11-05

## Context

ADR-0004 chose a read-later bookmarks API on FastAPI and PostgreSQL. The service
stays small because the platform is what the project shows, but its controls have
to be real, because the attacks test them.

## Options

Authentication:

| Option | Why not |
|---|---|
| **A random bearer token, stored only as a SHA-256 digest** | Chosen. `secrets.token_urlsafe(32)` gives 32 random bytes, which Python's documentation considers sufficient. A slow hash protects guessable passwords, and a fast one is enough for a value nobody can guess. |
| Passwords with JWTs | They add dependencies and attack classes the scope does not ask for. |

Bookmark IDs:

| Option | Why not |
|---|---|
| **Random UUIDs** | Chosen. OWASP recommends random, unpredictable IDs alongside the authorization check. The check stays the control the attacks test. |
| Sequential integers | Enumeration would be easy to demonstrate, but they drop a defense OWASP recommends. |

When the service fetches page titles:

| Option | Why not |
|---|---|
| **In Phase 4, together with its SSRF control and attack** | Chosen. Until then, the caller supplies the title. |
| In Phase 1 | It would leave a known SSRF hole in `main` for three phases. |

The database driver:

| Option | Why not |
|---|---|
| **`psycopg` 3 from its binary wheels, with plain `def` endpoints** | Chosen. Its documentation says the wheels need no compiler or local libraries, which suits `--only-binary :all:` (ADR-0003). FastAPI runs plain `def` endpoints in a threadpool, so a blocking query does not block the server. |
| `psycopg2-binary` | Semgrep's Python page names `psycopg2`, but `psycopg2`'s documentation advises against the binary package in production, and the source build it recommends conflicts with `--only-binary :all:`. |
| `asyncpg` | It would make the whole service async, for no gain at this size. |

The schema:

| Option | Why not |
|---|---|
| **SQL scripts built into the rebuilt PostgreSQL image** | Chosen. The official image runs them when the data directory is empty, and the database is recreated on every run. |
| A migration tool such as Alembic | It adds a dependency when there is nothing to migrate. |

Database roles:

| Option | Why not |
|---|---|
| **One role that owns the tables, and a separate login role for the service** | Chosen. The service's role has only the table privileges it needs and is neither a superuser nor the owner. An injection then cannot use `COPY ... PROGRAM`, which needs a superuser or a granted role. |
| One role for everything | It is simpler, but an injection would reach whatever that role can do, including commands on the server if it is a superuser. |

Versions:

| Option | Why not |
|---|---|
| **Python 3.14 and PostgreSQL 18** | Chosen. Both are current stable releases that the project's other tools list as supported. |
| Python 3.15 | It was released on 2026-10-09, but CodeQL's list of supported versions stops at 3.14. |
| PostgreSQL 19 | It is only a release candidate, and `psycopg` lists support up to 18. |

## Decision

The API uses JSON. Every endpoint needs a token except `POST /users` and
`GET /healthz`.

| Endpoint | What it does |
|---|---|
| `POST /users` | Creates a user and returns their token once |
| `POST /bookmarks` | Saves a link and its title for the caller |
| `GET /bookmarks?q=` | Lists the caller's bookmarks, with an optional search |
| `GET /bookmarks/{id}` | Reads one of the caller's bookmarks |
| `DELETE /bookmarks/{id}` | Deletes one of the caller's bookmarks |
| `GET /healthz` | Tells Kubernetes the service is alive |

There are two tables, `users` and `bookmarks`. Every query on bookmarks is limited to
the caller (`WHERE id = %s AND user_id = %s`), and someone else's bookmark returns the
same 404 as one that does not exist. That ownership check is the first control.

The database password is generated at deployment and passed to PostgreSQL as a
Kubernetes Secret. It never reaches git.

## Consequences

- Anyone can create a user, and nothing limits request rates. A real service would
  need both. They are left out because no attack in the scope needs them.
- A lost token cannot be recovered, only replaced by a new user.
- The database cannot be upgraded in place, which is acceptable because it holds no
  data worth keeping.
- Search uses parameterized SQL from the start, but it is not claimed as a control
  until its attack exists.
- Scanner coverage of `psycopg` is still unproven. ADR-0004's planted injection
  decides it.
- Row-level security stays a Phase 4 decision, as a possible second control behind
  the ownership check.
- None of this has been built yet.

## References

- Python documentation, [secrets](https://docs.python.org/3/library/secrets.html) and [Status of Python versions](https://devguide.python.org/versions/).
- OWASP, [API1:2023 Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization).
- FastAPI documentation, [Concurrency and async / await](https://fastapi.tiangolo.com/async/).
- Psycopg 3 documentation, [Installation](https://www.psycopg.org/psycopg3/docs/basic/install.html).
- Psycopg 2 documentation, [Installation](https://www.psycopg.org/docs/install.html).
- Docker Official Images, [postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md).
- PostgreSQL, [COPY](https://www.postgresql.org/docs/18/sql-copy.html) and [Versioning Policy](https://www.postgresql.org/support/versioning/).
- CodeQL, [Supported languages and frameworks](https://codeql.github.com/docs/codeql-overview/supported-languages-and-frameworks/).
- Semgrep documentation, [Python](https://docs.semgrep.dev/languages/python).
