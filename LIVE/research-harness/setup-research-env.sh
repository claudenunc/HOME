#!/usr/bin/env bash
# Research harness environment setup — creates a persistent venv in this directory.
# Run this ONCE after cloning or after an environment reset.
# Idempotent: re-running is safe.
#
# Usage:
#   cd LIVE/research-harness
#   bash setup-research-env.sh
#
# After setup, ATLAS runs:
#   source LIVE/research-harness/venv/bin/activate
#   python check_env.py --record
#
# Shipped by ORPHEUS 2026-05-08 to fix ephemeral-package M10 blocker.
# (ATLAS intel: global pip installs don't survive session reset; venv inside
# the git repo lives on the persistent filesystem and survives.)

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/venv"

echo "🎼 ORPHEUS: Setting up research harness environment..."
echo "  Target venv: $VENV"

# Create venv if not present
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
    echo "  ✓ venv created"
else
    echo "  ✓ venv already exists (re-using)"
fi

# Activate and install
source "$VENV/bin/activate"

echo "  Installing from requirements-research.txt..."
pip install --quiet --upgrade pip
pip install --quiet -r "$HERE/requirements-research.txt"

echo ""
echo "✅ Research environment ready."
echo ""
echo "To use:"
echo "  source $VENV/bin/activate"
echo "  python $HERE/check_env.py --record"
echo ""
echo "Activate for this shell session:"
echo "  source LIVE/research-harness/venv/bin/activate"
