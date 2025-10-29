# Repository Guidelines

## Project Structure & Module Organization
- Source code: `athena_client/` (e.g., `client.py`, `async_client.py`, `http.py`, `auth.py`, `cli.py`, `models/`, `utils/`)
- Tests: `tests/` (unit, async, property tests). Name files `test_*.py`.
- Examples: `examples/`
- Config & tooling: `pyproject.toml`, `Makefile`, `.github/workflows/`

## Build, Test, and Development Commands
- `make install` — create the Hatch env and install dev deps.
- `make quality` — format (ruff), lint, type-check (mypy), bandit.
- `make test` — run pytest.
- `make cov` — pytest with coverage report.
- `make ci-local` — run security + tests to mirror CI.
- `make bandit` — Bandit security scan.
Examples: `pytest -k concept_set`, `hatch run mypy athena_client`.

## Coding Style & Naming Conventions
- Python 3.9+; 4-space indent; max line length 88.
- Use type hints everywhere (mypy strict). No untyped defs.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Imports sorted/organized by Ruff (I). Avoid wildcard imports.
- Format with Ruff: `make quality` (or `ruff format athena_client tests`).

## Testing Guidelines
- Frameworks: pytest, pytest-asyncio, Hypothesis. Keep coverage ≥ 80% (`make cov`).
- Place tests under `tests/`; name tests `test_*` and functions `test_*`.
- Mock external I/O and HTTP. Prefer fixtures in `tests/conftest.py`.
- Property tests live in `tests/property/`; benchmarks in `tests/benchmarks/`.

## Commit & Pull Request Guidelines
- Prefer Conventional Commits when possible: `feat(http): add retry jitter`, `fix(cli): correct option parsing`.
- Keep messages imperative and scoped; small commits > large dumps.
- PRs must include: clear description, linked issues (`Fixes #123`), tests, and updated docs where relevant.
- Run `make pre-commit` or `./pre-push-check.sh` before pushing; ensure `make ci-local` passes.

## Security & Configuration Tips
- Configuration via `athena_client/settings.py` using env vars (e.g., `ATHENA_TOKEN`, `ATHENA_BASE_URL`). Use `get_settings()`; do not read `os.environ` directly.
- Never commit secrets or `.env`. Validate with `make bandit`. SBOM: `make cyclonedx`.

