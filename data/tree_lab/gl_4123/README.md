# Tree Lab case: Gavin Lake GL_4123

A real-data Tree Lab/FHOPS ground-system case built from the 2009 Gavin Lake
FUSION LIDARBIN canopy inventory.

## Case

- Case ID: `afrf-gavin-gl-4123`
- Block: `GL_4123`
- Area: 6.967 ha
- Trees: 400
- Mean stem: 3.49 m3
- Volume: 200.3 m3/ha; 1,395.5 m3 total
- TPH: 57.4
- Inventory: `tree_inventory/inventory.csv`
- Manifest: `case.json`
- Scenario: `scenario/scenario.yaml`
- Assignments: `assignments.csv`

The tree list is a canopy inventory, not a CFI. Species are `UNK` and DBH is
height allometry. The machine system is a reference execution model, not an
operational plan.

## System run

Command, from this directory with FHOPS `main` on `PYTHONPATH`:

```bash
python -m fhops.cli.main tree system scenario/scenario.yaml \
  --block GL_4123 \
  --feller H1 --skidder H2 --skidder H3 \
  --processor H5 --loader H4 \
  --bunch-volume 8.0 --rate-model calibrated \
  --shift-days 5 --shifts-per-day 2 --hours-per-shift 10 \
  --truck-capacity 30.0 --truck-count 2 --truck-cycle 3600.0 \
  --landing-capacity 120.0 --skidder-capacity 40.0 \
  --out runs/gl_4123/system
```

Result:

- 400 trees processed
- 1,384.4 m3 processed
- 52.4 h makespan
- 46 truck loads; 1,380 m3 dispatched
- Landing peak 41.1 m3; final 4.4 m3
- No warnings

Outputs:

- `runs/gl_4123/system/system_summary.json`
- `runs/gl_4123/system/system_events.csv`
- `runs/gl_4123/system/system_events.json`
- `runs/gl_4123/system/tree_processing.csv`

## Scene

```bash
python -m fhops.cli.main tree scene scenario/scenario.yaml assignments.csv \
  --out runs/gl_4123/scene --lod-threshold 200 --max-log-nodes 800
```

Result: 400 trees, 800 log nodes, simple LOD. The scene is procedural geometry,
not a surveyed tree map or machine CAD.

A local playback bundle was assembled in `runs/gl_4123/view/` with
`viewer.html`, `scene.gltf`, and `system_events.json`. Serve it with:

```bash
cd runs/gl_4123/view
python -m http.server 8794 --bind 127.0.0.1
# http://127.0.0.1:8794/viewer.html
```

The viewer shows the feller, skidders, processor, loader, and truck timeline.

## Copy into Tree Lab

Copy this directory into the Tree Lab `sandbox/cases/` tree on the Tree Lab
host. The `case.json` follows the observed `fhops.tree_lab.case.v1` manifest
shape. If the local runner expects a different manifest filename, rename
`case.json` to that name; the scenario, inventory, and assignments paths are
already relative to this directory.

The Tree Lab runner needs FHOPS with `tree system` (the unmerged Tree Lab
branch or current FHOPS `main`), not the `phase18` release checkout.
