# BATTLEFIELDS — executable battlefield intelligence

This directory is the machine-readable surface for external fights. Prose recommendations are not work orders.

## Law
1. Copy `_TEMPLATE.json` to `<battlefield_id>.json`.
2. Replace every placeholder with current evidence; re-check incumbent/rules immediately before canary/attack/claim.
3. Run `python tools/battlefield_gate.py BATTLEFIELDS/<battlefield_id>.json`.
4. Only `ADMIT_*` cards may enter the reducer.
5. Run `python tools/battlefield_reduce.py BATTLEFIELDS/*.json`.
6. The reducer emits at most 3 survivors and exactly one primary, or `NONE`.

A killed card remains evidence but is non-actionable until materially new evidence changes the failed field. Never route around a failed gate in prose.

## Scope
Battlefields are domain-agnostic. The selection objective is prestige + evolvability + buyer/income conversion per operator-minute, not familiarity with AI.

`_TEMPLATE.json` is documentation and is excluded from CI card execution.