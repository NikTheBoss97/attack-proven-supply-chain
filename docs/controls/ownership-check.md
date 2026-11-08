<!-- Author: Nicola Antonello -->

# Ownership check

Stops broken object-level authorization, threat T-API-1 in the
[threat model](../THREAT_MODEL.md): a user who reads or deletes another user's
bookmark by its ID. OWASP ranks this class first in its
[API Security Top 10](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization).

## The control

Every query on one bookmark is limited to the caller
([ADR-0006](../adr/0006-service-api-authentication-and-data-layer.md)):

```sql
SELECT id, url, title, created_at FROM app.bookmarks WHERE id = %s AND user_id = %s
DELETE FROM app.bookmarks WHERE id = %s AND user_id = %s
```

`user_id` comes from the caller's token, never from the request. When no row
matches, the service answers `404` with `{"error": "bookmark_not_found"}`. The
response is the same, byte for byte, whether the bookmark belongs to someone
else or does not exist, so it does not reveal that the bookmark exists.
Bookmark IDs are random UUIDs, which makes guessing one impractical, but the
check, not the randomness, is the control.

## The attack

[`attacks/bola/attack.py`](../../attacks/bola/attack.py). Alice and Bob each get
an account. Alice saves a bookmark and reads it back, which proves that it
exists; if she cannot, the run reports `error`. Then:

| Run | What it does | Must report |
| --- | --- | --- |
| Control off | Without the check, Bob reads Alice's bookmark, then in a second try deletes one | `succeeded`, both times |
| Control on | Bob reads Alice's bookmark | `blocked`, with `404 bookmark_not_found` |
| Variant | Bob deletes Alice's bookmark, which a check written only for reads would let through. Whether Alice can still read it decides the result, not Bob's response | `blocked`, with `404 bookmark_not_found` |
| Legitimate | Alice reads her own bookmark, deletes it, and finds it gone | works |

[`control-off.patch`](../../attacks/bola/control-off.patch) removes
`AND user_id = %s` and its parameter from both queries, and nothing else. The
suite applies it to a copy of `app/` and loads the image built from that copy
only into its own throwaway cluster
([ADR-0007](../adr/0007-how-the-attack-suite-works.md)). If the code moves so
that the patch no longer applies, the suite fails instead of testing nothing.

## Evidence

- On `main`, CI's [`attacks` job](https://github.com/NikTheBoss97/attack-proven-supply-chain/actions/runs/42498639830)
  ran the four runs and reproduced the README's table: control off `succeeded`,
  control on `blocked`, variant `blocked`, legitimate `works`.
- [A pull request that removes the check](https://github.com/NikTheBoss97/attack-proven-supply-chain/pull/8),
  by applying `control-off.patch` to the real code, failed both required jobs and
  was closed without merging:
  - [`gates`](https://github.com/NikTheBoss97/attack-proven-supply-chain/actions/runs/42500125247/job/128790869471):
    the service's tests `test_another_users_bookmark_looks_missing` and
    `test_another_user_cannot_delete` failed, the two that check the ownership
    rule directly.
  - [`attacks`](https://github.com/NikTheBoss97/attack-proven-supply-chain/actions/runs/42500125247/job/128790869941):
    control on and the variant reported `succeeded`, since Bob read Alice's
    bookmark and deleted it, and control off reported `error`, since its patch no
    longer applied to code that had already lost the check. The table check
    printed the difference.

## Known bypasses

- A new endpoint or query that forgets the user filter. The check lives in each
  query, so every new query needs its own, and its own test.
- An ID learned some other way: from a log, a shared link or a referrer. Random
  UUIDs do not stop someone who already has the ID. Only the check does.

## What it does not cover

- Listing and search. They are limited by the same rule, `WHERE user_id = %s`,
  but only unit tests check that, so it is not claimed (T-API-2).
- Stolen tokens. Whoever holds Alice's token is Alice to the service (T-API-4).
- Enumeration and rate limits. Nothing limits how many IDs a user can try
  (T-API-5, T-API-6).
- A second control behind this one. Row-level security in PostgreSQL is a
  Phase 4 decision.
