<!-- Author: Nicola Antonello -->

# ADR-0001: Record decisions as ADRs

- Status: accepted
- Date: 2026-11-05

## Context

What this project has to show is that its choices can be defended. The code shows
what was built. It does not show why, what was rejected, or what a choice gave up.
The design is also worked out over many sessions, and a decision that lives only
in a conversation is lost when the conversation ends.

## Options

| Option | Why not |
|---|---|
| **One short file per decision, numbered, in the repository** | Chosen |
| One design document, edited as decisions change | It shows the current state and loses what was rejected. A reversed decision leaves no trace. |
| Commit messages and pull request descriptions | A reader has to know where to look, and a decision that spans several commits has no single home. |
| A wiki or an issue tracker | It sits outside the repository, so it can drift from the code, and a reviewer may never open it. |

## Decision

Every significant decision gets an Architecture Decision Record in
`docs/adr/NNNN-title.md`, numbered in the order decisions are accepted. A decision
is significant when it picks a tool, draws a trust boundary, sets a policy model,
shapes an attack, or would be costly to reverse.

- **Before the record.** The owner sees 2-3 options with their tradeoffs and a
  recommendation, and decides. The record is written as soon as the owner accepts,
  not at the end of the work.
- **Its parts.** Status, date, Context, Options and why each was not chosen,
  Decision, Consequences, and References when it relied on a source. Consequences
  include what the decision gives up and what is still unverified.
- **After acceptance.** An accepted record changes only to clarify it, with a dated
  entry under `## Amendments`. A changed decision gets a new record that supersedes
  the old one, and the old one stays, marked `superseded by ADR-NNNN`.
- **Next to the design.** `docs/DESIGN.md` describes the design as it is now. The
  records say how it got there.

The format follows Nygard's, with Options added.

## Consequences

- Each decision takes longer and costs a small file.
- A wrong decision stays visible instead of being edited away, which is what makes
  the record honest.
- Each record is a prepared answer to the question "why this and not that?"
- Nothing enforces the practice. In Buchgeher et al.'s study, about half of the
  GitHub repositories with ADRs hold only one to five, which suggests the practice
  is often tried and not kept. Review is the only check that a decision got its
  record.

## References

- Michael Nygard, [Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (Cognitect, 2011).
- Georg Buchgeher et al., [Using Architecture Decision Records in Open Source Projects—An MSR Study on GitHub](https://doi.org/10.1109/ACCESS.2023.3287654) (IEEE Access, 2023).
- J. Tyree, A. Akerman, [Architecture Decisions: Demystifying Architecture](https://doi.org/10.1109/MS.2005.27) (IEEE Software, 2005).
- A. Jansen, J. Bosch, [Software Architecture as a Set of Architectural Design Decisions](https://doi.org/10.1109/WICSA.2005.61) (WICSA, 2005).
