---
doc_id: kb_004
failure_mode: OSF
name: Overstrain Failure
---

# Overstrain Failure (OSF)

## Symptoms

Overstrain failure occurs when accumulated mechanical strain — the product of tool wear and torque — exceeds a threshold. Critically, this threshold is **product-quality-dependent**: the same torque and wear values that are safe on one product variant can trigger failure on another.

Failure occurs when `strain_indicator` exceeds a variant-specific minimum:

| Quality variant | Threshold (approx.) |
|---|---|
| Low (L) | 11,000 min·Nm |
| Medium (M) | 12,000 min·Nm |
| High (H) | 13,000 min·Nm |

## Root Cause

Strain accumulates as a function of both how worn the tool is and how much torque is currently being applied:

```
strain_indicator = Tool wear [min] × Torque [Nm]
```

## Sensor Signature

- Requires the `Type` (L/M/H) field alongside `Tool wear` and `Torque`
- Compute `tool_wear × torque` and compare against the variant-specific threshold, not a single fixed number
- A worn tool under moderate torque and a fresh tool under high torque can both trigger OSF — the product, not either factor alone, is what matters

**Common misdiagnosis:** Applying a single global threshold across all product variants will produce both false positives (on L variant) and false negatives (on H variant). Always check variant-specific bands.

## Recommended Action

1. Always join product `Type` (L/M/H) into the OSF check — a threshold check without variant context will misclassify risk.
2. For long production runs on premium (H) variants, monitor cumulative wear×torque trend, not just current torque.
3. If a batch is running near its variant threshold, consider reducing torque setpoint or scheduling earlier tool replacement.

## Escalation & Safety

OSF represents genuine mechanical overstrain risk and can lead to tool or workpiece failure. Treat threshold breaches as higher priority than TWF alone.
