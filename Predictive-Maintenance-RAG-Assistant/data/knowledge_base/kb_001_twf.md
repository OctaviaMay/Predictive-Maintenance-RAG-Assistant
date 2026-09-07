---
doc_id: kb_001
failure_mode: TWF
name: Tool Wear Failure
---

# Tool Wear Failure (TWF)

## Symptoms

Tool wear time accumulates into a critical band, typically between 200 and 240 minutes of continuous use. Within this band, failure probability rises sharply and can occur without any other sensor anomaly — torque, temperature, and rotational speed may all look nominal right up to the failure event.

## Root Cause

Progressive mechanical degradation of the cutting tool edge. As wear accumulates, the tool's ability to cut cleanly degrades, eventually leading to tool fracture or process failure. This is a wear-out failure, not a stress-overload failure — it is time/usage-driven rather than load-driven.

## Sensor Signature

- Primary indicator: `Tool wear [min]` in the 200–240 range
- Torque and rotational speed are **not** reliable leading indicators for TWF — this is the key diagnostic distinction from OSF and PWF
- No air/process temperature anomaly expected

**False-positive note:** A unit with tool wear in the 200–240 band that has NOT failed is common — this is a probabilistic band, not a deterministic threshold. Do not treat "in-band" as "failed."

## Recommended Action

1. Flag any unit with tool wear > 200 min for priority inspection queue, regardless of other readings.
2. Schedule tool replacement before reaching 240 min if the unit is queued for a long run.
3. Do not rely on torque spikes as an early warning — by the time torque changes, failure may already be underway.

## Escalation & Safety

TWF is typically a quality/downtime issue rather than an acute safety hazard. Escalate to line supervisor for scheduling; halt is not automatically required unless tool fracture risk is confirmed by visual inspection.
