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
import getpass

__version__ = "1.4.0"

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
    
    def create_profile(self, profile_name: str) -> bool:
        """Create a new AWS profile interactively."""
        if not profile_name:
            print("❌ Profile name cannot be empty.")
            return False
        
        # Check if profile already exists
        profiles = self.get_available_profiles()
        if profile_name in profiles:
            print(f"❌ Profile '{profile_name}' already exists.")
            overwrite = input("   Overwrite existing profile? (y/n): ").strip().lower()
            if overwrite not in ['y', 'yes']:
                print("❌ Profile creation cancelled.")
                return False
        
        print(f"\n🔧 Creating AWS profile: '{profile_name}'")
        print("=" * 50)
        
        try:
            # Collect credentials
            print("📝 Enter AWS credentials:")
            access_key = input("   AWS Access Key ID: ").strip()
            if not access_key:
                print("❌ Access Key ID cannot be empty.")
                return False
            
            # Hide secret key input (basic implementation)
            try:
                secret_key = getpass.getpass("   AWS Secret Access Key: ").strip()
            except KeyboardInterrupt:
                print("\n❌ Profile creation cancelled.")
                return False
            
            if not secret_key:
                print("❌ Secret Access Key cannot be empty.")
                return False
            
            region = input("   Default region (us-east-1): ").strip() or "us-east-1"
            output_format = input("   Output format (json): ").strip() or "json"
            
            print(f"\n🔍 Testing credentials for profile '{profile_name}'...")
            
            # Create temporary credentials file to test
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.credentials', delete=False) as temp_creds:
                temp_creds.write(f"""[{profile_name}]
aws_access_key_id = {access_key}
aws_secret_access_key = {secret_key}
region = {region}
""")
                temp_creds_path = temp_creds.name
            
            # Test the credentials
            test_cmd = [
                'aws', 'sts', 'get-caller-identity',
                '--profile', profile_name,
                '--output', 'json'
            ]
            
            # Temporarily set AWS_SHARED_CREDENTIALS_FILE
            old_creds_file = os.environ.get('AWS_SHARED_CREDENTIALS_FILE')
            os.environ['AWS_SHARED_CREDENTIALS_FILE'] = temp_creds_path
            
            try:
                result = subprocess.run(
                    test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    # Parse account info
                    data = json.loads(result.stdout)
                    account_id = data.get('Account', 'Unknown')
                    user_arn = data.get('Arn', 'Unknown')
                    username = self.extract_username(user_arn)
                    
                    print(f"✅ Credentials validated successfully!")
                    print(f"   Account: {account_id}")
                    print(f"   User: {username}")
                else:
                    print(f"❌ Credential validation failed:")
                    print(f"   {result.stderr.strip()}")
                    return False
                    
            finally:
                # Restore original credentials file setting
                if old_creds_file:
                    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = old_creds_file
                elif 'AWS_SHARED_CREDENTIALS_FILE' in os.environ:
                    del os.environ['AWS_SHARED_CREDENTIALS_FILE']
                
                # Clean up temp file
                try:
                    os.unlink(temp_creds_path)
                except:
                    pass
            
            # Backup existing files
            if self.credentials_path.exists():
                backup_creds = self.credentials_path.with_suffix('.credentials.backup')
                shutil.copy2(self.credentials_path, backup_creds)
                print(f"📋 Backed up credentials to {backup_creds}")
            
            if self.config_path.exists():
                backup_config = self.config_path.with_suffix('.config.backup')
                shutil.copy2(self.config_path, backup_config)
                print(f"📋 Backed up config to {backup_config}")
            
            # Ensure AWS directory exists
            self.credentials_path.parent.mkdir(exist_ok=True)
            
            # Update credentials file
            creds_config = configparser.ConfigParser()
            if self.credentials_path.exists():
                creds_config.read(self.credentials_path)
            
            if not creds_config.has_section(profile_name):
                creds_config.add_section(profile_name)
            
            creds_config.set(profile_name, 'aws_access_key_id', access_key)
            creds_config.set(profile_name, 'aws_secret_access_key', secret_key)
            
            with open(self.credentials_path, 'w') as f:
                creds_config.write(f)
            print(f"✅ Added '{profile_name}' to credentials file")
            
            # Update config file
            config_config = configparser.ConfigParser()
            if self.config_path.exists():
                config_config.read(self.config_path)
            
            # Profile sections in config are named "profile profilename" (except default)
            config_section = f"profile {profile_name}" if profile_name != 'default' else profile_name
            
            if not config_config.has_section(config_section):
                config_config.add_section(config_section)
            
            config_config.set(config_section, 'region', region)
            config_config.set(config_section, 'output', output_format)
            
            with open(self.config_path, 'w') as f:
                config_config.write(f)
            print(f"✅ Added '{profile_name}' to config file")
            
            print(f"\n🎉 Successfully created profile '{profile_name}'!")
            print(f"💡 Test it with: awsprofile -p {profile_name}")
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ Credential validation timed out. Check your network connection.")
            return False
        except json.JSONDecodeError:
            print("❌ Invalid response from AWS. Check your credentials.")
            return False
        except Exception as e:
            print(f"❌ Error creating profile: {str(e)}")
            return False

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
    
    def list_profiles(self, names_only: bool = False) -> None:
        """List all available AWS profiles with account information."""
        profiles = self.get_available_profiles()
        current_profile = self.get_current_profile()
        
        if not profiles:
            print("❌ No AWS profiles found.")
            print("💡 Create one with: aws configure --profile <name>")
            return
        
        if names_only:
            for profile in profiles:
                print(profile)
            return
        
        print("📋 Available profiles ({} total):".format(len(profiles)))
        print("----------------------------------------")
        
        for i, profile in enumerate(profiles, 1):
            is_current = profile == current_profile
            marker = "✅ " if is_current else "   "
            
            print(f"{marker}{i}. {profile}")
            
            # Get account info for each profile
            account_info = self.get_account_info(profile)
            if account_info:
                account_id, username = account_info
                print(f"       Account: {account_id}")
                if username != "Unknown":
                    print(f"       User: {username}")
            else:
                print("       ❌ Invalid/expired credentials")
            print()

    def show_current_profile(self) -> None:
        """Show the current AWS profile with account information."""
        current_profile = self.get_current_profile()
        print(f"📍 Current profile: {current_profile}")
        
        account_info = self.get_account_info(current_profile)
        if account_info:
            account_id, username = account_info
            print(f"   Account: {account_id}")
            if username != "Unknown":
                print(f"   User: {username}")
        else:
            print("   ❌ Invalid/expired credentials")
    
    def setup_shell_integration(self) -> bool:
        """Set up shell integration automatically."""
        shell = os.environ.get('SHELL', '').split('/')[-1]
        home = Path.home()
        
        if shell == 'zsh':
            shell_config = home / '.zshrc'
        elif shell == 'bash':
            shell_config = home / '.bashrc'
        else:
            print(f"❌ Unsupported shell: {shell}")
            print("💡 Supported shells: bash, zsh")
            return False
        
        # Shell integration functions
        integration_code = '''
# AWS Profile Switcher - Auto-generated
awsp() { 
    if [ $# -eq 0 ]; then
        echo "❌ Profile name required"
        echo "💡 Usage: awsp <profile-name>"
        echo "💡 Available profiles:"
        awsprofile list --names-only
        return 1
    fi
    
    local output
    output=$(awsprofile -p "$1" --shell 2>&1)
    
    if echo "$output" | grep -q "export AWS_PROFILE"; then
        # Success - evaluate the export command
        eval "$output"
        echo "✅ Switched to AWS profile: $1"
    else
        # Error - show the error message
        echo "$output"
        return 1
    fi
}

awsl() { awsprofile list; }
awsi() { awsprofile; }
awsc() { awsprofile current; }
awsclear() { unset AWS_PROFILE; echo "✅ Cleared AWS_PROFILE"; }
'''
        
        # Check if already set up
        if shell_config.exists():
            content = shell_config.read_text()
            if 'AWS Profile Switcher - Auto-generated' in content:
                print("✅ Shell integration already set up!")
                return True
        
        print(f"🔧 Setting up shell integration for {shell}...")
        
        try:
            # Backup existing config
            if shell_config.exists():
                backup_path = shell_config.with_suffix(f'{shell_config.suffix}.backup')
                shutil.copy2(shell_config, backup_path)
                print(f"📋 Backed up {shell_config} to {backup_path}")
            
            # Append integration code
            with open(shell_config, 'a') as f:
                f.write('\n' + integration_code)
            
            print(f"✅ Added shell integration to {shell_config}")
            print("\n🎉 Setup complete!")
            print(f"💡 Run: source {shell_config}")
            print("💡 Or restart your terminal")
            print("\nThen use these commands:")
            print("  awsp <profile>  - Switch profiles")
            print("  awsl           - List profiles") 
            print("  awsi           - Interactive mode")
            print("  awsc           - Show current profile")
            print("  awsclear       - Clear profile")
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up shell integration: {str(e)}")
            return False

    def check_shell_integration(self) -> bool:
        """Check if shell integration is available."""
        try:
            result = subprocess.run(['which', 'awsp'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def switch_profile(self, profile_name: str, shell_mode: bool = False) -> bool:
        """Switch to a specific AWS profile."""
        # Check if profile exists
        profiles = self.get_available_profiles()
        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found.")
            print(f"💡 Available profiles: {', '.join(profiles)}")
            return False
        
        # If profile exists but it's None (no active profile), just set it
        if self.get_current_profile() == profile_name:
            if shell_mode:
                print(f"export AWS_PROFILE={profile_name}")
            else:
                print(f"✅ Already using AWS profile: {profile_name}")
            return True
        
        # Get account info for validation
        account_info = self.get_account_info(profile_name)
        if not account_info:
            print(f"❌ Invalid or expired credentials for profile '{profile_name}'")
            return False
        
        account_id, username = account_info
        
        if shell_mode:
            # Output shell export command
            print(f"export AWS_PROFILE={profile_name}")
        else:
            # Set environment variable for current process
            os.environ['AWS_PROFILE'] = profile_name
            print(f"✅ Switched to AWS profile: {profile_name}")
            print(f"   Account: {account_id}")
            if username != "Unknown":
                print(f"   User: {username}")
            
            print(f"\n💡 To use with CDK/tools in current shell:")
            print(f"   eval \"$(awsprofile -p {profile_name} --shell)\"")
            print(f"\n💡 Or add shell integration with:")
            print(f"   awsprofile setup-shell")
        
        return True
    
    def interactive_mode(self) -> None:
        """Interactive profile selection mode."""
        profiles = self.get_available_profiles()
        
        if not profiles:
            return
        
        while True:
            current = self.get_current_profile()
            
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
            
            print(f"\n🔄 Options:")
            print(f"   1-{len(profiles)}: Switch to profile")
            print(f"   c: Create a new profile")
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
                elif choice == 'c':
                    # Create profile mode
                    print("\n🔧 Profile creation mode")
                    profile_name = input("Enter new profile name: ").strip()
                    if profile_name:
                        if self.create_profile(profile_name):
                            # Refresh profiles list after creation
                            profiles = self.get_available_profiles()
                        else:
                            print("❌ Profile creation failed.")
                    else:
                        print("❌ Profile name cannot be empty.")
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
                    print("❌ Please enter a valid number, 'c' to create, 'd' to delete, 'r' to refresh, or 'q' to quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break


def main():
    """Main entry point for the CLI."""
    import argparse
    
    # Create the main parser
    parser = argparse.ArgumentParser(
        prog='awsprofile',
        description='AWS Profile Switcher - Manage AWS profiles with ease',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  awsprofile                         # Interactive mode
  awsprofile list                    # List all profiles
  awsprofile current                 # Show current profile  
  awsprofile setup-shell             # Setup shell integration (one-time)
  awsprofile create dev-profile      # Create new profile
  awsprofile delete old-profile      # Delete profile
  awsprofile -p work                 # Switch to 'work' profile
  awsprofile -p work --shell         # Switch with shell export

Shell Integration Commands (after running 'awsprofile setup-shell'):
  awsp <profile>                     # Switch to profile (persists in shell)
  awsl                               # List all profiles  
  awsi                               # Interactive mode
  awsc                               # Show current profile
  awsclear                           # Clear AWS_PROFILE environment variable
  
Quick Start:
  1. awsprofile setup-shell          # One-time setup
  2. source ~/.zshrc                 # Reload shell config  
  3. awsp my-profile                 # Switch profiles easily
        """
    )
    
    # Add the profile flag
    parser.add_argument('-p', '--profile', 
                       metavar='NAME',
                       help='Switch to specified profile')
    
    # Add shell flag (only works with -p)
    parser.add_argument('--shell', 
                       action='store_true',
                       help='Output shell export command (use with -p)')
    
    # Add version flag
    parser.add_argument('--version', 
                       action='version', 
                       version=f'AWS Profile Switcher v{__version__}')
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', 
                                      help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', 
                                       help='List all available profiles')
    list_parser.add_argument('--names-only', 
                            action='store_true',
                            help='Output only profile names')
    
    # Current command  
    subparsers.add_parser('current', 
                         help='Show current active profile')
    
    # Setup-shell command
    subparsers.add_parser('setup-shell', 
                         help='Set up shell integration (one-time setup)')
    
    # Create command
    create_parser = subparsers.add_parser('create', 
                                         help='Create a new profile')
    create_parser.add_argument('name', 
                              help='Name of the profile to create')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', 
                                         help='Delete an existing profile')
    delete_parser.add_argument('name', 
                              help='Name of the profile to delete')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create manager
    manager = AWSProfileManager()
    
    # Handle profile switching (can be combined with commands or standalone)
    if args.profile:
        if args.shell:
            manager.switch_profile(args.profile, shell_mode=True)
        else:
            manager.switch_profile(args.profile)
        return
    
    # Handle subcommands
    if args.command == 'list':
        if hasattr(args, 'names_only') and args.names_only:
            manager.list_profiles(names_only=True)
        else:
            manager.list_profiles()
    elif args.command == 'current':
        manager.show_current_profile()
    elif args.command == 'setup-shell':
        success = manager.setup_shell_integration()
        if not success:
            sys.exit(1)
    elif args.command == 'create':
        manager.create_profile(args.name)
    elif args.command == 'delete':
        manager.delete_profile(args.name)
    elif args.command is None and not args.profile:
        # No command and no profile - start interactive mode
        manager.interactive_mode()
    elif args.shell and not args.profile:
        # --shell flag without -p doesn't make sense
        print("❌ --shell flag requires -p/--profile flag")
        print("💡 Usage: awsprofile -p <profile-name> --shell")
    else:
        # This shouldn't happen with argparse, but just in case
        parser.print_help()


if __name__ == "__main__":
    main()