<!-- Author: Nicola Antonello -->

# ADR-0010: How tests reach the service

- Status: accepted
- Date: 2026-11-06

## Context

The service's tests need a database, and the attack harness needs to reach the
service inside a throwaway `kind` cluster. Both run inside the toolbox container
(ADR-0008, ADR-0009), which drives the host's Docker through its socket. ADR-0008
noted that reaching a `kind` cluster from a container had not been tried on Windows.
ADR-0004 noted that PostgreSQL's image lists no writable directories, so whether it
runs with a read-only root filesystem was unknown. Both were tried first, on
2026-11-06, on Windows 11 with Docker Desktop:

- A container joined to kind's Docker network drove the cluster with the kubeconfig
  from `kind get kubeconfig --internal`, from Git Bash and from WSL alike. Creating
  the cluster took 29 to 56 seconds.
- A Service's NodePort answered about a second after the Service was created, because
  kube-proxy writes its rules asynchronously. A pod with no readiness probe counted
  as ready before its server was listening.
- PostgreSQL 18 ran as user 999 with a read-only root filesystem, given writable
  mounts at `/var/lib/postgresql`, `/var/run/postgresql` and `/tmp`. It also writes
  to `/dev/shm`, which the container runtime provides on its own.

The project also needs a rule for which endpoints land before the first attack does.

## Options

How the service's tests reach a database:

| Option | Why not |
|---|---|
| **A real PostgreSQL built from `db/`** | Chosen. The tests run in an image built from the service's own lock files, on a Docker network with the database. |
| Mocking the data layer | The ownership check lives in the SQL `WHERE` clause, so a mocked test would still pass with the check removed. In Spadini et al.'s study, developers prefer not to mock classes that hold the system's rules, and find it hard to keep a mock's behavior compatible with the real class. |

How the harness reaches the cluster:

| Option | Why not |
|---|---|
| **kind's Docker network and a NodePort** | Chosen. After creating the cluster, the harness connects the toolbox container to kind's network and uses `kind get kubeconfig --internal`. It reaches the service on the node's NodePort, set by a kustomize patch that exists only in the test overlay. |
| Host networking | Docker Desktop supports it only from version 4.34, after the user signs in and turns it on in its settings, so it is not portable. |
| `kubectl port-forward` | One more long-running process per stack, and one more thing to fail mid-run. |

Image references in the test cluster:

| Option | Why not |
|---|---|
| **`kind load` under a unique tag per run** | Chosen. The default `IfNotPresent` pull policy finds a loaded image, as long as its tag is not `latest`. |
| A local registry on kind's network, deploying by digest | One more component, and Phase 2's registry decision made early. |

The order of the first control:

| Option | Why not |
|---|---|
| **The ownership check lands with its attack** | Chosen. Reads and deletes by ID land with their ownership check in the same commit as the attack, after the harness is proven on the other endpoints. Listing is limited to the caller too, but it has no attack, so it lands earlier with unit tests and is not claimed. |
| Building the whole service first | The claimed check would sit in `main` for three pull requests with no attack. |

## Decision

- The database's and the service's tests run against a real PostgreSQL built from
  `db/`, on a Docker network made for the run.
- The service's database role gets its password from the environment through psql's
  `\getenv`, quoted as an SQL literal by `:'api_password'`. If the variable is unset,
  psql leaves `:'api_password'` as written, the statement fails, and setup stops,
  because the image runs its scripts with `ON_ERROR_STOP=1`.
- The harness creates its `kind` cluster, connects the toolbox container to kind's
  network, and uses the internal kubeconfig. It reaches the service on a NodePort that
  only the test overlay sets, and polls `/healthz` until it answers instead of
  fetching once.
- Images reach the test cluster through `kind load`, under a tag unique to the run.
  This is an exception to "deployed by digest, never by tag", limited to the
  throwaway cluster until a registry exists.
- PostgreSQL runs with a read-only root filesystem and writable `emptyDir` volumes at
  the three paths above.
- A control lands with its attack. Behavior with no attack, such as listing only the
  caller's bookmarks, is tested but not claimed.

## Consequences

- The image's `initdb` trusts connections from inside its own container, so every
  database test connects from another container, with a password.
- Passwords are generated per run and never written to the repository.
- The NodePort exists only in the test cluster. The base manifests keep `ClusterIP`.
- Inside the test cluster an image is found by its tag, not its digest. Each run
  builds and loads its own, so nothing else uses that tag, but the cluster does not
  check what the tag points to.
- A single request right after a deployment can fail even when everything works, so
  every wait in the harness polls with a deadline.
- Listing is limited by the same `user_id` filter, but the project claims nothing
  about it until an attack tests it.
- How long a run takes, and how much disk it uses on CI runners, is measured later in
  Phase 1.

## References

- kind, [Access kind cluster from a container outside of cluster](https://github.com/kubernetes-sigs/kind/issues/2148) (issue #2148).
- kind documentation, [Quick Start: Loading an Image Into Your Cluster](https://kind.sigs.k8s.io/docs/user/quick-start/#loading-an-image-into-your-cluster).
- Docker Official Images, [postgres](https://github.com/docker-library/docs/blob/master/postgres/README.md).
- PostgreSQL 18 documentation, [psql](https://www.postgresql.org/docs/18/app-psql.html): [`\getenv`](https://www.postgresql.org/docs/18/app-psql.html#APP-PSQL-META-COMMAND-GETENV) and [SQL Interpolation](https://www.postgresql.org/docs/18/app-psql.html#APP-PSQL-INTERPOLATION).
- Docker documentation, [Host network driver](https://docs.docker.com/engine/network/drivers/host/).
- D. Spadini, M. Aniche, M. Bruntink, A. Bacchelli, [To Mock or Not to Mock? An Empirical Study on Mocking Practices](https://doi.org/10.1109/MSR.2017.61) (MSR, 2017).
