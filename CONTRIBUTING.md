# Contributing

Issues and pull requests are welcome.

## Development setup

Backend (Python 3.12+):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
python -m pytest
```

Frontend (Node 22+):

```bash
cd frontend
npm ci
npm run lint
npm run build
```

Both checks run in CI on every push and pull request. The frontend currently has no automated tests; changes to it should be verified in the browser against a running backend.

## Pull requests

- Branch from `main`, keep the change focused, and describe what it does and why.
- Add or update backend tests for behaviour changes. Tests must not touch the network; frozen element sets live in `backend/tests/fixtures.py`.
- Keep the README accurate. If you change what the EO analysis computes, update the "How the EO analysis works" section.

## Style

- Python: `ruff` (configuration in `backend/pyproject.toml`), type hints on public functions, docstrings where the behaviour is not obvious from the name.
- TypeScript: strict mode, no `any`, ESLint clean.
- Commit messages: short imperative summary, body only when the why is not obvious.
