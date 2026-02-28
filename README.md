# FatSecret MCP Server

This repository is organized as a dual-project migration:

- `javascript/`: current TypeScript MCP implementation (existing production logic)
- `python/`: Python 3.11 port scaffold using FastMCP v3

The migration is incremental. TypeScript remains the source of full feature behavior while Python is being ported.

## Repository Layout

```text
mcp-fatsecret-py/
├── .cursor/
│   └── rules/
├── docs/
│   └── plans/
├── javascript/
│   ├── src/
│   ├── utils/
│   ├── package.json
│   └── tsconfig.json
├── python/
│   ├── pyproject.toml
│   ├── src/fatsecret_mcp/
│   └── tests/
├── README.md
└── LICENSE
```

## JavaScript Project (`javascript/`)

Use this project for the current complete MCP server behavior.

### Prerequisites

- Node.js (v14+)
- npm
- FatSecret developer credentials

### Build and run

```bash
cd javascript
npm install
npm run build
npm start
```

### Useful scripts

```bash
cd javascript
npm run dev
node utils/test-interactive.js
node utils/test-date-conversion.js
node utils/test-mcp.js | node dist/index.js
```

## Python Project (`python/`)

This is the new port target:

- Python `3.11`
- FastMCP `v3`
- `pytest` for tests

### Quick start

```bash
cd python
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q
```

Current status: initial scaffold is in place and smoke tests are set up for server creation.

## Migration Guidance

- Keep behavior parity between TypeScript and Python as tools are ported.
- Port tools in batches (auth, foods, recipes, user diary) to reduce risk.
- Keep root-level docs and planning artifacts shared across both implementations.

## License

MIT License - see `LICENSE` for details.
