# Photo Challenge

Compares two designated entrants' frozen photo descriptions against host-defined criteria, permits objections, and reserves the final winner for a separate human judge.

## Why it is an Intelligent Contract

Return left and right criterion masks plus LEFT, RIGHT, TIE, or NEITHER for the frozen declarations. GenLayer validators independently replay that semantic judgment before it becomes shared state. Entrant authorization, one entry per side, criteria freezing, one objection per entrant, and judge-only finalization are deterministic.

## Reusable deployment model

Deploy once per two-entry photo challenge. Reuse the source through a fresh deployment with new entrants, judge, prompt, and criteria.

A completed deployment is an auditable record and is not reset or silently repurposed. Reuse means deploying the same reviewed source with new constructor data.

## Roles and workflow

The deployer is the host and may also be the left entrant; left and right entrant addresses are fixed, and a different named judge records the final decision.

State path: `CRITERIA_SETUP → WAITING_FOR_ENTRIES → READY_TO_COMPARE → OBJECTION_WINDOW → COMPLETE`

## Evidence boundary

The stored challenge prompt, declaration rule, ordered criteria, each entrant's photo description, and its provenance declaration. Validators do not fetch or inspect image pixels or metadata.

## Core invariants

- Criteria freeze before either entry can be compared.
- Only the designated entrant can submit its assigned side.
- Each entrant may lodge at most one bounded objection after comparison.
- AI cannot select the final winner; only the distinct human judge can do so.

## Public interface

Write methods: `append_criterion, compare_entries, freeze_entries, object_left, object_right, open_duel, record_judgment, submit_left_entry, submit_right_entry`

View methods: `get_entry, get_policy, get_state`

`get_policy` exposes the machine-readable operating boundary and confirms that this contract never custodies funds.

## Verification

Pinned GenVM runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`

```powershell
python -m pip install -r requirements.txt
genvm-lint check contracts/photo_challenge.py
genvm-lint typecheck contracts/photo_challenge.py
pytest tests/direct -q
python tests/run_glsim.py --port 4000 --validators 5 --no-browser
gltest tests/integration/test_glsim_consensus.py --network localnet -q
```

The StudioNet smoke test is opt-in and uses three disposable Mimi-only accounts protected outside the workspace. It asserts finalized successful execution and reads committed state with `LATEST_FINAL`.

## Final StudioNet proof

- Contract: https://explorer-studio.genlayer.com/address/0xb1eB7d6DFd7A7985d0eBFEb7683fe72812B1d484
- Studio import: https://studio.genlayer.com/?import-contract=0xb1eB7d6DFd7A7985d0eBFEb7683fe72812B1d484
- Deployment transaction: https://explorer-studio.genlayer.com/tx/0x5ea4b151c848020eb964caa2e56bee6b86cb8148f543ec2962ea1f1250e33a34
- Intelligent transaction: https://explorer-studio.genlayer.com/tx/0x39f553db845953c601d7442606f025a6652ff297c6dbd61481271a10565e6a6c
- Observed committed state: `"LEFT"`
- Audited source SHA-256: `ab5f14ef2daa8760fd6dd28b76148b8a98dce0f246d3cc1d2052ed3f5e7e655c`

## Limitations

- The contract compares text declarations and does not inspect photographs.
- Time, place, authorship, and provenance declarations are recorded but not authenticated.
- The comparison is challenge-specific and is not a general artistic-quality score.

## Repository map

- `contracts/photo_challenge.py` — Intelligent Contract source
- `tests/direct` — hardened leader/validator and lifecycle tests
- `tests/integration/test_glsim_consensus.py` — five-validator simulator flow
- `tests/integration/test_studionet_smoke.py` — live opt-in proof
- `deployments/studionet.json` — source-bound public deployment evidence
- `ARCHITECTURE.md`, `SOURCE_POLICY.md`, `SECURITY.md`, `AUDIT.md` — reviewer material

License: MIT.
