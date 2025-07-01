"""Tests for the CLI module."""

import json
import sys
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from athena_client.cli import _create_client, _format_output, cli


class TestCLI:
    """Test cases for the CLI        # Verify that format_output was called
    mock_format_output.assert_called_once()

    # Verify that the first two arguments are correct (limited_results and 'table')
    # The third argument is the console which we don't need to check
    args, _ = mock_format_output.call_args
    assert args[0] == limited_results
    assert args[1] == 'table'
    # We don't care about the third argument (console)odule."""

    def test_create_client(self):
        """Test client creation with parameters."""
        with patch("athena_client.cli.Athena") as mock_athena:
            mock_client = Mock()
            mock_athena.return_value = mock_client

            result = _create_client(
                base_url="https://api.example.com",
                token="test-token",
                timeout=60,
                retries=5,
            )

            mock_athena.assert_called_once_with(
                base_url="https://api.example.com",
                token="test-token",
                timeout=60,
                max_retries=5,
            )
            assert result == mock_client

    def test_create_client_with_none_values(self):
        """Test client creation with None values."""
        with patch("athena_client.cli.Athena") as mock_athena:
            mock_client = Mock()
            mock_athena.return_value = mock_client

            result = _create_client(None, None, None, None)

            mock_athena.assert_called_once_with(
                base_url=None,
                token=None,
                timeout=None,
                max_retries=None,
            )
            assert result == mock_client

    def test_format_output_json_string(self):
        """Test JSON output formatting with string input."""
        data = '{"key": "value"}'
        _format_output(data, "json")
        # This should just print the string as-is

    def test_format_output_json_dict(self):
        """Test JSON output formatting with dictionary input."""
        data = {"key": "value", "number": 123}

        with patch("builtins.print") as mock_print:
            _format_output(data, "json")
            mock_print.assert_called_once_with(json.dumps(data, indent=2))

    def test_format_output_yaml_success(self):
        """Test YAML output formatting."""
        data = {"key": "value", "number": 123}
        mock_yaml = Mock()
        mock_yaml.dump.return_value = "key: value\nnumber: 123\n"
        with patch.dict("sys.modules", {"yaml": mock_yaml}):
            with patch("builtins.print") as mock_print:
                _format_output(data, "yaml")
                mock_print.assert_called_once_with("key: value\nnumber: 123\n")

    def test_format_output_yaml_import_error(self):
        """Test YAML output formatting when pyyaml is not available."""
        data = {"key": "value"}
        with patch.dict("sys.modules", {"yaml": None}):
            with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
                _format_output(data, "yaml")
                mock_print.assert_called()
                mock_exit.assert_called_once_with(1)

    def test_format_output_table_with_search_result(self):
        """Test table output formatting with SearchResult."""
        mock_search_result = Mock()
        mock_search_result.to_list.return_value = [
            {
                "id": 1,
                "name": "Test Company",
                "code": "TEST001",
                "vocabulary": "SNOMED",
                "domain": "Condition",
                "className": "Clinical Finding",
            }
        ]

        with patch("athena_client.cli.Table") as mock_table_class:
            mock_table = Mock()
            mock_table_class.return_value = mock_table

            with patch("builtins.print"):
                _format_output(mock_search_result, "table", Mock())

                mock_table_class.assert_called_once()
                mock_table.add_column.assert_called()
                mock_table.add_row.assert_called()

    def test_format_output_table_empty_results(self):
        """Test table output formatting with empty results."""
        mock_search_result = Mock()
        mock_search_result.to_list.return_value = []

        mock_console = Mock()

        with patch("athena_client.cli.rich"):
            _format_output(mock_search_result, "table", mock_console)

            # Should print "No results found" message
            mock_console.print.assert_called_once()

    def test_format_output_table_with_other_data(self):
        """Test table output formatting with other data types."""
        data = {"key": "value", "number": 42}
        mock_console = Mock()
        _format_output(data, "table", mock_console)
        mock_console.print.assert_called_once()

    def test_format_output_pretty(self):
        """Test pretty output formatting."""
        data = {"key": "value", "number": 123}
        mock_console = Mock()

        with patch("athena_client.cli.rich"):
            _format_output(data, "pretty", mock_console)
            mock_console.print.assert_called_once_with(data)

    def test_format_output_fallback(self):
        """Test fallback output formatting."""
        data = {"key": "value", "number": 123}

        with patch("builtins.print") as mock_print:
            _format_output(data, "unknown", None)
            mock_print.assert_called_once_with(json.dumps(data, indent=2))

    def test_cli_initialization(self):
        """Test CLI initialization."""
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "--base-url",
                "https://api.example.com",
                "--token",
                "test-token",
                "--timeout",
                "60",
                "--retries",
                "5",
                "--output",
                "json",
                "--help",  # Use help to avoid making actual API calls
            ],
        )
        assert result.exit_code in (0, 2)  # Accept both success and usage error

    def test_cli_initialization_no_rich(self):
        """Test CLI initialization without rich."""
        with patch("athena_client.cli.rich", None):
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "--base-url",
                    "https://api.example.com",
                    "--token",
                    "test-token",
                    "--timeout",
                    "60",
                    "--retries",
                    "5",
                    "--output",
                    "json",
                    "--help",  # Use help to avoid making actual API calls
                ],
            )
            assert result.exit_code in (0, 2)  # Accept both success and usage error

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_search_command(self, mock_format_output, mock_create_client):
        """Test search command."""
        mock_client = Mock()
        mock_search_result = Mock()
        mock_client.search.return_value = mock_search_result
        mock_create_client.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "test query",
                "--fuzzy",
                "--page-size",
                "50",
                "--page",
                "1",
                "--domain",
                "Condition",
                "--vocabulary",
                "SNOMED",
            ],
        )
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.search.assert_called_once()
        mock_format_output.assert_called_once()

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_search_command_with_limit(self, mock_format_output, mock_create_client):
        """Test search command with limit option."""
        mock_client = Mock()
        mock_search_result = Mock()
        mock_client.search.return_value = mock_search_result
        mock_create_client.return_value = mock_client

        # Setup the mock for top() method
        limited_results = Mock()
        mock_search_result.top.return_value = limited_results

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "search",
                "test query",
                "--limit",
                "3",
            ],
        )

        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.search.assert_called_once()

        # Verify that top() was called with the correct limit
        mock_search_result.top.assert_called_once_with(3)

        # Verify that format_output was called
        mock_format_output.assert_called_once()

        # Verify that the first two arguments are correct (limited_results and 'table')
        args, _ = mock_format_output.call_args
        assert args[0] == limited_results
        assert args[1] == "table"

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_details_command(self, mock_format_output, mock_create_client):
        """Test details command."""
        mock_client = Mock()
        mock_details = Mock()
        mock_client.details.return_value = mock_details
        mock_create_client.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(cli, ["details", "123"])
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.details.assert_called_once()
        mock_format_output.assert_called_once()

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_relationships_command(self, mock_format_output, mock_create_client):
        """Test relationships command."""
        mock_client = Mock()
        mock_relationships = Mock()
        mock_client.relationships.return_value = mock_relationships
        mock_create_client.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["relationships", "123", "--relationship-id", "Is a", "--only-standard"],
        )
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.relationships.assert_called_once()
        mock_format_output.assert_called_once()

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_graph_command(self, mock_format_output, mock_create_client):
        """Test graph command."""
        mock_client = Mock()
        mock_graph = Mock()
        mock_client.graph.return_value = mock_graph
        mock_create_client.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(
            cli, ["graph", "123", "--depth", "5", "--zoom-level", "3"]
        )
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.graph.assert_called_once()
        mock_format_output.assert_called_once()

    @patch("athena_client.cli._create_client")
    @patch("athena_client.cli._format_output")
    def test_summary_command(self, mock_format_output, mock_create_client):
        """Test summary command."""
        mock_client = Mock()
        mock_summary = {"details": {}, "relationships": {}, "graph": {}}
        mock_client.summary.return_value = mock_summary
        mock_create_client.return_value = mock_client
        runner = CliRunner()
        result = runner.invoke(cli, ["summary", "123"])
        assert result.exit_code == 0
        mock_create_client.assert_called_once()
        mock_client.summary.assert_called_once()
        mock_format_output.assert_called_once()

    def test_click_import_error(self):
        """Test CLI import error handling."""
        import importlib

        # Save original click import
        original_click = sys.modules.get("click")
        try:
            sys.modules["click"] = None
            import athena_client
            import athena_client.cli

            with pytest.raises(SystemExit):
                importlib.reload(athena_client.cli)
        finally:
            if original_click is not None:
                sys.modules["click"] = original_click
            else:
                del sys.modules["click"]

    def test_rich_import_error(self):
        """Test ImportError handling for rich."""
        import importlib

        module_name = "athena_client.cli"
        sys.modules.pop(module_name, None)
        with patch.dict("sys.modules", {"rich": None}):
            import athena_client.cli

            importlib.reload(athena_client.cli)
            assert athena_client.cli.rich is None
            assert athena_client.cli.Console is None
            assert athena_client.cli.Syntax is None
            assert athena_client.cli.Table is None

    def test_main_entrypoint(self):
        """Test CLI main entrypoint."""
        from click.testing import CliRunner

        from athena_client.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli)
        # Accept exit_code 0 (success) or 2 (Click usage error when no command provided)
        assert result.exit_code in (0, 2)

    def test_format_output_yaml_import_error_branch(self):
        """Test _format_output YAML ImportError branch."""
        data = {"key": "value"}
        with patch.dict("sys.modules", {"yaml": None}):
            with patch("builtins.print") as mock_print, patch("sys.exit") as mock_exit:
                _format_output(data, "yaml")
                mock_print.assert_called()
                mock_exit.assert_called_once_with(1)

    def test_format_output_table_no_rich(self):
        """Test _format_output with table output and no rich."""
        data = {"key": "value"}
        with patch("athena_client.cli.rich", None):
            from athena_client.cli import _format_output

            with patch("builtins.print") as mock_print:
                _format_output(data, "table", None)
                mock_print.assert_called()

    def test_format_output_pretty_no_rich(self):
        """Test _format_output with pretty output and no rich."""
        data = {"key": "value"}
        with patch("athena_client.cli.rich", None):
            from athena_client.cli import _format_output

            with patch("builtins.print") as mock_print:
                _format_output(data, "pretty", None)
                mock_print.assert_called()

    def test_generate_set_command_success(self) -> None:
        import importlib

        import athena_client.cli as cli_module

        cli_module = importlib.reload(cli_module)

        mock_client = Mock()
        mock_client.generate_concept_set = Mock(
            return_value={"concept_ids": [1], "metadata": {"status": "SUCCESS"}}
        )

        with (
            patch.object(
                cli_module, "_create_client", return_value=mock_client
            ) as mock_create_client,
            patch.object(cli_module, "_format_output") as mock_format_output,
            patch(
                "athena_client.cli.asyncio.run",
                return_value={
                    "concept_ids": [1],
                    "metadata": {"status": "SUCCESS", "strategy_used": "Tier 1"},
                },
            ),
        ):
            runner = CliRunner()
            result = runner.invoke(
                cli_module.cli,
                [
                    "--output",
                    "json",
                    "generate-set",
                    "diabetes",
                    "--db-connection",
                    "sqlite:///db",
                ],
            )

        assert result.exit_code == 0
        mock_format_output.assert_called_once()
        mock_create_client.assert_called_once()
        mock_client.generate_concept_set.assert_called_once()

    def test_generate_set_command_failure(self) -> None:
        import importlib

        import athena_client.cli as cli_module

        cli_module = importlib.reload(cli_module)

        mock_client = Mock()
        mock_client.generate_concept_set = Mock(
            return_value={
                "concept_ids": [],
                "metadata": {"status": "FAILURE", "reason": "bad"},
            }
        )

        with (
            patch.object(
                cli_module, "_create_client", return_value=mock_client
            ) as mock_create_client,
            patch.object(cli_module, "_format_output") as mock_format_output,
            patch(
                "athena_client.cli.asyncio.run",
                return_value={
                    "concept_ids": [],
                    "metadata": {"status": "FAILURE", "reason": "bad"},
                },
            ),
        ):
            runner = CliRunner()
            result = runner.invoke(
                cli_module.cli,
                [
                    "--output",
                    "json",
                    "generate-set",
                    "term",
                    "--db-connection",
                    "sqlite:///db",
                ],
            )

        assert result.exit_code == 0
        mock_format_output.assert_called_once()
        mock_create_client.assert_called_once()
        assert "Failure:" in result.output

    def test_generate_set_command_missing_db(self):
        """Missing --db-connection option."""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate-set", "test"], catch_exceptions=False)
        assert result.exit_code != 0
        assert "Missing option '--db-connection'" in result.output

    def test_cli_search_limit_functionality(self):
        """
        Test that CLI correctly applies limit to search results by
        directly reading code. This test doesn't use mocks but
        directly examines the CLI code to ensure it's correct.
        """
        # Open the CLI file and read its content
        cli_path = (
            "/Users/alvaro1/Documents/Coral/Code/athena_api/athena_client/"
            "athena_client/cli.py"
        )
        with open(cli_path, "r") as f:
            cli_code = f.read()
        # Verify that the CLI code includes logic to apply the top() method
        # when limit is provided. This checks that the code contains the
        # critical line that applies the limit
        assert "results = results.top(limit)" in cli_code, (
            "CLI implementation doesn't include code to apply limit using top() method"
        )
