#!/usr/bin/env bash
# HOME repo setup — run after cloning or when environment resets.
# Idempotent. Safe to re-run.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

echo "🎼 ORPHEUS: Configuring HOME repo..."

# Install git hooks — two-layer: hooksPath config + direct copy to .git/hooks/
# hooksPath works when .git/config persists across sessions.
# Direct copy is the fallback for ephemeral environments where .git/config resets.
git config --local core.hooksPath .githooks 2>/dev/null && echo "  ✓ core.hooksPath = .githooks" || echo "  ⚠ core.hooksPath set failed (will use direct copy)"
for hook in pre-commit post-commit; do
    if [ -f "$REPO_ROOT/.githooks/$hook" ]; then
        cp "$REPO_ROOT/.githooks/$hook" "$REPO_ROOT/.git/hooks/$hook"
        chmod +x "$REPO_ROOT/.git/hooks/$hook"
        echo "  ✓ .git/hooks/$hook installed (direct copy)"
    fi
done

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
