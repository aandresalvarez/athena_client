"""
Integration tests for different installation methods.

These tests verify that the package can be installed correctly via
different package managers: pip, pipx, poetry, and uv.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import pytest

# Get expected version from the package
from athena_client import __version__ as EXPECTED_VERSION


def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, and stderr.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=120,  # 2-minute timeout
    )
    return result.returncode, result.stdout, result.stderr


def is_tool_available(tool: str) -> bool:
    """Check if a command-line tool is available."""
    try:
        subprocess.run(
            [tool, "--version"],
            capture_output=True,
            timeout=10,
        )
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("CI") != "true",
    reason="Integration tests only run in CI environment",
)
class TestInstallationMethods:
    """Test different installation methods work correctly."""

    def test_pip_install_in_venv(self, tmp_path: Path):
        """Test that package can be installed via pip in a virtual environment."""
        venv_dir = tmp_path / "venv"

        # Create virtual environment
        exit_code, stdout, stderr = run_command(
            [sys.executable, "-m", "venv", str(venv_dir)]
        )
        assert exit_code == 0, f"Failed to create venv: {stderr}"

        # Get pip path in venv
        if sys.platform == "win32":
            pip_path = venv_dir / "Scripts" / "pip.exe"
            python_path = venv_dir / "Scripts" / "python.exe"
        else:
            pip_path = venv_dir / "bin" / "pip"
            python_path = venv_dir / "bin" / "python"

        # Install package
        package_dir = Path(__file__).parent.parent
        exit_code, stdout, stderr = run_command(
            [str(pip_path), "install", str(package_dir)]
        )
        assert exit_code == 0, f"Failed to install: {stderr}"

        # Verify import works
        exit_code, stdout, stderr = run_command(
            [
                str(python_path),
                "-c",
                "import athena_client; print(athena_client.__version__)",
            ]
        )
        assert exit_code == 0, f"Failed to import: {stderr}"
        assert EXPECTED_VERSION in stdout

        # Verify CLI works
        athena_cmd = (
            venv_dir / "bin" / "athena"
            if sys.platform != "win32"
            else venv_dir / "Scripts" / "athena.exe"
        )
        exit_code, stdout, stderr = run_command([str(athena_cmd), "--version"])
        assert exit_code == 0, f"CLI failed: {stderr}"
        assert EXPECTED_VERSION in stdout

    @pytest.mark.skipif(not is_tool_available("pipx"), reason="pipx not installed")
    def test_pipx_install(self, tmp_path: Path):
        """Test that package can be installed via pipx."""
        # Set PIPX_HOME to temp directory
        env = os.environ.copy()
        pipx_home = tmp_path / "pipx"
        env["PIPX_HOME"] = str(pipx_home)
        env["PIPX_BIN_DIR"] = str(pipx_home / "bin")

        package_dir = Path(__file__).parent.parent

        # Install with pipx
        result = subprocess.run(
            ["pipx", "install", str(package_dir)],
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"pipx install failed: {result.stderr}"

        # Verify CLI is available
        athena_bin = pipx_home / "bin" / "athena"
        result = subprocess.run(
            [str(athena_bin), "--version"],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"athena --version failed: {result.stderr}"
        assert EXPECTED_VERSION in result.stdout

        # Test that imports work (regression test for original pipx bug)
        result = subprocess.run(
            [
                str(athena_bin),
                "--help",
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"athena --help failed: {result.stderr}"
        assert "search" in result.stdout.lower()

    @pytest.mark.skipif(not is_tool_available("poetry"), reason="poetry not installed")
    def test_poetry_install(self, tmp_path: Path):
        """Test that package can be installed via poetry."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()

        # Create minimal pyproject.toml
        pyproject = project_dir / "pyproject.toml"
        package_dir = Path(__file__).parent.parent
        pyproject.write_text(
            f"""[tool.poetry]
name = "test-project"
version = "0.1.0"
description = "Test project"
authors = ["Test <test@example.com>"]

[tool.poetry.dependencies]
python = "^3.9"
athena-client = {{ path = "{package_dir}", develop = true }}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        )

        # Install dependencies
        exit_code, stdout, stderr = run_command(
            ["poetry", "install"],
            cwd=str(project_dir),
        )
        assert exit_code == 0, f"poetry install failed: {stderr}"

        # Verify import works
        exit_code, stdout, stderr = run_command(
            [
                "poetry",
                "run",
                "python",
                "-c",
                "import athena_client; print(athena_client.__version__)",
            ],
            cwd=str(project_dir),
        )
        assert exit_code == 0, f"Import failed: {stderr}"
        assert EXPECTED_VERSION in stdout

    @pytest.mark.skipif(not is_tool_available("uv"), reason="uv not installed")
    def test_uv_install(self, tmp_path: Path):
        """Test that package can be installed via uv."""
        venv_dir = tmp_path / "venv"

        # Create virtual environment with uv
        exit_code, stdout, stderr = run_command(["uv", "venv", str(venv_dir)])
        assert exit_code == 0, f"Failed to create venv: {stderr}"

        # Install package with uv
        package_dir = Path(__file__).parent.parent
        exit_code, stdout, stderr = run_command(
            ["uv", "pip", "install", str(package_dir)],
            cwd=str(venv_dir),
        )
        assert exit_code == 0, f"Failed to install: {stderr}"

        # Get python path in venv
        if sys.platform == "win32":
            python_path = venv_dir / "Scripts" / "python.exe"
        else:
            python_path = venv_dir / "bin" / "python"

        # Verify import works
        exit_code, stdout, stderr = run_command(
            [
                str(python_path),
                "-c",
                "import athena_client; print(athena_client.__version__)",
            ]
        )
        assert exit_code == 0, f"Failed to import: {stderr}"
        assert EXPECTED_VERSION in stdout


@pytest.mark.integration
def test_optional_dependencies_install():
    """Test that optional dependencies can be installed correctly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        venv_dir = Path(tmp_dir) / "venv"

        # Create venv
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
            capture_output=True,
        )

        pip_path = (
            venv_dir / "bin" / "pip"
            if sys.platform != "win32"
            else venv_dir / "Scripts" / "pip.exe"
        )
        python_path = (
            venv_dir / "bin" / "python"
            if sys.platform != "win32"
            else venv_dir / "Scripts" / "python.exe"
        )

        package_dir = Path(__file__).parent.parent

        # Install with pandas extra
        subprocess.run(
            [str(pip_path), "install", f"{package_dir}[pandas]"],
            check=True,
            capture_output=True,
        )

        # Verify pandas is available
        result = subprocess.run(
            [str(python_path), "-c", "import pandas; print('pandas available')"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "pandas available" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
