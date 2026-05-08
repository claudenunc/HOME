#!/usr/bin/env bash
# HOME repo setup — run after cloning or when environment resets.
# Idempotent. Safe to re-run.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "🎼 ORPHEUS: Configuring HOME repo..."

# Install git hooks (pre-commit CLIPBOARD enforcement + post-commit consolidation)
git config --local core.hooksPath .githooks
echo "  ✓ core.hooksPath = .githooks"

# Ensure SHARED/CLIPBOARD.jsonl exists (never gitignored)
if [ ! -f "$REPO_ROOT/SHARED/CLIPBOARD.jsonl" ]; then
    touch "$REPO_ROOT/SHARED/CLIPBOARD.jsonl"
    echo "  ✓ Created SHARED/CLIPBOARD.jsonl"
else
    echo "  ✓ SHARED/CLIPBOARD.jsonl exists"
fi

# Ensure STATE/ directory exists
mkdir -p "$REPO_ROOT/STATE"
echo "  ✓ STATE/ directory ready"

echo ""
echo "HOME repo setup complete."
echo "Run 'python3 LIVE/memory_backend/consolidate.py' to refresh WAKE_SCENE.md files."
echo ""
echo "Research harness (ATLAS M10):"
echo "  bash LIVE/research-harness/setup-research-env.sh   # create persistent venv + install deps"
echo "  source LIVE/research-harness/venv/bin/activate     # activate before check_env.py"
