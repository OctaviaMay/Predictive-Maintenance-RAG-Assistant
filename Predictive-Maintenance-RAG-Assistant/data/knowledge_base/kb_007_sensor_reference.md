---
doc_id: kb_007
failure_mode:
name: Sensor and Derived Feature Reference
---

# Sensor and Derived Feature Reference

## Raw Sensor Fields

| Field | Unit | Description |
|---|---|---|
| Type | L/M/H | Product quality variant |
| Air temperature | K | Ambient temperature near the process |
| Process temperature | K | Temperature of the process itself (typically air temp + ~10K + noise) |
| Rotational speed | rpm | Spindle/tool rotational speed |
| Torque | Nm | Applied torque |
| Tool wear | min | Cumulative tool usage time |

## Derived Features & Quick Lookup

| Derived feature | Formula | Used for |
|---|---|---|
| temp_diff | Process temperature − Air temperature | HDF |
| power | Torque × Rotational speed × (2π / 60) | PWF |
| strain_indicator | Tool wear × Torque | OSF |

**Why derived features matter:** None of the four sensor-driven failure modes (TWF excepted, which uses tool wear directly) can be correctly diagnosed from raw sensor values alone. HDF, PWF, and OSF are all defined on combinations of two or more raw fields. Any retrieval or reasoning system working with this data should compute these derived features before attempting root-cause classification, not rely on an LLM to mentally combine raw values on the fly.

**Quick lookup — which fields matter for which failure mode:**

| Failure mode | Fields required |
|---|---|
| TWF | Tool wear |
| HDF | Air temperature, Process temperature, Rotational speed |
| PWF | Torque, Rotational speed |
| OSF | Type, Tool wear, Torque |
| RNF | None (background rate) |
