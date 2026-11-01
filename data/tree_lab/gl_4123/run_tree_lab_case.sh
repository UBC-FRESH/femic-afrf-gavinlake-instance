#!/usr/bin/env bash
# Reproduce the Gavin Lake GL_4123 Tree Lab/FHOPS case.
#
# FHOPS_SRC must point at a checkout with `fhops tree system` (Tree Lab branch
# or current FHOPS main). RUN from this case directory.
set -euo pipefail

: "${FHOPS_SRC:?set FHOPS_SRC to the FHOPS src directory}"
PYTHON="${PYTHON:-python}"
VIEWER="${VIEWER:-$FHOPS_SRC/../examples/tree_system/viewer.html}"

export PYTHONPATH="$FHOPS_SRC${PYTHONPATH:+:$PYTHONPATH}"

rm -rf runs/gl_4123/system runs/gl_4123/scene runs/gl_4123/view
"$PYTHON" -m fhops.cli.main tree system scenario/scenario.yaml \
  --block GL_4123 \
  --feller H1 --skidder H2 --skidder H3 \
  --processor H5 --loader H4 \
  --bunch-volume 8.0 --rate-model calibrated \
  --shift-days 5 --shifts-per-day 2 --hours-per-shift 10 \
  --truck-capacity 30.0 --truck-count 2 --truck-cycle 3600.0 \
  --landing-capacity 120.0 --skidder-capacity 40.0 \
  --out runs/gl_4123/system

"$PYTHON" -m fhops.cli.main tree scene scenario/scenario.yaml assignments.csv \
  --out runs/gl_4123/scene --lod-threshold 200 --max-log-nodes 800

mkdir -p runs/gl_4123/view
cp runs/gl_4123/scene/scene.gltf runs/gl_4123/scene/scene.glb runs/gl_4123/view/
cp runs/gl_4123/system/system_events.json runs/gl_4123/view/
cp "$VIEWER" runs/gl_4123/view/viewer.html

echo "Serve:"
echo "  cd runs/gl_4123/view && python -m http.server 8794 --bind 127.0.0.1"
echo "  http://127.0.0.1:8794/viewer.html"
