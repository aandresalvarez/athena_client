.PHONY: help install quality test cov bandit cyclonedx

help:
	@echo "Commands:"
	@echo "  install    - create env & deps"
	@echo "  quality    - ruff, mypy, bandit"
	@echo "  test       - pytest"
	@echo "  cov        - pytest with coverage"

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
	bandit -c pyproject.toml -r athena_client -s B101,B404,B603

cyclonedx:
	@echo "📦  Generating CycloneDX SBOM..."
	@hatch run cyclonedx-bom --format json --output sbom.json
