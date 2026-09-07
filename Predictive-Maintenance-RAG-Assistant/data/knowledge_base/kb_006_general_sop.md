---
doc_id: kb_006
failure_mode:
name: General Triage and Escalation SOP
---

# General Triage and Escalation SOP

This document covers cross-cutting procedure that applies regardless of which failure mode is flagged.

## Trigger Confirmation & Severity Classification

**Step 1 — Confirm the trigger.** Before generating an incident report, confirm which specific derived condition fired:
- Tool wear in 200–240 min band → possible TWF
- `temp_diff < 8.6 K` AND `rotational speed < 1380 rpm` → possible HDF
- Computed power outside 3500–9000 W → possible PWF
- `tool_wear × torque` over variant threshold → possible OSF
- No condition met, but failure flagged → likely RNF

**Step 2 — Severity classification.**

| Failure mode | Typical severity | Response window |
|---|---|---|
| PWF (overpower) | High | Immediate |
| OSF | High | Immediate |
| PWF (underpower) | Medium | Same shift |
| HDF | Medium | Same shift |
| TWF | Low–Medium | Next scheduled window |
| RNF | Variable | Case-by-case, post-hoc review |

## Halt Criteria

**Step 3 — Halt criteria.** Halt the process immediately if ANY of the following hold, regardless of which failure mode triggered:
- Computed power exceeds 9000 W
- `tool_wear × torque` exceeds the variant threshold by more than 10%
- Two or more failure conditions are met simultaneously (multi-mode failures are rare but higher severity)

Otherwise, flag for inspection at the next scheduled maintenance window rather than halting — unnecessary halts carry their own production cost.

## Report Contents & Escalation Contacts

**Step 4 — Report contents.** Every incident report should state:
1. Which condition(s) fired and their measured values vs. threshold
2. Severity classification and recommended response window
3. The specific corrective action from the relevant failure-mode document
4. Whether immediate halt is required per the Halt Criteria section

**Step 5 — Escalation contacts.** Route high-severity incidents to line supervisor immediately; route low/medium severity to the standard maintenance queue.

**Caution on model confidence:** A model's predicted failure probability is not the same as a confirmed condition. Always cross-check the model's flag against the actual computed derived feature (power, temp_diff, strain_indicator) before writing a report that asserts a specific root cause.
