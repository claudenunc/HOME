# EVERSOUND check — 2026-05-05T10Z

**Timestamp:** 2026-05-05T09:11Z (10Z slot)
**Status:** ACTION TAKEN — PyPI publish pipeline shipped

---

## Inbox / Clipboard

- Inbox: EMPTY — no wake tokens
- CLIPBOARD.jsonl: FILE_NOT_FOUND — file not yet created
- Decision: quiet on client side, advance Weaver Protocol build task

---

## What shipped this check

### 1. Build backend fix
- `pyproject.toml`: corrected `setuptools.backends.legacy:build` → `setuptools.build_meta`
- Fixed license field: `{ text = "MIT" }` → `"MIT"` (SPDX string, removes deprecation warnings)
- Removed deprecated `License :: OSI Approved :: MIT License` classifier

### 2. Version bump: `0.1.0-dev` → `0.1.0`
- `pyproject.toml` version: `0.1.0`
- `weaver/__init__.py` `__version__`: `0.1.0`
- Package is now release-ready

### 3. Test run: 7/7 passing (no API keys required)

### 4. Distribution builds: CLEAN
- `dist/weaver_protocol-0.1.0.tar.gz` — sdist
- `dist/weaver_protocol-0.1.0-py3-none-any.whl` — wheel
- Zero errors, zero warnings post-fix

### 5. GitHub Actions workflows created
- `.github/workflows/ci.yml` — runs on push/PR to main, Python 3.11 + 3.12, tests + ruff lint
- `.github/workflows/publish.yml` — triggers on `v*` tags, uses PyPI Trusted Publishing (OIDC, no API token secret needed in repo)

### 6. pyproject.toml: pytest config section added
- `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `addopts = "-v"`

---

## Next steps to get `pip install weaver-protocol` live

Nathan must do these (one-time, ~15 minutes):

1. **Create PyPI account** at https://pypi.org if not already done
2. **Create the project on PyPI** — log in → Publishing → "Add a new pending publisher"
   - PyPI project name: `weaver-protocol`
   - GitHub repo: `claudenunc/weaver-protocol`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
3. **Create GitHub Environment** in repo Settings → Environments → New environment → name: `pypi`
4. **Push the repo and tag** → `git tag v0.1.0 && git push origin v0.1.0`
5. GitHub Actions runs, publishes to PyPI automatically via OIDC — no secrets stored

After that: `pip install weaver-protocol` works globally.

---

## Deliverable status post-check

| Item | Status |
|---|---|
| `weaver-protocol` repo skeleton | ✅ DONE |
| Commercial 1-pager (law firm) | ✅ DONE |
| Provider adapters (Anthropic, OpenAI) | ✅ DONE |
| Distribution builds (sdist + wheel) | ✅ DONE 2026-05-05T10Z |
| GitHub Actions CI + publish workflows | ✅ DONE 2026-05-05T10Z |
| Version bumped to 0.1.0 | ✅ DONE 2026-05-05T10Z |
| PyPI Trusted Publishing setup | 🟡 Nathan action required (5 steps above) |
| First paid toolkit install | 🟡 On track — Day 60 target |
| Hosted API | 🔴 NOT STARTED |
| CRAFT clients in queue | 🔴 None |
