#!/usr/bin/env python3
"""
AWS Profile Switcher CLI Tool - Enhanced Version
A simple, interactive tool to view, switch, and delete AWS profiles.

Author: Sovang Widomski
License: MIT
"""

import os
import subprocess
import sys
import json
from pathlib import Path
import configparser
from typing import List, Tuple, Optional
import shutil

__version__ = "1.1.0"

class AWSProfileManager:
    """Main class for managing AWS profiles."""
    
    def __init__(self):
        self.credentials_path = Path.home() / '.aws' / 'credentials'
        self.config_path = Path.home() / '.aws' / 'config'
    
    def get_current_profile(self) -> str:
        """Get the currently active AWS profile."""
        return os.environ.get('AWS_PROFILE', 'default')
    
    def get_available_profiles(self) -> List[str]:
        """Read available profiles from ~/.aws/credentials file."""
        if not self.credentials_path.exists():
            print("❌ No AWS credentials file found at ~/.aws/credentials")
            print("💡 Run 'aws configure' to set up your first profile.")
            return []
        
        config = configparser.ConfigParser()
        config.read(self.credentials_path)
        
        profiles = list(config.sections())
        
        # Add 'default' if it's not explicitly listed but exists
        if 'default' not in profiles and config.has_option('DEFAULT', 'aws_access_key_id'):
            profiles.insert(0, 'default')
        
        return sorted(profiles)
    
    def get_account_info(self, profile_name: str) -> Tuple[str, str]:
        """Get AWS account information for a given profile."""
        try:
            cmd = [
                'aws', 'sts', 'get-caller-identity', 
                '--profile', profile_name, 
                '--output', 'json'
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                account_id = data.get('Account', 'Unknown')
                user_arn = data.get('Arn', 'Unknown')
                return account_id, user_arn
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return "Invalid", error_msg
        
        except subprocess.TimeoutExpired:
            return "Timeout", "AWS call timed out (>10s)"
        except json.JSONDecodeError:
            return "Error", "Invalid JSON response from AWS"
        except FileNotFoundError:
            return "Error", "AWS CLI not found - please install it"
        except Exception as e:
            return "Error", str(e)
    
    def extract_username(self, arn: str) -> str:
        """Extract username from AWS ARN."""
        if '/' in arn:
            return arn.split('/')[-1]
        elif ':' in arn:
            return arn.split(':')[-1]
        return arn
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile from AWS credentials and config files."""
        if profile_name == 'default':
            print("❌ Cannot delete the 'default' profile.")
            print("💡 Use 'aws configure' to modify the default profile instead.")
            return False
        
        profiles = self.get_available_profiles()
        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found.")
            return False
        
        # Confirm deletion
        print(f"⚠️  Are you sure you want to delete profile '{profile_name}'?")
        print("   This will remove it from both credentials and config files.")
        confirm = input("   Type 'yes' to confirm: ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Profile deletion cancelled.")
            return False
        
        try:
            # Backup files first
            if self.credentials_path.exists():
                backup_creds = self.credentials_path.with_suffix('.credentials.backup')
                shutil.copy2(self.credentials_path, backup_creds)
                print(f"📋 Backed up credentials to {backup_creds}")
            
            if self.config_path.exists():
                backup_config = self.config_path.with_suffix('.config.backup')
                shutil.copy2(self.config_path, backup_config)
                print(f"📋 Backed up config to {backup_config}")
            
            # Remove from credentials file
            if self.credentials_path.exists():
                creds_config = configparser.ConfigParser()
                creds_config.read(self.credentials_path)
                
                if creds_config.has_section(profile_name):
                    creds_config.remove_section(profile_name)
                    with open(self.credentials_path, 'w') as f:
                        creds_config.write(f)
                    print(f"✅ Removed '{profile_name}' from credentials file")
            
            # Remove from config file
            if self.config_path.exists():
                config_config = configparser.ConfigParser()
                config_config.read(self.config_path)
                
                # Profile sections in config are named "profile profilename" (except default)
                config_section = f"profile {profile_name}" if profile_name != 'default' else profile_name
                
                if config_config.has_section(config_section):
                    config_config.remove_section(config_section)
                    with open(self.config_path, 'w') as f:
                        config_config.write(f)
                    print(f"✅ Removed '{profile_name}' from config file")
            
            # If this was the current profile, reset to default
            current_profile = self.get_current_profile()
            if current_profile == profile_name:
                os.environ.pop('AWS_PROFILE', None)
                print(f"🔄 Reset current profile to 'default' (was '{profile_name}')")
            
            print(f"✅ Successfully deleted profile '{profile_name}'")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting profile: {str(e)}")
            return False
    
    def show_profiles(self) -> None:
        """Display current profile and all available profiles."""
        current = self.get_current_profile()
        profiles = self.get_available_profiles()
        
        if not profiles:
            return
        
        print("\n🔧 AWS Profile Manager v{}".format(__version__))
        print("=" * 60)
        
        # Show current profile with account info
        current_account, current_detail = self.get_account_info(current)
        print(f"📍 Current profile: {current}")
        print(f"   Account: {current_account}")
        
        if current_account not in ["Invalid", "Error", "Timeout"]:
            username = self.extract_username(current_detail)
            print(f"   User: {username}")
        elif current_detail:
            print(f"   Status: {current_detail}")
        
        print(f"\n📋 Available profiles ({len(profiles)} total):")
        print("-" * 40)
        
        for i, profile in enumerate(profiles, 1):
            account_id, detail = self.get_account_info(profile)
            status = "✅" if profile == current else "  "
            
            print(f"{status} {i:2d}. {profile}")
            print(f"       Account: {account_id}")
            
            # Show additional info based on status
            if account_id == "Invalid":
                print(f"       Status: ❌ {detail}")
            elif account_id == "Error":
                print(f"       Status: ⚠️  {detail}")
            elif account_id == "Timeout":
                print(f"       Status: ⏱️  {detail}")
    
    def validate_profile(self, profile_name: str) -> bool:
        """Validate that a profile exists and has valid credentials."""
        profiles = self.get_available_profiles()
        
        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found.")
            print(f"💡 Available profiles: {', '.join(profiles)}")
            return False
        
        # Test the profile
        print(f"🔍 Testing profile '{profile_name}'...")
        account_id, detail = self.get_account_info(profile_name)
        
        if account_id in ["Invalid", "Error", "Timeout"]:
            print(f"❌ Profile '{profile_name}' validation failed:")
            print(f"   {detail}")
            return False
        
        return True
    
    def switch_profile(self, profile_name: str, shell_mode: bool = False) -> bool:
        """Switch to a specific AWS profile."""
        if not self.validate_profile(profile_name):
            return False
        
        if shell_mode:
            # Output shell commands for sourcing
            print(f"export AWS_PROFILE={profile_name}")
            return True
        
        # Set the environment variable for this session
        os.environ['AWS_PROFILE'] = profile_name
        
        # Get account info for confirmation
        account_id, arn = self.get_account_info(profile_name)
        username = self.extract_username(arn)
        
        print(f"✅ Successfully switched to profile '{profile_name}'")
        print(f"   Account: {account_id}")
        print(f"   User: {username}")
        
        # Show how to make this permanent
        print(f"\n💡 To use with CDK/tools in current shell:")
        print(f"   eval \"$(awsprofile {profile_name} --shell)\"")
        print(f"\n💡 Or add this function to ~/.zshrc:")
        print("   awsp() { eval \"$(awsprofile \"$1\" --shell)\"; }")
        
        return True
    
    def interactive_mode(self) -> None:
        """Interactive profile selection mode."""
        profiles = self.get_available_profiles()
        
        if not profiles:
            return
        
        while True:
            self.show_profiles()
            
            print(f"\n🔄 Options:")
            print(f"   1-{len(profiles)}: Switch to profile")
            print(f"   d: Delete a profile")
            print(f"   r: Refresh profile list")
            print(f"   q: Quit")
            
            try:
                choice = input("\nSelect option: ").strip().lower()
                
                if choice == 'q':
                    print("👋 Goodbye!")
                    break
                elif choice == 'r':
                    print("🔄 Refreshing...")
                    continue
                elif choice == 'd':
                    # Delete profile mode
                    print("\n🗑️  Profile deletion mode")
                    print("Available profiles:")
                    for i, profile in enumerate(profiles, 1):
                        print(f"   {i}. {profile}")
                    
                    try:
                        del_choice = input("\nEnter profile number to delete (or 'c' to cancel): ").strip().lower()
                        if del_choice == 'c':
                            continue
                        
                        del_num = int(del_choice)
                        if 1 <= del_num <= len(profiles):
                            profile_to_delete = profiles[del_num - 1]
                            self.delete_profile(profile_to_delete)
                            # Refresh profiles list after deletion
                            profiles = self.get_available_profiles()
                        else:
                            print(f"❌ Please enter a number between 1 and {len(profiles)}")
                    except ValueError:
                        print("❌ Please enter a valid number")
                    continue
                
                # Try to convert to number for profile selection
                try:
                    profile_num = int(choice)
                    if 1 <= profile_num <= len(profiles):
                        selected_profile = profiles[profile_num - 1]
                        if self.switch_profile(selected_profile):
                            # Ask if user wants to continue or exit
                            continue_choice = input("\nContinue managing profiles? (y/n): ").strip().lower()
                            if continue_choice in ['n', 'no']:
                                break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(profiles)}")
                except ValueError:
                    print("❌ Please enter a valid number, 'd' to delete, 'r' to refresh, or 'q' to quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break


def show_help():
    """Show help message."""
    print("AWS Profile Switcher v{}".format(__version__))
    print("\nA simple tool to view, switch, and delete AWS profiles.")
    print("\nUsage:")
    print("  awsprofile                    # Interactive mode")
    print("  awsprofile list               # Show all profiles")
    print("  awsprofile <profile>          # Switch to specific profile")
    print("  awsprofile <profile> --shell  # Output shell export command")
    print("  awsprofile delete <profile>   # Delete a profile")
    print("  awsprofile --help             # Show this help")
    print("  awsprofile --version          # Show version")
    print("\nExamples:")
    print("  awsprofile                    # Start interactive mode")
    print("  awsprofile work               # Switch to 'work' profile")
    print("  awsprofile list               # List all available profiles")
    print("  awsprofile delete old-profile # Delete 'old-profile'")
    print("  eval \"$(awsprofile work --shell)\" # Switch for current shell")
    print("\nShell Integration:")
    print("  Add this to your ~/.zshrc or ~/.bashrc:")
    print("  awsp() { eval \"$(awsprofile \"$1\" --shell)\"; }")
    print("  Then use: awsp work")


def generate_shell_integration():
    """Generate shell integration commands."""
    integration = r'''
# AWS Profile Switcher Shell Integration
# Add this to your ~/.zshrc or ~/.bashrc

awsp() {
    if [ $# -eq 0 ]; then
        # No arguments - show interactive mode
        awsprofile
    else
        # Switch profile and export to current shell
        local output
        output=$(awsprofile "$1" --shell 2>&1)
        
        if echo "$output" | grep -q "export AWS_PROFILE"; then
            # Success - evaluate the export command
            eval "$output"
            echo "✅ Switched to AWS profile: $1"
            echo "   Use 'aws sts get-caller-identity' to verify"
        else
            # Error - show the error message
            echo "$output"
        fi
    fi
}

# Tab completion for awsp function (bash)
_awsp_completion() {
    local profiles
    profiles=$(awsprofile list 2>/dev/null | grep "^  [0-9]" | sed 's/^.*[0-9]\. //' | cut -d' ' -f1)
    COMPREPLY=($(compgen -W "$profiles" -- "${COMP_WORDS[1]}"))
}
complete -F _awsp_completion awsp

# Alternative short aliases
alias awsl="awsprofile list"     # List profiles
alias awsi="awsprofile"          # Interactive mode
'''
    return integration


def main():
    """Main CLI entry point."""
    manager = AWSProfileManager()
    
    if len(sys.argv) == 1:
        # No arguments - start interactive mode
        manager.interactive_mode()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        
        if arg in ['--help', '-h']:
            show_help()
        elif arg in ['--version', '-v']:
            print(f"AWS Profile Switcher v{__version__}")
        elif arg == 'list':
            manager.show_profiles()
        elif arg == '--shell-integration':
            print(generate_shell_integration())
        else:
            # Switch to specific profile
            manager.switch_profile(arg)
    elif len(sys.argv) == 3:
        command = sys.argv[1]
        arg = sys.argv[2]
        
        if command == 'delete':
            manager.delete_profile(arg)
        elif arg == '--shell':
            # Switch profile in shell mode
            manager.switch_profile(command, shell_mode=True)
        else:
            print("❌ Invalid arguments.")
            print("💡 Use 'awsprofile --help' for usage information.")
    else:
        print("❌ Too many arguments.")
        print("💡 Use 'awsprofile --help' for usage information.")


if __name__ == "__main__":
    main()