#!/usr/bin/env python3
"""
AWS Profile Switcher CLI Tool
A simple, interactive tool to view and switch between AWS profiles.

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

__version__ = "1.0.0"

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
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch to a specific AWS profile."""
        if not self.validate_profile(profile_name):
            return False
        
        # Set the environment variable for this session
        os.environ['AWS_PROFILE'] = profile_name
        
        # Get account info for confirmation
        account_id, arn = self.get_account_info(profile_name)
        username = self.extract_username(arn)
        
        print(f"✅ Successfully switched to profile '{profile_name}'")
        print(f"   Account: {account_id}")
        print(f"   User: {username}")
        
        # Show how to make this permanent
        print(f"\n💡 To make this permanent for your terminal session:")
        print(f"   export AWS_PROFILE={profile_name}")
        print(f"\n💡 To make it permanent globally:")
        print(f"   echo 'export AWS_PROFILE={profile_name}' >> ~/.zshrc")
        
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
                
                # Try to convert to number
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
                    print("❌ Please enter a valid number, 'r' to refresh, or 'q' to quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break


def show_help():
    """Show help message."""
    print("AWS Profile Switcher v{}".format(__version__))
    print("\nA simple tool to view and switch between AWS profiles.")
    print("\nUsage:")
    print("  awsprofile              # Interactive mode")
    print("  awsprofile list         # Show all profiles")
    print("  awsprofile <profile>    # Switch to specific profile")
    print("  awsprofile --help       # Show this help")
    print("  awsprofile --version    # Show version")
    print("\nExamples:")
    print("  awsprofile              # Start interactive mode")
    print("  awsprofile work         # Switch to 'work' profile")
    print("  awsprofile list         # List all available profiles")


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
        else:
            # Switch to specific profile
            manager.switch_profile(arg)
    else:
        print("❌ Too many arguments.")
        print("💡 Use 'awsprofile --help' for usage information.")


if __name__ == "__main__":
    main()