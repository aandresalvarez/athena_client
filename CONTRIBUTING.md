# Contributing to Athena Client

Thank you for considering a contribution!

### Quick Start

```bash
pip install hatch
make install
make quality   # format + lint + mypy + bandit
make test      # unit, async & property tests
```

### Security Checks

We run **Bandit** on every pull request. Execute locally with:

```bash
make bandit
```

The CI build fails on any high-severity finding.
