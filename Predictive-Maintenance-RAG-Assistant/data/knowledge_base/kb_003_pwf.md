---
doc_id: kb_003
failure_mode: PWF
name: Power Failure
---

# Power Failure (PWF)

## Symptoms

Power failure is triggered when the mechanical power delivered to the process falls outside a safe operating band — either too low (insufficient power to complete the cut) or too high (overpowering the process).

Failure occurs when:
- `Power < 3500 W` (underpowered — torque too low relative to speed, risk of incomplete/stalled process), or
- `Power > 9000 W` (overpowered — excessive torque relative to speed, risk of mechanical overload)

## Root Cause

Power is a derived quantity, not a directly measured sensor value:

```
Power [W] = Torque [Nm] × Rotational speed [rad/s]
          = Torque [Nm] × Rotational speed [rpm] × (2π / 60)
```

## Sensor Signature

- Compute the derived `power` feature from torque and rotational speed; do not evaluate torque or speed in isolation
- A torque or rotational speed reading that looks "normal" in isolation can still produce an out-of-band power value — always check the product, not the individual factors
- Look for compensatory patterns: very high torque with very low speed (or vice versa) is the classic PWF signature

**Common misdiagnosis:** Torque or rotational speed alone appearing "in range" does not rule out PWF — always check the computed power value.

## Recommended Action

1. Compute and monitor `power` as a first-class derived feature in any real-time dashboard — do not rely on operators reading torque and speed separately.
2. If power trends toward either boundary (3500 W or 9000 W), adjust torque or speed setpoints before the process reaches the limit.
3. Investigate drive/motor calibration if power drifts outside band without an obvious setpoint change.

## Escalation & Safety

Overpower events (>9000 W) carry higher acute mechanical risk (potential for equipment damage) than underpower events and should be escalated with higher priority.
