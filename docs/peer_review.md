# Peer Review — powphysical MVP

## Blocking Issues (must fix)

1. **`resolver.py:41` hardcodes `require_wifi: True`** — ignores caller's request. Fix: pass `request` through.

2. **`compatibility.py:22` checks `input_voltage_max` instead of `input_voltage_min`** — 12V device passes USB check. Fix: check `min`.

3. **`compatibility.py:64-75` is a no-op** — `CameraComputeCheck` returns `(True, '')` always. Remove or implement.

4. **`base.py:40` — `import os` at bottom of file** — move to top.

5. **Division by zero at `resolver.py:149`** when `quantity=0`.

## Important Issues

6. `pow_reprice_build` silently drops missing parts — cost comparison meaningless.
7. `_get_price` returns 999.0 for missing prices — silently inflates costs.
8. No input validation anywhere.
9. Build storage is volatile (in-memory dict).
10. `Offer` dataclass exists but is never used.

## Design Concerns

11. Search logic duplicated between MCP and resolver.
12. 30 fixture components hardcoded in Python, not in data/.
13. Missing capabilities: `sense_soil_moisture`, `battery_power`, `drive_wheels`, `linux_compute`.
14. No logging.
15. Normalize pipeline half-built.
