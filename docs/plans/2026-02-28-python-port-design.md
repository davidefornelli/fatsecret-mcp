# Python Port Design (Option A)

Date: 2026-02-28
Project: `mcp-fatsecret-py`

## Goals

- Port the current TypeScript MCP server to Python.
- Use FastMCP v3 as the Python MCP framework.
- Standardize on Python 3.11 for the Python codebase.
- Preserve a safe and incremental migration path.

## Repository Architecture

Use a split monorepo layout:

- Keep top-level shared project metadata (`README.md`, `LICENSE`, `.gitignore`, `.cursor/`).
- Move existing TypeScript implementation into `javascript/`.
- Create a dedicated Python port in `python/`.

Planned structure:

```text
.
├── .cursor/
├── docs/
│   └── plans/
├── javascript/
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── python/
│   ├── pyproject.toml
│   ├── README.md
│   ├── src/
│   │   └── fatsecret_mcp/
│   └── tests/
├── README.md
└── LICENSE
```

## Cursor Rules

Create project-wide rules in `.cursor/rules/` with `alwaysApply: true`:

1. Context7 documentation usage:
   - Always use Context7 to look up library/framework docs before implementation details.
2. Python target standards:
   - Python version is 3.11 for this port.
   - Prefer typed Python and `pytest` for tests.
3. MCP framework standard:
   - Use FastMCP v3 for Python MCP implementation.

## Porting Scope

### Phase 1 (this change set)

- Add persistent Cursor rules for migration standards.
- Reorganize repository layout (`javascript/` + `python/`).
- Scaffold Python project for FastMCP v3 and Python 3.11.

### Phase 2 (next iterations)

Port server features by domain while keeping behavior parity:

- Authentication and credential management tools.
- Food search/detail tools.
- Recipe search/detail tools.
- User diary/profile tools.

## Data Flow and Behavior Parity

- Keep existing MCP tool contract intent during migration.
- Maintain equivalent input validation and response shaping where feasible.
- Preserve OAuth and API interaction behavior while adapting implementation to Python idioms.

## Error Handling Strategy

- Define domain exceptions (config, auth, validation, API/network).
- Convert internal exceptions to clear MCP tool-level error messages.
- Ensure invalid user input produces actionable errors.

## Testing Strategy

- Unit tests for core utility logic (date conversion, signing helpers, parsing/mapping).
- Tool-level tests for validation and response contracts.
- Smoke test for FastMCP server startup and tool registration.

## Risks and Mitigations

- Risk: behavior drift during translation.
  - Mitigation: migrate in tool groups and compare request/response semantics.
- Risk: mixed-language repo confusion.
  - Mitigation: clear folder boundaries and per-runtime READMEs.
- Risk: dependency mismatch in Python ecosystem.
  - Mitigation: document FastMCP v3 and pin minimum Python at 3.11.

## Acceptance Criteria

- Design approved.
- Design documented under `docs/plans/`.
- Implementation plan generated from this design before code migration work begins.
