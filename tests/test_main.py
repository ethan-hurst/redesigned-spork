"""
Tests for main CLI module.
"""

import pytest
from unittest.mock import patch, Mock
from click.testing import CliRunner

from src.main import cli


class TestMainCLI:
    """Tests for main CLI functionality."""
    
    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Microsoft Dynamics & Power Platform Architecture Builder" in result.output
    
    def test_cli_version(self):
        """Test CLI version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_validate_command(self):
        """Test validate command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['validate'])
        
        assert result.exit_code == 0
        assert "Validating system requirements" in result.output
    
    def test_stats_command(self):
        """Test stats command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['stats'])
        
        assert result.exit_code == 0
        assert "Technology Catalog Statistics" in result.output
    
    def test_list_components_command(self):
        """Test list-components command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-components', '--category', 'power_platform'])
        
        assert result.exit_code == 0
        assert "Power Platform" in result.output
    
    def test_list_components_invalid_category(self):
        """Test list-components with invalid category."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-components', '--category', 'invalid_category'])
        
        # The CLI should handle this gracefully and show an error message
        # but may not exit with code 1 if it's handled internally
        assert "Invalid category" in result.output or "No components found" in result.output
    
    def test_examples_command(self):
        """Test examples command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['examples'])
        
        assert result.exit_code == 0
        assert "Examples" in result.output
        assert "Simple Power Platform Stack" in result.output
    
    def test_examples_command_all(self):
        """Test examples command with --all flag."""
        runner = CliRunner()
        result = runner.invoke(cli, ['examples', '--all'])
        
        assert result.exit_code == 0
        assert "Examples" in result.output
    
    @patch('src.cli.commands.CLICommands.generate_from_components')
    def test_generate_command(self, mock_generate):
        """Test generate command."""
        mock_generate.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate', 
            '--components', 'power_bi,dataverse',
            '--output', 'test.png',
            '--name', 'Test Architecture'
        ])
        
        assert result.exit_code == 0
        mock_generate.assert_called_once()
        
        # Check that the method was called with correct arguments
        call_args = mock_generate.call_args
        assert call_args[1]['component_ids'] == ['power_bi', 'dataverse']
        assert call_args[1]['output_file'] == 'test.png'
        assert call_args[1]['name'] == 'Test Architecture'
    
    def test_generate_command_missing_components(self):
        """Test generate command without components."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate',
            '--output', 'test.png'
        ])
        
        # Should fail due to missing required --components option
        assert result.exit_code == 2
        assert "Missing option" in result.output
    
    def test_generate_command_missing_output(self):
        """Test generate command without output."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'generate',
            '--components', 'power_bi,dataverse'
        ])
        
        # Should fail due to missing required --output option
        assert result.exit_code == 2
        assert "Missing option" in result.output
    
    @patch('src.cli.commands.CLICommands.run_interactive_mode')
    def test_interactive_command(self, mock_interactive):
        """Test interactive command."""
        mock_interactive.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(cli, ['interactive'])
        
        assert result.exit_code == 0
        mock_interactive.assert_called_once()
    
    @patch('src.cli.commands.CLICommands.run_interactive_mode')
    def test_interactive_command_keyboard_interrupt(self, mock_interactive):
        """Test interactive command with keyboard interrupt."""
        mock_interactive.side_effect = KeyboardInterrupt()
        
        runner = CliRunner()
        result = runner.invoke(cli, ['interactive'])
        
        assert result.exit_code == 0
        assert "cancelled by user" in result.output
    
    @patch('src.cli.commands.CLICommands.__init__')
    def test_command_exception_handling(self, mock_init):
        """Test exception handling in commands."""
        mock_init.side_effect = Exception("Test error")
        
        runner = CliRunner()
        result = runner.invoke(cli, ['stats'])
        
        assert result.exit_code == 1
        assert "Error" in result.output