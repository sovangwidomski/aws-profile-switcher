#!/usr/bin/env python3
"""
Test suite for AWS Profile Switcher
"""

import pytest
import os
import tempfile
import configparser
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import shutil

# Import the module to test
from awsprofile.cli import AWSProfileManager


class TestAWSProfileManager:
    """Test cases for AWSProfileManager class."""
    
    @pytest.fixture
    def temp_aws_dir(self):
        """Create a temporary AWS directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            aws_dir = Path(temp_dir) / '.aws'
            aws_dir.mkdir()
            
            # Create sample credentials file
            creds_content = """[default]
aws_access_key_id = AKIA123456789
aws_secret_access_key = secret123
region = us-east-1

[work]
aws_access_key_id = AKIA987654321
aws_secret_access_key = secret456
region = us-west-2

[personal]
aws_access_key_id = AKIA555666777
aws_secret_access_key = secret789
region = eu-west-1
"""
            (aws_dir / 'credentials').write_text(creds_content)
            
            # Create sample config file
            config_content = """[default]
region = us-east-1
output = json

[profile work]
region = us-west-2
output = json

[profile personal]
region = eu-west-1
output = json
"""
            (aws_dir / 'config').write_text(config_content)
            
            # Patch the home directory
            with patch('pathlib.Path.home', return_value=Path(temp_dir)):
                yield aws_dir
    
    def test_get_current_profile_default(self):
        """Test getting current profile when no AWS_PROFILE is set."""
        with patch.dict(os.environ, {}, clear=True):
            manager = AWSProfileManager()
            assert manager.get_current_profile() == 'default'
    
    def test_get_current_profile_custom(self):
        """Test getting current profile when AWS_PROFILE is set."""
        with patch.dict(os.environ, {'AWS_PROFILE': 'work'}):
            manager = AWSProfileManager()
            assert manager.get_current_profile() == 'work'
    
    def test_get_available_profiles(self, temp_aws_dir):
        """Test getting list of available profiles."""
        manager = AWSProfileManager()
        profiles = manager.get_available_profiles()
        expected = ['default', 'personal', 'work']  # sorted
        assert profiles == expected
    
    def test_get_available_profiles_no_file(self):
        """Test handling when credentials file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            manager = AWSProfileManager()
            profiles = manager.get_available_profiles()
            assert profiles == []
    
    @patch('subprocess.run')
    def test_get_account_info_success(self, mock_run):
        """Test successful AWS account info retrieval."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Account": "123456789012", "Arn": "arn:aws:iam::123456789012:user/testuser"}'
        )
        
        manager = AWSProfileManager()
        account, arn = manager.get_account_info('test-profile')
        
        assert account == '123456789012'
        assert arn == 'arn:aws:iam::123456789012:user/testuser'
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_get_account_info_failure(self, mock_run):
        """Test handling AWS account info failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr='The security token included in the request is invalid.'
        )
        
        manager = AWSProfileManager()
        account, detail = manager.get_account_info('invalid-profile')
        
        assert account == 'Invalid'
        assert 'security token' in detail
    
    @patch('subprocess.run')
    def test_get_account_info_timeout(self, mock_run):
        """Test handling AWS timeout."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired('aws', 10)
        
        manager = AWSProfileManager()
        account, detail = manager.get_account_info('slow-profile')
        
        assert account == 'Timeout'
        assert 'timed out' in detail
    
    def test_extract_username(self):
        """Test username extraction from ARN."""
        manager = AWSProfileManager()
        
        # Test IAM user ARN
        arn = 'arn:aws:iam::123456789012:user/testuser'
        assert manager.extract_username(arn) == 'testuser'
        
        # Test assumed role ARN
        arn = 'arn:aws:sts::123456789012:assumed-role/role-name/session-name'
        assert manager.extract_username(arn) == 'session-name'
        
        # Test simple string
        assert manager.extract_username('simple') == 'simple'
    
    def test_validate_profile_exists(self, temp_aws_dir):
        """Test profile validation for existing profile."""
        with patch.object(AWSProfileManager, 'get_account_info', return_value=('123456789012', 'arn')):
            manager = AWSProfileManager()
            assert manager.validate_profile('work') is True
    
    def test_validate_profile_not_exists(self, temp_aws_dir):
        """Test profile validation for non-existing profile."""
        manager = AWSProfileManager()
        assert manager.validate_profile('nonexistent') is False
    
    def test_validate_profile_invalid_credentials(self, temp_aws_dir):
        """Test profile validation with invalid credentials."""
        with patch.object(AWSProfileManager, 'get_account_info', return_value=('Invalid', 'Bad credentials')):
            manager = AWSProfileManager()
            assert manager.validate_profile('work') is False
    
    def test_switch_profile_shell_mode(self, temp_aws_dir):
        """Test profile switching in shell mode."""
        with patch.object(AWSProfileManager, 'get_account_info', return_value=('123456789012', 'arn')):
            manager = AWSProfileManager()
            result = manager.switch_profile('work', shell_mode=True)
            assert result is True
    
    def test_switch_profile_normal_mode(self, temp_aws_dir):
        """Test profile switching in normal mode."""
        with patch.object(AWSProfileManager, 'get_account_info', return_value=('123456789012', 'arn:aws:iam::123456789012:user/testuser')):
            manager = AWSProfileManager()
            result = manager.switch_profile('work', shell_mode=False)
            assert result is True
            assert os.environ.get('AWS_PROFILE') == 'work'
    
    def test_delete_profile_default_protection(self, temp_aws_dir):
        """Test that default profile cannot be deleted."""
        manager = AWSProfileManager()
        result = manager.delete_profile('default')
        assert result is False
    
    def test_delete_profile_not_exists(self, temp_aws_dir):
        """Test deleting a profile that doesn't exist."""
        manager = AWSProfileManager()
        result = manager.delete_profile('nonexistent')
        assert result is False
    
    def test_delete_profile_cancelled(self, temp_aws_dir):
        """Test profile deletion when user cancels."""
        with patch('builtins.input', return_value='no'):
            manager = AWSProfileManager()
            result = manager.delete_profile('personal')
            assert result is False
    
    def test_delete_profile_success(self, temp_aws_dir):
        """Test successful profile deletion."""
        with patch('builtins.input', return_value='yes'):
            manager = AWSProfileManager()
            result = manager.delete_profile('personal')
            assert result is True
            
            # Verify profile was removed
            profiles = manager.get_available_profiles()
            assert 'personal' not in profiles
            
            # Verify backup files were created
            backup_creds = temp_aws_dir / 'credentials.backup'
            backup_config = temp_aws_dir / 'config.backup'
            assert backup_creds.exists()
            assert backup_config.exists()
    
    def test_delete_profile_current_profile_reset(self, temp_aws_dir):
        """Test that current profile is reset when deleted."""
        with patch('builtins.input', return_value='yes'):
            with patch.dict(os.environ, {'AWS_PROFILE': 'personal'}):
                manager = AWSProfileManager()
                result = manager.delete_profile('personal')
                assert result is True
                assert 'AWS_PROFILE' not in os.environ
    
    @patch('subprocess.run')
    def test_delete_profile_with_config_cleanup(self, mock_run, temp_aws_dir):
        """Test that profiles are removed from both credentials and config files."""
        with patch('builtins.input', return_value='yes'):
            manager = AWSProfileManager()
            result = manager.delete_profile('work')
            assert result is True
            
            # Check credentials file
            creds_config = configparser.ConfigParser()
            creds_config.read(manager.credentials_path)
            assert not creds_config.has_section('work')
            
            # Check config file
            config_config = configparser.ConfigParser()
            config_config.read(manager.config_path)
            assert not config_config.has_section('profile work')
    
    def test_create_profile_empty_name(self):
        """Test creating profile with empty name."""
        manager = AWSProfileManager()
        result = manager.create_profile('')
        assert result is False
    
    def test_create_profile_already_exists_decline(self, temp_aws_dir):
        """Test creating profile that already exists - user declines overwrite."""
        with patch('builtins.input', return_value='n'):
            manager = AWSProfileManager()
            result = manager.create_profile('work')  # 'work' profile exists in fixture
            assert result is False
    
    @patch('subprocess.run')
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_profile_success(self, mock_getpass, mock_input, mock_run, temp_aws_dir):
        """Test successful profile creation."""
        # Mock user inputs
        mock_input.side_effect = ['AKIA123456789', 'us-west-1', 'json']
        mock_getpass.return_value = 'secretkey123'
        
        # Mock successful AWS validation
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"Account": "123456789012", "Arn": "arn:aws:iam::123456789012:user/newuser"}'
        )
        
        manager = AWSProfileManager()
        result = manager.create_profile('newprofile')
        assert result is True
        
        # Verify profile was added to available profiles
        profiles = manager.get_available_profiles()
        assert 'newprofile' in profiles
    
    @patch('subprocess.run')
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_profile_invalid_credentials(self, mock_getpass, mock_input, mock_run, temp_aws_dir):
        """Test profile creation with invalid credentials."""
        # Mock user inputs
        mock_input.side_effect = ['AKIA123456789', 'us-west-1', 'json']
        mock_getpass.return_value = 'badkey'
        
        # Mock failed AWS validation
        mock_run.return_value = MagicMock(
            returncode=1,
            stderr='The security token included in the request is invalid.'
        )
        
        manager = AWSProfileManager()
        result = manager.create_profile('badprofile')
        assert result is False
    
    @patch('builtins.input')
    def test_create_profile_empty_access_key(self, mock_input, temp_aws_dir):
        """Test profile creation with empty access key."""
        mock_input.return_value = ''  # Empty access key
        
        manager = AWSProfileManager()
        result = manager.create_profile('testprofile')
        assert result is False
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_profile_empty_secret_key(self, mock_input, mock_getpass, temp_aws_dir):
        """Test profile creation with empty secret key."""
        mock_input.return_value = 'AKIA123456789'
        mock_getpass.return_value = ''  # Empty secret key
        
        manager = AWSProfileManager()
        result = manager.create_profile('testprofile')
        assert result is False
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_create_profile_keyboard_interrupt(self, mock_input, mock_getpass, temp_aws_dir):
        """Test profile creation interrupted by user."""
        mock_input.return_value = 'AKIA123456789'
        mock_getpass.side_effect = KeyboardInterrupt()
        
        manager = AWSProfileManager()
        result = manager.create_profile('testprofile')
        assert result is False


class TestCLIIntegration:
    """Test CLI integration and main function."""
    
    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_create_profile(self, mock_manager_class):
        """Test main function with profile creation."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile', 'create', 'new-profile']):
            from awsprofile.cli import main
            main()
            
        mock_manager.create_profile.assert_called_once_with('new-profile')

    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_no_args_interactive(self, mock_manager_class):
        """Test main function with no arguments starts interactive mode."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile']):
            from awsprofile.cli import main
            main()
            
        mock_manager.interactive_mode.assert_called_once()
    
    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_list_command(self, mock_manager_class):
        """Test main function with list command."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile', 'list']):
            from awsprofile.cli import main
            main()
            
        mock_manager.show_profiles.assert_called_once()
    
    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_switch_profile(self, mock_manager_class):
        """Test main function with profile switch."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile', 'work']):
            from awsprofile.cli import main
            main()
            
        mock_manager.switch_profile.assert_called_once_with('work')
    
    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_delete_profile(self, mock_manager_class):
        """Test main function with profile deletion."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile', 'delete', 'old-profile']):
            from awsprofile.cli import main
            main()
            
        mock_manager.delete_profile.assert_called_once_with('old-profile')
    
    @patch('awsprofile.cli.AWSProfileManager')
    def test_main_shell_mode(self, mock_manager_class):
        """Test main function with shell mode."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        with patch('sys.argv', ['awsprofile', 'work', '--shell']):
            from awsprofile.cli import main
            main()
            
        mock_manager.switch_profile.assert_called_once_with('work', shell_mode=True)
    
    def test_main_help(self, capsys):
        """Test main function with help argument."""
        with patch('sys.argv', ['awsprofile', '--help']):
            from awsprofile.cli import main
            main()
            
        captured = capsys.readouterr()
        assert 'AWS Profile Switcher' in captured.out
        assert 'Usage:' in captured.out
    
    def test_main_version(self, capsys):
        """Test main function with version argument."""
        with patch('sys.argv', ['awsprofile', '--version']):
            from awsprofile.cli import main
            main()
            
        captured = capsys.readouterr()
        assert 'AWS Profile Switcher v' in captured.out


class TestShellIntegration:
    """Test shell integration functionality."""
    
    def test_generate_shell_integration(self):
        """Test shell integration script generation."""
        from awsprofile.cli import generate_shell_integration
        
        integration = generate_shell_integration()
        
        assert 'awsp()' in integration
        assert 'export AWS_PROFILE' in integration
        assert 'complete -F _awsp_completion awsp' in integration
        assert 'compdef _awsp_zsh_completion awsp' in integration


# Performance and edge case tests
class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('pathlib.Path.exists')
    def test_missing_aws_directory(self, mock_exists):
        """Test behavior when .aws directory doesn't exist."""
        mock_exists.return_value = False
        manager = AWSProfileManager()
        profiles = manager.get_available_profiles()
        assert profiles == []
    
    @patch('configparser.ConfigParser.read')
    def test_corrupted_credentials_file(self, mock_read):
        """Test handling of corrupted credentials file."""
        mock_read.side_effect = configparser.Error("Corrupted file")
        manager = AWSProfileManager()
        
        # Should handle the exception gracefully
        try:
            profiles = manager.get_available_profiles()
            # If it doesn't raise an exception, test passes
            assert True
        except configparser.Error:
            pytest.fail("Should handle corrupted config file gracefully")
    
    def test_very_long_profile_names(self, temp_aws_dir):
        """Test handling of very long profile names."""
        # Create a profile with a very long name
        long_name = 'a' * 200
        manager = AWSProfileManager()
        
        # This should not crash the application
        result = manager.validate_profile(long_name)
        assert result is False  # Profile doesn't exist, but shouldn't crash
    
    @patch('subprocess.run')
    def test_network_connectivity_issues(self, mock_run):
        """Test handling of network connectivity issues."""
        import socket
        mock_run.side_effect = socket.gaierror("Network unreachable")
        
        manager = AWSProfileManager()
        account, detail = manager.get_account_info('test-profile')
        
        assert account == 'Error'
        assert 'Network unreachable' in detail or 'gaierror' in detail


if __name__ == '__main__':
    pytest.main([__file__])