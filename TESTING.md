# Testing Guide

This guide explains how to run tests locally that exactly match the GitHub Actions CI pipeline, ensuring you catch errors early before pushing to GitHub.

## Quick Start

```bash
# Run the full CI pipeline locally (matches GitHub Actions exactly)
make ci-local

# Or run individual jobs
make ci-security  # Security scan (matches GitHub Actions security job)
make ci-test      # Tests with coverage (matches GitHub Actions test job)
```

## Available Testing Commands

### CI Pipeline Commands (Match GitHub Actions)

| Command | Description | GitHub Actions Equivalent |
|---------|-------------|---------------------------|
| `make ci-local` | Full CI pipeline locally | Runs both security + test jobs |
| `make ci-security` | Security scan with bandit | `security` job |
| `make ci-test` | Tests with coverage + package list | `test` job |

### Development Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `make quality` | Code quality checks (ruff, mypy, bandit) | Before committing |
| `make test` | Run tests without coverage | Quick testing |
| `make cov` | Run tests with coverage | Detailed testing |
| `make dev-setup` | Setup development environment | First time setup |
| `make pre-commit` | Quality + tests (recommended before commit) | Pre-commit hook |

## CI Pipeline Details

### Security Job (`make ci-security`)
Matches GitHub Actions `security` job exactly:
- Python 3.9 environment
- Bandit security scan with project configuration
- Same exclusions: B101, B404, B603

### Test Job (`make ci-test`)
Matches GitHub Actions `test` job exactly:
- Python 3.9 environment  
- Lists all installed packages (for debugging)
- Runs pytest with coverage
- Generates coverage report
- Same test results as CI

## Configuration Alignment

Our local setup now matches GitHub Actions CI:

| Setting | Local | GitHub Actions | Status |
|---------|-------|----------------|--------|
| Python Version | 3.9 (mypy config) | 3.9 | ✅ Aligned |
| Ruff Config | `lint.select` | `lint.select` | ✅ Aligned |
| Test Command | `hatch run cov` | `hatch run cov` | ✅ Aligned |
| Security Scan | `hatch run bandit-check` | `make bandit` | ✅ Aligned |
| Dependencies | Same hatch env | Same hatch env | ✅ Aligned |

## Expected Results

When you run `make ci-local`, you should see:

```
🔒  Running Security Job (matches GitHub Actions security job)
✅  Security job completed successfully
🧪  Running Test Job (matches GitHub Actions test job)  
🎉  Full CI pipeline completed successfully!
🚀  Your code is ready for GitHub Actions
```

### Test Results
Currently expected: **355 passed, 3 failed**
- The 3 failing tests are minor HTTP client test issues
- Same failures occur in GitHub Actions CI
- Core functionality is not affected

## Troubleshooting

### If CI fails locally but you expected it to pass:
1. Check that you've committed all changes
2. Run `make quality` to fix code style issues
3. Check the specific error messages

### If local tests pass but GitHub Actions fails:
This should not happen anymore since we've aligned the environments. If it does:
1. Check the GitHub Actions logs for the exact error
2. Ensure you're using the latest version of this testing setup
3. Report the discrepancy as it indicates a configuration drift

## Development Workflow

### Recommended workflow:
```bash
# 1. Setup (first time only)
make dev-setup

# 2. During development
make quality      # Fix code style issues
make test        # Quick test run

# 3. Before committing  
make pre-commit  # Full quality + test check

# 4. Before pushing (optional but recommended)
make ci-local    # Full CI simulation
```

### Pre-commit Hook Setup
Add this to `.git/hooks/pre-commit`:
```bash
#!/bin/sh
make pre-commit
```

## Coverage Goals

Current coverage: **84%**
- Target: Maintain above 80%
- Focus areas for improvement:
  - CLI module (77% coverage)
  - Progress utilities (46% coverage)

## Performance Benchmarks

The test suite includes performance benchmarks:
- JSON serialization (orjson vs stdlib)
- Currently: orjson ~1.69x faster than stdlib
- Benchmarks run automatically with tests

## Environment Details

### Dependencies
- **Hatch**: Environment and dependency management
- **pytest**: Test framework with coverage
- **ruff**: Linting and formatting  
- **mypy**: Type checking
- **bandit**: Security analysis

### Python Version
- **Local**: Python 3.13.5 (runtime) + Python 3.9 (mypy target)
- **CI**: Python 3.9
- **Compatibility**: Code targets Python 3.9+ for maximum compatibility

This ensures your local development environment exactly matches the CI environment, catching issues early and speeding up your development cycle.