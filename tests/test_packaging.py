"""
Packaging and build system tests for athena-client.

These tests ensure that the package configuration is correct and prevent
regressions in dependency declarations, particularly for tools like pipx.
"""

import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        pytest.skip("tomli not available", allow_module_level=True)


@pytest.fixture
def pyproject_data():
    """Load and parse pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def test_build_system_uses_hatchling(pyproject_data):
    """
    Test that the build system uses hatchling.

    Regression test for pipx installation issue where setuptools backend
    caused dependencies to not be installed properly.
    """
    build_system = pyproject_data.get("build-system", {})

    # Check that hatchling is the build backend
    assert build_system.get("build-backend") == "hatchling.build", (
        "Build backend should be 'hatchling.build' to ensure proper "
        "dependency resolution with pipx and other installers"
    )

    # Check that hatchling is in requirements
    requires = build_system.get("requires", [])
    assert "hatchling" in requires, "hatchling must be in build-system.requires"

    # Ensure we're not mixing build systems
    assert "setuptools" not in " ".join(requires).lower(), (
        "Should not have setuptools in build requirements when using hatchling"
    )


def test_core_dependencies_declared(pyproject_data):
    """
    Test that all core dependencies are properly declared.

    Ensures that dependencies like requests, httpx, etc. are present
    so they get installed by pipx and other tools.
    """
    dependencies = pyproject_data.get("project", {}).get("dependencies", [])

    # Core dependencies that must be present
    required_deps = [
        "requests",  # Critical: regression test for pipx issue
        "httpx",
        "orjson",
        "pydantic",
        "pydantic-settings",
        "backoff",
        "click",
        "rich",
    ]

    for dep in required_deps:
        # Check if dependency is in the list (may have version specifiers)
        found = any(dep in d.lower() for d in dependencies)
        assert found, (
            f"Missing required dependency '{dep}' in project.dependencies. "
            f"This can cause ModuleNotFoundError when installing via pipx."
        )


def test_requests_dependency_present(pyproject_data):
    """
    Specific regression test for the requests dependency.

    This is the dependency that was missing in the pipx installation
    reported by vojtech_huser.
    """
    dependencies = pyproject_data.get("project", {}).get("dependencies", [])

    # Check specifically for requests with version constraint
    requests_found = any("requests" in d.lower() for d in dependencies)
    assert requests_found, (
        "requests dependency is missing! This will cause "
        "'ModuleNotFoundError: No module named requests' when installed via pipx"
    )

    # Find the actual requests entry
    requests_dep = next((d for d in dependencies if "requests" in d.lower()), None)
    assert requests_dep is not None

    # Verify it has a version constraint
    assert ">=" in requests_dep, (
        f"requests dependency should have version constraint, got: {requests_dep}"
    )


def test_cli_dependencies_in_main_dependencies(pyproject_data):
    """
    Test that CLI dependencies (click, rich) are in main dependencies.

    This ensures the CLI works out of the box without requiring extras.
    """
    dependencies = pyproject_data.get("project", {}).get("dependencies", [])

    # CLI dependencies should be in main dependencies, not just in [cli] extra
    assert any("click" in d.lower() for d in dependencies), (
        "click should be in main dependencies for CLI to work"
    )
    assert any("rich" in d.lower() for d in dependencies), (
        "rich should be in main dependencies for CLI to work"
    )


def test_project_scripts_defined(pyproject_data):
    """Test that CLI entry points are properly defined."""
    scripts = pyproject_data.get("project", {}).get("scripts", {})

    assert "athena" in scripts, "athena CLI script not defined"
    assert "athena-client" in scripts, "athena-client CLI script not defined"

    # Verify they point to the right module
    assert scripts["athena"] == "athena_client.cli:main"
    assert scripts["athena-client"] == "athena_client.cli:main"


def test_no_setuptools_configuration(pyproject_data):
    """
    Test that there's no leftover setuptools configuration.

    Regression test: mixing setuptools and hatchling configs can cause issues.
    """
    tool = pyproject_data.get("tool", {})

    assert "setuptools" not in tool, (
        "Found [tool.setuptools] configuration while using hatchling backend. "
        "This mixing of build systems can cause dependency resolution issues."
    )


def test_hatchling_wheel_config(pyproject_data):
    """Test that hatchling wheel configuration is present and correct."""
    tool_hatch = pyproject_data.get("tool", {}).get("hatch", {})
    build_targets = tool_hatch.get("build", {}).get("targets", {})
    wheel_config = build_targets.get("wheel", {})

    # Should have packages configuration
    assert "packages" in wheel_config, (
        "hatchling wheel target should specify packages to include"
    )

    # Should include athena_client
    packages = wheel_config["packages"]
    assert "athena_client" in packages, "athena_client should be in wheel packages"


def test_python_version_constraint(pyproject_data):
    """Test that Python version constraint is reasonable."""
    requires_python = pyproject_data.get("project", {}).get("requires-python", "")

    assert requires_python, "requires-python should be specified"
    assert ">=3.9" in requires_python, "Should support Python 3.9 and above"


def test_version_format(pyproject_data):
    """Test that version is in correct format."""
    version = pyproject_data.get("project", {}).get("version", "")

    assert version, "version should be specified"

    # Should be semantic versioning format
    parts = version.split(".")
    assert len(parts) == 3, f"Version should be in format X.Y.Z, got: {version}"

    # All parts should be numeric
    for part in parts:
        assert part.isdigit(), f"Version parts should be numeric, got: {version}"


def test_optional_dependencies_structure(pyproject_data):
    """Test that optional dependencies are properly structured."""
    optional_deps = pyproject_data.get("project", {}).get("optional-dependencies", {})

    # Should have common optional groups
    expected_groups = ["core", "async", "pandas", "cli", "db", "dev"]

    for group in expected_groups:
        assert group in optional_deps, (
            f"Optional dependency group '{group}' should be defined"
        )


def test_no_dependency_duplication(pyproject_data):
    """
    Test that dependencies aren't duplicated between main and optional.

    Core dependencies should be in main dependencies, not just in optionals.
    """
    main_deps = pyproject_data.get("project", {}).get("dependencies", [])

    # Extract package names from main dependencies (without version specifiers)
    main_packages = {
        d.split(">=")[0].split("==")[0].split("[")[0].strip().lower() for d in main_deps
    }

    # Core packages that should be in main, not relegated to optionals
    core_packages = {"requests", "httpx", "orjson", "pydantic", "backoff"}

    for pkg in core_packages:
        assert pkg in main_packages, (
            f"Core package '{pkg}' should be in main dependencies, "
            f"not just in optional groups"
        )


def test_version_consistency(pyproject_data):
    """
    Test that version in __init__.py matches pyproject.toml.

    Regression test: versions can get out of sync during releases,
    causing runtime version to differ from package version.
    """
    from athena_client import __version__

    pyproject_version = pyproject_data.get("project", {}).get("version", "")

    assert __version__ == pyproject_version, (
        f"Version mismatch: __init__.py has {__version__} "
        f"but pyproject.toml has {pyproject_version}"
    )


def test_py_typed_marker_exists():
    """
    Test that py.typed marker file exists.

    This file is required for type checkers to recognize the package
    as typed and provide type hints to users.
    """
    py_typed_path = Path(__file__).parent.parent / "athena_client" / "py.typed"

    assert py_typed_path.exists(), (
        "py.typed marker file is missing. This file is required for "
        "type checkers (mypy, pyright) to recognize the package as typed. "
        "Create an empty file at athena_client/py.typed"
    )


def test_py_typed_included_in_wheel(pyproject_data):
    """
    Test that py.typed is configured to be included in the wheel.

    Without proper configuration, py.typed won't be included in the
    distributed package even if it exists in the source.
    """
    tool_hatch = pyproject_data.get("tool", {}).get("hatch", {})
    build_config = tool_hatch.get("build", {})

    # Check for py.typed in wheel targets or force-include
    wheel_targets = build_config.get("targets", {}).get("wheel", {})

    # Either in force-include or packages should include it
    has_force_include = "force-include" in wheel_targets

    # If using force-include, py.typed should be there
    if has_force_include:
        force_include = wheel_targets.get("force-include", {})
        py_typed_included = any("py.typed" in key for key in force_include.keys())
        assert py_typed_included, (
            "py.typed should be in wheel force-include configuration"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
