# Architecture

## Deployment boundary

Deploy once per two-entry photo challenge. Reuse the source through a fresh deployment with new entrants, judge, prompt, and criteria.

Constructor data establishes the deployment subject and fixed role boundary. Later writes add only the bounded records permitted by the lifecycle; a completed instance cannot be reopened.

## Participants

The deployer is the host and may also be the left entrant; left and right entrant addresses are fixed, and a different named judge records the final decision.

Addresses are normalized before authorization comparisons. Role checks and lifecycle gates execute before semantic assessment.

## State machine

`CRITERIA_SETUP → WAITING_FOR_ENTRIES → READY_TO_COMPARE → OBJECTION_WINDOW → COMPLETE`

The phase-like field is the primary lifecycle lock. Each write advances that path, performs a documented bounded loop, or fails with an `[EXPECTED]` user error.

## Evidence assembly

The stored challenge prompt, declaration rule, ordered criteria, each entrant's photo description, and its provenance declaration. Validators do not fetch or inspect image pixels or metadata.

Before consensus, the contract normalizes bounded text, copies required storage into plain local values, serializes a sorted JSON packet, and places it between explicit START/END delimiters. Nondeterministic callbacks do not read contract storage.

## Consensus boundary

Return left and right criterion masks plus LEFT, RIGHT, TIE, or NEITHER for the frozen declarations.

The leader callback validates exact JSON shape, field types, closed labels, masks or codes, and length bounds. A validator reruns the same semantic operation and rejects disagreement before state is committed.

## Deterministic boundary

Entrant authorization, one entry per side, criteria freezing, one objection per entrant, and judge-only finalization are deterministic.

Important invariants:

- Criteria freeze before either entry can be compared.
- Only the designated entrant can submit its assigned side.
- Each entrant may lodge at most one bounded objection after comparison.
- AI cannot select the final winner; only the distinct human judge can do so.

No method sends value, pays rewards, escrows assets, deletes external data, calls another contract, or invokes a webhook.

## Failure model

- Invalid caller input or lifecycle use raises `[EXPECTED]` and leaves state unchanged.
- Malformed or out-of-policy model output raises `[LLM_ERROR]` and cannot be stored.
- Validator disagreement cannot commit the semantic result.
- StudioNet proof reads explicitly target `LATEST_FINAL`, avoiding stale pre-final state.
