# Python Port (Option A) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split the repository into `javascript/` and `python/`, add Cursor rules for migration standards, and scaffold a Python 3.11 FastMCP v3 project as the base for the full port.

**Architecture:** Keep the existing TypeScript code intact but relocate it under `javascript/` to preserve history and behavior while creating an isolated Python project under `python/`. Introduce project-wide Cursor rules to enforce documentation lookup via Context7 and Python migration constraints before deeper feature-porting work.

**Tech Stack:** TypeScript (existing), Python 3.11, FastMCP v3, pytest, Cursor rules (`.cursor/rules/*.mdc`)

---

### Task 1: Create Project-Wide Cursor Rules

**Files:**
- Create: `.cursor/rules/context7-documentation-first.mdc`
- Create: `.cursor/rules/python-port-standards.mdc`
- Create: `.cursor/rules/python-mcp-framework.mdc`
- Test: N/A (manual file validation)

**Step 1: Write the failing check**

Run: `ls .cursor/rules`
Expected: directory missing or rule files missing.

**Step 2: Create rule files with frontmatter**

Add three `.mdc` files using:
- `alwaysApply: true`
- concise descriptions
- direct instructions:
  - require Context7 for docs lookup
  - require Python 3.11
  - require FastMCP v3 for Python MCP server work

**Step 3: Verify files exist and are readable**

Run: `ls .cursor/rules`
Expected: all three `.mdc` files listed.

**Step 4: Validate frontmatter shape**

Run: `rg "alwaysApply: true|description:" .cursor/rules/*.mdc`
Expected: each rule file contains valid `description` and `alwaysApply: true`.

**Step 5: Commit**

```bash
git add .cursor/rules
git commit -m "chore: add cursor rules for python port standards"
```

### Task 2: Move Existing TypeScript Project to `javascript/`

**Files:**
- Create: `javascript/` (directory)
- Modify: move `src/`, `package.json`, `tsconfig.json`, and JS test utilities into `javascript/`
- Modify: update any path-sensitive scripts/docs that reference old root layout
- Test: `javascript` build and startup commands

**Step 1: Write the failing check**

Run: `ls javascript`
Expected: path does not exist.

**Step 2: Move TypeScript project files**

Move:
- `src/` -> `javascript/src/`
- `package.json` -> `javascript/package.json`
- `tsconfig.json` -> `javascript/tsconfig.json`
- `test-*.js` -> `javascript/`

Keep top-level docs/license shared in root.

**Step 3: Verify moved structure**

Run: `ls javascript`
Expected: `src`, `package.json`, `tsconfig.json`, test files.

**Step 4: Run TypeScript project sanity checks**

Run:
- `npm install` (in `javascript/`)
- `npm run build` (in `javascript/`)

Expected: build succeeds and emits `javascript/dist/`.

**Step 5: Commit**

```bash
git add javascript
git commit -m "refactor: relocate typescript server into javascript folder"
```

### Task 3: Scaffold Python 3.11 FastMCP v3 Project

**Files:**
- Create: `python/pyproject.toml`
- Create: `python/README.md`
- Create: `python/src/fatsecret_mcp/__init__.py`
- Create: `python/src/fatsecret_mcp/server.py`
- Create: `python/tests/test_server_smoke.py`
- Test: `python -m pytest -q` in `python/`

**Step 1: Write the failing test**

Create `python/tests/test_server_smoke.py`:

```python
from fatsecret_mcp.server import create_server


def test_create_server_returns_instance():
    server = create_server()
    assert server is not None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q python/tests/test_server_smoke.py`
Expected: FAIL due to missing module/project scaffolding.

**Step 3: Write minimal implementation**

Create `python/src/fatsecret_mcp/server.py` with minimal FastMCP v3 server factory:

```python
from fastmcp import FastMCP


def create_server() -> FastMCP:
    return FastMCP(name="fatsecret")
```

Add package init and `pyproject.toml` with:
- `requires-python = ">=3.11,<3.12"` (or `>=3.11`)
- dependency on FastMCP v3
- test dependency on pytest

**Step 4: Run test to verify it passes**

Run:
- `python -m pip install -e "python[dev]"`
- `python -m pytest -q python/tests/test_server_smoke.py`

Expected: PASS.

**Step 5: Commit**

```bash
git add python
git commit -m "feat: scaffold python 3.11 fastmcp v3 project"
```

### Task 4: Update Root Documentation for Dual-Project Layout

**Files:**
- Modify: `README.md`
- Test: manual docs review

**Step 1: Write the failing check**

Run: `rg "src/|npm run build|Project Structure" README.md`
Expected: references old single-root TypeScript layout.

**Step 2: Update README sections**

Update docs to:
- explain split layout (`javascript/` and `python/`)
- keep TS usage instructions under `javascript/`
- add Python 3.11 + FastMCP v3 setup instructions under `python/`
- clarify that Python port is phased and initially scaffolded

**Step 3: Verify docs consistency**

Run: `rg "javascript/|python/|FastMCP|3.11" README.md`
Expected: all terms present and coherent.

**Step 4: Optional lint/check**

Run: markdown lint if configured, otherwise manual review.
Expected: no obvious formatting issues.

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: describe javascript and python project layout"
```

### Task 5: Final Verification and Integration Commit

**Files:**
- Modify: any touched files from prior tasks
- Test: repo-level sanity checks

**Step 1: Run integrated checks**

Run:
- `git status --short`
- `npm run build` in `javascript/`
- `python -m pytest -q` in `python/`

Expected: build/test pass and intended files changed only.

**Step 2: Review diff before final commit**

Run: `git diff --stat` and `git diff`
Expected: only intended migration and scaffold changes.

**Step 3: Create final integration commit (if using squash workflow)**

```bash
git add .
git commit -m "feat: initialize python port and split javascript project layout"
```

**Step 4: Verify clean state**

Run: `git status`
Expected: clean working tree.
