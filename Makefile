.PHONY: help install quality test cov bandit cyclonedx release bump-version ci-local ci-security ci-test dev-setup pre-commit

help:
	@echo "Commands:"
	@echo "  install      - create env & deps"
	@echo "  quality      - ruff, mypy, bandit"
	@echo "  test         - pytest"
	@echo "  cov          - pytest with coverage"
	@echo "  ci-local     - run full CI pipeline locally (matches GitHub Actions)"
	@echo "  ci-security  - run security checks (matches GitHub Actions security job)"
	@echo "  ci-test      - run tests with coverage (matches GitHub Actions test job)"
	@echo "  dev-setup    - setup development environment"
	@echo "  pre-commit   - run pre-commit checks"
	@echo "  release      - commit, tag, and push for GitHub Actions publishing"
	@echo "  bump-version - update version in pyproject.toml and athena_client/__init__.py"

install:
	hatch env create

quality:
	hatch run quality

test:
	hatch run test

cov:
	hatch run cov

bandit:
	@echo "🔍  Running Bandit security scan..."
	hatch run bandit-check

cyclonedx:
	@echo "📦  Generating CycloneDX SBOM..."
	@hatch run cyclonedx-py environment --of json -o sbom.json

release:
	@echo "🚀  Preparing release..."
	@echo "Current version: $(shell grep '^version =' pyproject.toml | cut -d'"' -f2)"
	@echo "Please confirm the version above is correct and you want to release it."
	@read -p "Press Enter to continue or Ctrl+C to abort..."
	@echo "📝  Adding all changes..."
	@git add .
	@echo "💾  Committing changes..."
	@git commit -m "Release version $(shell grep '^version =' pyproject.toml | cut -d'"' -f2) - Fix conditional imports and improve dependency management"
	@echo "🏷️   Creating tag v$(shell grep '^version =' pyproject.toml | cut -d'"' -f2)..."
	@git tag -a v$(shell grep '^version =' pyproject.toml | cut -d'"' -f2) -m "Release version $(shell grep '^version =' pyproject.toml | cut -d'"' -f2)"
	@echo "📤  Pushing to GitHub..."
	@git push origin main
	@git push origin v$(shell grep '^version =' pyproject.toml | cut -d'"' -f2)
	@echo "✅  Release pushed! GitHub Actions will handle the publishing."

bump-version:
	@read -p "Enter new version: " v; \
	sed -i '' "s/^version = \".*\"/version = \"$v\"/" pyproject.toml; \
	sed -i '' "s/^__version__ = \".*\"/__version__ = \"$v\"/" athena_client/__init__.py; \
	echo "Version updated to $v in pyproject.toml and athena_client/__init__.py"

# CI Pipeline Targets (match GitHub Actions exactly)
ci-security:
	@echo "🔒  Running Security Job (matches GitHub Actions security job)"
	@echo "📋  Installing dependencies..."
	@hatch env create
	@echo "🔍  Running Bandit security scan..."
	@make bandit
	@echo "✅  Security job completed successfully"

ci-test:
	@echo "🧪  Running Test Job (matches GitHub Actions test job)"
	@echo "📋  Installing dependencies..."
	@hatch env create
	@echo "📦  Listing installed packages..."
	@hatch run pip list
	@echo "🧪  Running test suite with coverage..."
	@hatch run cov
	@echo "✅  Test job completed successfully"

ci-local: ci-security ci-test
	@echo "🎉  Full CI pipeline completed successfully!"
	@echo "🚀  Your code is ready for GitHub Actions"

# Additional helper targets for development
dev-setup:
	@echo "🛠️   Setting up development environment..."
	@make install
	@echo "🔧  Running initial quality checks..."
	@make quality
	@echo "✅  Development environment ready!"

pre-commit: quality ci-test
	@echo "✅  Pre-commit checks passed! Safe to commit."