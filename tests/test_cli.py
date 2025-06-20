#!/usr/bin/env python3
"""
Test suite for AWS Profile Switcher
"""

import pytest
import os
import tempfile
import subprocess
from unittest.mock import patch, MagicMock, call
from pathlib import Path
from io import StringIO

# Import the functions to test
from awsprofile.cli import (
    get_profiles, get_current_profile, switch_profile, list_profiles,
    show_current_profile, create_profile, delete_profile, clear_profile,
    create_profile_interactive, delete_profile_interactive, interactive_mode,
    main
)


class TestGetProfiles:
    """Test the get_profiles function."""
    
    @patch('subprocess.run')
    def test_get_profiles_success(self, mock_run):
        """Test successful profile retrieval."""
        # Mock aws configure list-profiles
        list_result = MagicMock()
        list_result.returncode = 0
        list_result.stdout = "default\nwork\npersonal\n"
        
        # Mock sts get-caller-identity calls
        sts_account_result = MagicMock()
        sts_account_result.returncode = 0
        sts_account_result.stdout = "123456789012"
        
        sts_user_result = MagicMock()
        sts_user_result.returncode = 0
        sts_user_result.stdout = "arn:aws:iam::123456789012:user/testuser"
        
        mock_run.side_effect = [
            list_result,  # list-profiles
            sts_account_result, sts_user_result,  # default profile
            sts_account_result, sts_user_result,  # work profile  
            sts_account_result, sts_user_result,  # personal profile
        ]
        
        profiles = get_profiles()
        
        assert 'default' in profiles
        assert 'work' in profiles
        assert 'personal' in profiles
        assert profiles['default']['account'] == '123456789012'
        assert profiles['default']['user'] == 'arn:aws:iam::123456789012:user/testuser'
    
    @patch('subprocess.run')
    def test_get_profiles_no_profiles(self, mock_run):
        """Test when no profiles are configured."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'aws')
        
        profiles = get_profiles()
        assert profiles == {}
    
    @patch('subprocess.run')
    def test_get_profiles_aws_cli_not_found(self, mock_run):
        """Test when AWS CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        with pytest.raises(SystemExit):
            get_profiles()
    
    @patch('subprocess.run')
    def test_get_profiles_invalid_credentials(self, mock_run):
        """Test handling of invalid credentials."""
        # Mock aws configure list-profiles
        list_result = MagicMock()
        list_result.returncode = 0
        list_result.stdout = "invalid-profile\n"
        
        # Mock failed sts calls
        sts_result = MagicMock()
        sts_result.returncode = 1
        
        mock_run.side_effect = [
            list_result,  # list-profiles
            sts_result, sts_result,  # failed sts calls
        ]
        
        profiles = get_profiles()
        
        assert 'invalid-profile' in profiles
        assert profiles['invalid-profile']['account'] == 'Invalid'
        assert profiles['invalid-profile']['user'] == 'Unknown'
    
    @patch('subprocess.run')
    def test_get_profiles_timeout(self, mock_run):
        """Test handling of timeout during profile validation."""
        list_result = MagicMock()
        list_result.returncode = 0
        list_result.stdout = "slow-profile\n"
        
        mock_run.side_effect = [
            list_result,  # list-profiles
            subprocess.TimeoutExpired(['aws'], 10),  # timeout
        ]
        
        profiles = get_profiles()
        
        assert 'slow-profile' in profiles
        assert profiles['slow-profile']['account'] == 'Invalid'
        assert profiles['slow-profile']['user'] == 'The config profile could not be found'


class TestGetCurrentProfile:
    """Test the get_current_profile function."""
    
    def test_get_current_profile_from_env(self):
        """Test getting current profile from AWS_PROFILE environment variable."""
        with patch.dict(os.environ, {'AWS_PROFILE': 'work'}):
            current = get_current_profile()
            assert current == 'work'
    
    @patch('subprocess.run')
    def test_get_current_profile_from_aws_cli(self, mock_run):
        """Test getting current profile from AWS CLI when no env var set."""
        with patch.dict(os.environ, {}, clear=True):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Name                    Value             Source\nprofile               work-profile      profile\n"
            mock_run.return_value = mock_result
            
            current = get_current_profile()
            assert current == 'work-profile'
    
    @patch('subprocess.run')
    def test_get_current_profile_none(self, mock_run):
        """Test when no current profile is set."""
        with patch.dict(os.environ, {}, clear=True):
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Name                    Value             Source\nprofile               <not set>         None\n"
            mock_run.return_value = mock_result
            
            current = get_current_profile()
            assert current is None


class TestSwitchProfile:
    """Test the switch_profile function."""
    
    @patch('awsprofile.cli.get_profiles')
    @patch('subprocess.run')
    def test_switch_profile_success(self, mock_run, mock_get_profiles):
        """Test successful profile switching."""
        mock_get_profiles.return_value = {
            'work': {'account': '123456789012', 'user': 'arn:aws:iam::123456789012:user/testuser'}
        }
        
        # Mock successful aws configure get/set calls
        get_result = MagicMock()
        get_result.returncode = 0
        get_result.stdout = "us-west-2"
        
        set_result = MagicMock()
        set_result.returncode = 0
        
        mock_run.side_effect = [get_result, get_result, set_result, set_result, 
                               get_result, get_result, set_result, set_result]
        
        result = switch_profile('work')
        assert result is True
    
    @patch('awsprofile.cli.get_profiles')
    def test_switch_profile_not_found(self, mock_get_profiles):
        """Test switching to non-existent profile."""
        mock_get_profiles.return_value = {'work': {}}
        
        result = switch_profile('nonexistent')
        assert result is False
    
    @patch('awsprofile.cli.get_profiles')
    @patch('subprocess.run')
    def test_switch_profile_aws_error(self, mock_run, mock_get_profiles):
        """Test handling AWS CLI errors during switch."""
        mock_get_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_run.side_effect = subprocess.CalledProcessError(1, 'aws')
        
        result = switch_profile('work')
        assert result is False


class TestCreateProfile:
    """Test the create_profile function."""
    
    @patch('builtins.input')
    @patch('subprocess.run')
    def test_create_profile_success(self, mock_run, mock_input):
        """Test successful profile creation."""
        mock_input.side_effect = ['AKIA123456789', 'secretkey123', 'us-west-2', 'json']
        mock_run.return_value = MagicMock(returncode=0)
        
        result = create_profile('newprofile')
        assert result is True
    
    @patch('builtins.input')
    def test_create_profile_empty_access_key(self, mock_input):
        """Test profile creation with empty access key."""
        mock_input.return_value = ''
        
        result = create_profile('testprofile')
        assert result is False
    
    @patch('builtins.input')
    def test_create_profile_keyboard_interrupt(self, mock_input):
        """Test profile creation interrupted by user."""
        mock_input.side_effect = KeyboardInterrupt()
        
        result = create_profile('testprofile')
        assert result is False


class TestDeleteProfile:
    """Test the delete_profile function."""
    
    @patch('awsprofile.cli.get_profiles')
    def test_delete_profile_not_found(self, mock_get_profiles):
        """Test deleting non-existent profile."""
        mock_get_profiles.return_value = {'work': {}}
        
        result = delete_profile('nonexistent')
        assert result is False
    
    @patch('awsprofile.cli.get_profiles')
    @patch('builtins.input')
    def test_delete_profile_cancelled(self, mock_input, mock_get_profiles):
        """Test profile deletion when user cancels."""
        mock_get_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_input.return_value = 'n'
        
        result = delete_profile('work')
        assert result is False
    
    @patch('awsprofile.cli.get_profiles')
    @patch('builtins.input')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    @patch('pathlib.Path.write_text')
    def test_delete_profile_success(self, mock_write, mock_read, mock_exists, mock_input, mock_get_profiles):
        """Test successful profile deletion."""
        mock_get_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_input.return_value = 'yes'
        mock_exists.return_value = True
        mock_read.return_value = "[work]\naws_access_key_id = test\n[other]\nkey = value"
        
        result = delete_profile('work')
        assert result is True


class TestClearProfile:
    """Test the clear_profile function."""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    @patch('pathlib.Path.write_text')
    def test_clear_profile_success(self, mock_write, mock_read, mock_exists):
        """Test successful profile clearing."""
        mock_exists.return_value = True
        mock_read.return_value = "[default]\naws_access_key_id = test\n[other]\nkey = value"
        
        result = clear_profile()
        assert result is True


class TestInteractiveMode:
    """Test the interactive_mode function."""
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('builtins.input')
    def test_interactive_mode_quit(self, mock_input, mock_current, mock_profiles):
        """Test quitting interactive mode."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_input.return_value = 'q'
        
        # Should not raise an exception
        interactive_mode()
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile') 
    @patch('builtins.input')
    def test_interactive_mode_refresh_redisplays_menu(self, mock_input, mock_current, mock_profiles):
        """Test that refresh option redisplays the menu."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_input.side_effect = ['r', 'q']  # refresh, then quit
        
        # Should call get_profiles twice (initial + after refresh)
        interactive_mode()
        assert mock_profiles.call_count >= 2
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('awsprofile.cli.switch_profile')
    @patch('builtins.input')
    def test_interactive_mode_profile_switch_continues(self, mock_input, mock_switch, mock_current, mock_profiles):
        """Test that profile switching asks to continue and loops back to menu."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_switch.return_value = True
        mock_input.side_effect = ['1', 'y', 'q']  # switch to profile 1, continue, then quit
        
        interactive_mode()
        mock_switch.assert_called_once_with('work')
        # Should call get_profiles multiple times due to looping
        assert mock_profiles.call_count >= 2
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('awsprofile.cli.switch_profile')
    @patch('builtins.input')
    def test_interactive_mode_profile_switch_exits(self, mock_input, mock_switch, mock_current, mock_profiles):
        """Test that user can exit after profile switching."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_switch.return_value = True
        mock_input.side_effect = ['1', 'n']  # switch to profile 1, don't continue
        
        interactive_mode()
        mock_switch.assert_called_once_with('work')
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('awsprofile.cli.create_profile_interactive')
    @patch('builtins.input')
    def test_interactive_mode_create_profile_loops_back(self, mock_input, mock_create, mock_current, mock_profiles):
        """Test that creating profile loops back to main menu."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_create.return_value = True
        mock_input.side_effect = ['c', 'q']  # create profile, then quit
        
        interactive_mode()
        mock_create.assert_called_once()
        # Should call get_profiles multiple times due to looping
        assert mock_profiles.call_count >= 2
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('awsprofile.cli.delete_profile_interactive')
    @patch('builtins.input')
    def test_interactive_mode_delete_profile_loops_back(self, mock_input, mock_delete, mock_current, mock_profiles):
        """Test that deleting profile loops back to main menu."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_delete.return_value = True
        mock_input.side_effect = ['d', 'q']  # delete profile, then quit
        
        interactive_mode()
        mock_delete.assert_called_once()
        # Should call get_profiles multiple times due to looping
        assert mock_profiles.call_count >= 2
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('awsprofile.cli.clear_profile')
    @patch('builtins.input')
    def test_interactive_mode_clear_profile_loops_back(self, mock_input, mock_clear, mock_current, mock_profiles):
        """Test that clearing profile loops back to main menu."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_clear.return_value = True
        mock_input.side_effect = ['x', 'q']  # clear profile, then quit
        
        interactive_mode()
        mock_clear.assert_called_once()
        # Should call get_profiles multiple times due to looping
        assert mock_profiles.call_count >= 2
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('builtins.input')
    def test_interactive_mode_invalid_option_error_handling(self, mock_input, mock_current, mock_profiles):
        """Test error handling for invalid options."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_input.side_effect = ['invalid', '', 'q']  # invalid option, empty, then quit
        
        # Should not raise an exception
        interactive_mode()
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('builtins.input')
    def test_interactive_mode_invalid_number_error_handling(self, mock_input, mock_current, mock_profiles):
        """Test error handling for invalid profile numbers."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_input.side_effect = ['99', '', 'q']  # invalid number, enter, then quit
        
        # Should not raise an exception
        interactive_mode()
    
    @patch('awsprofile.cli.get_profiles')
    def test_interactive_mode_no_profiles(self, mock_profiles):
        """Test interactive mode when no profiles exist."""
        mock_profiles.return_value = {}
        
        # Should exit gracefully without crashing
        interactive_mode()
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('builtins.input')
    def test_interactive_mode_keyboard_interrupt(self, mock_input, mock_current, mock_profiles):
        """Test handling keyboard interrupt in interactive mode."""
        mock_profiles.return_value = {'work': {'account': '123', 'user': 'test'}}
        mock_current.return_value = None
        mock_input.side_effect = KeyboardInterrupt()
        
        # Should handle KeyboardInterrupt gracefully
        interactive_mode()


class TestMainFunction:
    """Test the main function and CLI argument parsing."""
    
    @patch('awsprofile.cli.switch_profile')
    def test_main_profile_switch(self, mock_switch):
        """Test main function with profile switching."""
        with patch('sys.argv', ['awsprofile', '-p', 'work']):
            main()
        mock_switch.assert_called_once_with('work')
    
    @patch('awsprofile.cli.list_profiles')
    def test_main_list_command(self, mock_list):
        """Test main function with list command."""
        with patch('sys.argv', ['awsprofile', 'list']):
            main()
        mock_list.assert_called_once()
    
    @patch('awsprofile.cli.show_current_profile')
    def test_main_current_command(self, mock_current):
        """Test main function with current command."""
        with patch('sys.argv', ['awsprofile', 'current']):
            main()
        mock_current.assert_called_once()
    
    @patch('awsprofile.cli.clear_profile')
    def test_main_clear_command(self, mock_clear):
        """Test main function with clear command."""
        with patch('sys.argv', ['awsprofile', 'clear']):
            main()
        mock_clear.assert_called_once()
    
    @patch('awsprofile.cli.create_profile')
    def test_main_create_command(self, mock_create):
        """Test main function with create command."""
        with patch('sys.argv', ['awsprofile', 'create', 'newprofile']):
            main()
        mock_create.assert_called_once_with('newprofile')
    
    @patch('awsprofile.cli.delete_profile')
    def test_main_delete_command(self, mock_delete):
        """Test main function with delete command."""
        with patch('sys.argv', ['awsprofile', 'delete', 'oldprofile']):
            main()
        mock_delete.assert_called_once_with('oldprofile')
    
    @patch('awsprofile.cli.interactive_mode')
    def test_main_no_args_interactive(self, mock_interactive):
        """Test main function with no arguments starts interactive mode."""
        with patch('sys.argv', ['awsprofile']):
            main()
        mock_interactive.assert_called_once()


class TestListProfiles:
    """Test the list_profiles function."""
    
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.get_current_profile')
    @patch('builtins.print')
    def test_list_profiles_with_profiles(self, mock_print, mock_current, mock_profiles):
        """Test listing profiles when profiles exist."""
        mock_profiles.return_value = {
            'work': {'account': '123456789012', 'user': 'arn:aws:iam::123456789012:user/testuser'},
            'personal': {'account': '987654321098', 'user': 'arn:aws:iam::987654321098:user/myuser'}
        }
        mock_current.return_value = 'work'
        
        list_profiles()
        
        # Should print profile information
        mock_print.assert_called()
    
    @patch('awsprofile.cli.get_profiles')
    @patch('builtins.print')
    def test_list_profiles_no_profiles(self, mock_print, mock_profiles):
        """Test listing profiles when no profiles exist."""
        mock_profiles.return_value = {}
        
        list_profiles()
        
        # Should print no profiles message
        mock_print.assert_called()


class TestShowCurrentProfile:
    """Test the show_current_profile function."""
    
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_show_current_profile_with_profile(self, mock_print, mock_run):
        """Test showing current profile when one is set."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Name                    Value             Source\nprofile               work-profile      profile\n"
        mock_run.return_value = mock_result
        
        show_current_profile()
        mock_print.assert_called()
    
    @patch('subprocess.run')
    @patch('builtins.print')
    def test_show_current_profile_no_profile(self, mock_print, mock_run):
        """Test showing current profile when none is set."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Name                    Value             Source\nprofile               <not set>         None\n"
        mock_run.return_value = mock_result
        
        show_current_profile()
        mock_print.assert_called()


class TestCreateProfileInteractive:
    """Test the create_profile_interactive function."""
    
    @patch('builtins.input')
    @patch('awsprofile.cli.get_profiles')
    @patch('awsprofile.cli.create_profile')
    def test_create_profile_interactive_success(self, mock_create, mock_profiles, mock_input):
        """Test successful interactive profile creation."""
        mock_input.return_value = 'newprofile'
        mock_profiles.return_value = {'existing': {}}
        mock_create.return_value = True
        
        result = create_profile_interactive()
        assert result is True
        mock_create.assert_called_once_with('newprofile')
    
    @patch('builtins.input')
    def test_create_profile_interactive_empty_name(self, mock_input):
        """Test interactive profile creation with empty name."""
        mock_input.return_value = ''
        
        result = create_profile_interactive()
        assert result is False
    
    @patch('builtins.input')
    @patch('awsprofile.cli.get_profiles')
    def test_create_profile_interactive_existing_profile(self, mock_profiles, mock_input):
        """Test interactive profile creation with existing profile name."""
        mock_input.return_value = 'existing'
        mock_profiles.return_value = {'existing': {}}
        
        result = create_profile_interactive()
        assert result is False


class TestDeleteProfileInteractive:
    """Test the delete_profile_interactive function."""
    
    @patch('builtins.input')
    @patch('awsprofile.cli.delete_profile')
    def test_delete_profile_interactive_by_number(self, mock_delete, mock_input):
        """Test interactive profile deletion by number."""
        profiles = {'work': {}, 'personal': {}}
        mock_input.return_value = '1'
        mock_delete.return_value = True
        
        result = delete_profile_interactive(profiles)
        assert result is True
        mock_delete.assert_called_once_with('work')
    
    @patch('builtins.input')
    @patch('awsprofile.cli.delete_profile')
    def test_delete_profile_interactive_by_name(self, mock_delete, mock_input):
        """Test interactive profile deletion by name."""
        profiles = {'work': {}, 'personal': {}}
        mock_input.return_value = 'personal'
        mock_delete.return_value = True
        
        result = delete_profile_interactive(profiles)
        assert result is True
        mock_delete.assert_called_once_with('personal')
    
    @patch('builtins.input')
    def test_delete_profile_interactive_invalid_number(self, mock_input):
        """Test interactive profile deletion with invalid number."""
        profiles = {'work': {}}
        mock_input.return_value = '99'
        
        result = delete_profile_interactive(profiles)
        assert result is False
    
    def test_delete_profile_interactive_no_profiles(self):
        """Test interactive profile deletion with no profiles."""
        result = delete_profile_interactive({})
        assert result is False


# Integration and edge case tests
class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @patch('awsprofile.cli.get_profiles')
    def test_very_long_profile_names(self, mock_profiles):
        """Test handling of very long profile names."""
        long_name = 'a' * 200
        mock_profiles.return_value = {}
        
        # Should not crash the application
        result = switch_profile(long_name)
        assert result is False
    
    @patch('subprocess.run')
    def test_network_connectivity_issues(self, mock_run):
        """Test handling of network connectivity issues."""
        import socket
        mock_run.side_effect = socket.gaierror("Network unreachable")
        
        profiles = get_profiles()
        # Should handle network issues gracefully
        assert isinstance(profiles, dict)


if __name__ == '__main__':
    pytest.main([__file__])