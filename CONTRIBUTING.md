# Contributing to Athena Client

Thank you for considering a contribution!

### Quick Start

```bash
pip install hatch
make install
make quality   # format + lint + mypy + bandit
make test      # unit, async & property tests
```

### Pre-Push Checks

Before pushing to GitHub, run our comprehensive pre-push check script to catch issues early:

```bash
./pre-push-check.sh
```

This script runs the same checks that GitHub Actions will run:
- Installs all dependencies (including optional ones for testing)
- Runs the full test suite with coverage
- Performs security checks with Bandit
- Checks code formatting with Ruff
- Runs linting checks
- Performs type checking with MyPy

### Security Checks

We run **Bandit** on every pull request. Execute locally with:

```bash
make bandit
```

The CI build fails on any high-severity finding.
