---
doc_id: kb_002
failure_mode: HDF
name: Heat Dissipation Failure
---

# Heat Dissipation Failure (HDF)

## Symptoms

Heat dissipation failure occurs when the process is unable to shed heat effectively during low-speed operation. It is defined jointly by two conditions occurring together:

1. The gap between process temperature and air temperature is small — specifically, `Process temperature [K] − Air temperature [K] < 8.6 K`
2. Rotational speed is low — specifically, `Rotational speed [rpm] < 1380`

Neither condition alone is sufficient; HDF is a **combined-condition** failure mode.

## Root Cause

At low rotational speed, airflow and mechanical agitation around the tool/workpiece drop, reducing convective heat transfer. If the process and ambient temperatures are already close together (small thermal gradient), there is insufficient thermal driving force to dissipate process heat, and heat accumulates locally.

## Sensor Signature

- Compute the derived feature `temp_diff = Process temperature − Air temperature`
- Watch for `temp_diff < 8.6 K` AND `Rotational speed < 1380 rpm` simultaneously
- Air and process temperature individually may look "normal" — it's the *gap* and the *speed* together that matter

**Common misdiagnosis:** Do not diagnose HDF from rotational speed alone — many low-speed runs are entirely safe. The joint condition with `temp_diff` is what distinguishes a true HDF risk from normal low-speed operation.

## Recommended Action

1. Add `temp_diff` as a monitored derived feature, not just raw temperatures.
2. If a unit is running below 1380 rpm for an extended period, actively check the temperature gradient rather than assuming low speed is inherently safe.
3. Consider forced cooling or increasing rotational speed if both conditions are trending toward the threshold simultaneously.

## Escalation & Safety

Sustained low thermal gradient at low speed can be an early indicator of coolant or airflow system issues upstream — worth a maintenance ticket even if failure hasn't yet triggered.
