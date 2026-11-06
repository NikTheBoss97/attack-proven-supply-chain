<!-- Author: Nicola Antonello -->

# Application security

The attacks the service has to withstand, and the database features behind its controls. Part of the [reading list](README.md).

## Attacks on APIs

- ★ OWASP, [API Security Top 10 (2023)](https://api-security.owasp.org/editions/2023/en/0x11-t10) (OWASP). Ranks broken object-level authorization first and server-side request forgery seventh.
- OWASP, [API1:2023 Broken Object Level Authorization](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization) (OWASP). How it happens and how to prevent it: check access on every record lookup, prefer random IDs, and test the authorization mechanism.
- Psycopg, [Passing parameters to SQL queries](https://www.psycopg.org/psycopg3/docs/basic/params.html) (Psycopg 3 documentation). Why values must never be merged into a query with `%` or `+`, and how the query and its parameters reach the server separately.
- Bahruz Jabiyev et al., [Preventing Server-Side Request Forgery Attacks](https://doi.org/10.1145/3412841.3442036) (ACM SAC, 2021). What SSRF is and how to defend against it.
- M. Monshizadeh, P. Naldurg, V. N. Venkatakrishnan, [MACE: Detecting Privilege Escalation Vulnerabilities in Web Applications](https://doi.org/10.1145/2660267.2660337) (ACM CCS, 2014). Finding broken authorization, the class behind object-level attacks.
- Z. Su, G. Wassermann, [The Essence of Command Injection Attacks in Web Applications](https://doi.org/10.1145/1111037.1111070) (ACM POPL, 2006). A formal definition: input that changes the intended syntax of a query.

## PostgreSQL

- PostgreSQL, [Row Security Policies](https://www.postgresql.org/docs/18/ddl-rowsecurity.html) (PostgreSQL 18 documentation). Per-user limits on which rows a query can see, and which roles bypass them.
- PostgreSQL, [COPY](https://www.postgresql.org/docs/18/sql-copy.html) (PostgreSQL 18 documentation). How `COPY ... PROGRAM` runs a command on the server, and which roles may use it: why an injection's reach depends on the database role.
- PostgreSQL, [psql: SQL Interpolation](https://www.postgresql.org/docs/18/app-psql.html#APP-PSQL-INTERPOLATION) (PostgreSQL 18 documentation). How `:'name'` quotes a variable's value as an SQL literal, why an unset variable is left as written, and `\getenv`, which reads one from the environment.
- Docker Official Images, [postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md) (image documentation). How the image runs setup scripts on an empty data directory, why it trusts connections from inside its own container, and how it runs as another user.
