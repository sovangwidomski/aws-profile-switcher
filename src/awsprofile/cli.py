#!/usr/bin/env python3
"""
AWS Profile Switcher v1.5.1
A simple tool to list and switch between AWS profiles with ease.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional

VERSION = "1.5.1"


def get_profiles() -> Dict[str, Dict]:
    """Get all available AWS profiles with their details."""
    profiles = {}
    
    try:
        # Get list of profiles from AWS CLI
        result = subprocess.run([
            'aws', 'configure', 'list-profiles'
        ], capture_output=True, text=True, check=True)
        
        profile_names = result.stdout.strip().split('\n')
        
        for profile_name in profile_names:
            if not profile_name.strip():
                continue
                
            profile_info = {}
            
            # Get account ID
            try:
                sts_result = subprocess.run([
                    'aws', 'sts', 'get-caller-identity',
                    '--profile', profile_name,
                    '--query', 'Account',
                    '--output', 'text'
                ], capture_output=True, text=True, timeout=10)
                
                if sts_result.returncode == 0:
                    profile_info['account'] = sts_result.stdout.strip()
                else:
                    profile_info['account'] = 'Invalid'
                    
                # Get user ARN
                user_result = subprocess.run([
                    'aws', 'sts', 'get-caller-identity',
                    '--profile', profile_name,
                    '--query', 'Arn',
                    '--output', 'text'
                ], capture_output=True, text=True, timeout=10)
                
                if user_result.returncode == 0:
                    profile_info['user'] = user_result.stdout.strip()
                else:
                    profile_info['user'] = 'Unknown'
                    
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                profile_info['account'] = 'Invalid'
                profile_info['user'] = 'The config profile could not be found'
            
            profiles[profile_name] = profile_info
    
    except subprocess.CalledProcessError:
        # aws CLI not available or no profiles configured
        pass
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install AWS CLI first.")
        sys.exit(1)
    
    return profiles


def get_current_profile() -> Optional[str]:
    """Get the name of the currently active AWS profile."""
    try:
        # Check AWS_PROFILE environment variable first
        env_profile = os.environ.get('AWS_PROFILE')
        if env_profile:
            return env_profile
        
        # Check what AWS CLI reports as current
        result = subprocess.run([
            'aws', 'configure', 'list'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'profile' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        profile_name = parts[1]
                        if profile_name != '<not' and profile_name != 'set>':
                            return profile_name
        
        return None
        
    except Exception:
        return None


def switch_profile(profile_name: str) -> bool:
    """Switch to the specified AWS profile by making it the default."""
    profiles = get_profiles()
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found.")
        if profiles:
            print(f"💡 Available profiles: {', '.join(profiles.keys())}")
        return False
    
    try:
        # Copy the selected profile's settings to [default] sections
        config_file = Path.home() / '.aws' / 'config'
        credentials_file = Path.home() / '.aws' / 'credentials'
        
        # Get the selected profile's settings using aws configure
        region_result = subprocess.run([
            'aws', 'configure', 'get', 'region', '--profile', profile_name
        ], capture_output=True, text=True)
        
        output_result = subprocess.run([
            'aws', 'configure', 'get', 'output', '--profile', profile_name
        ], capture_output=True, text=True)
        
        # Set these as the default
        if region_result.returncode == 0:
            subprocess.run([
                'aws', 'configure', 'set', 'region', region_result.stdout.strip()
            ], check=True)
        
        if output_result.returncode == 0:
            subprocess.run([
                'aws', 'configure', 'set', 'output', output_result.stdout.strip()
            ], check=True)
        
        # Copy credentials to default
        key_result = subprocess.run([
            'aws', 'configure', 'get', 'aws_access_key_id', '--profile', profile_name
        ], capture_output=True, text=True)
        
        secret_result = subprocess.run([
            'aws', 'configure', 'get', 'aws_secret_access_key', '--profile', profile_name
        ], capture_output=True, text=True)
        
        if key_result.returncode == 0:
            subprocess.run([
                'aws', 'configure', 'set', 'aws_access_key_id', key_result.stdout.strip()
            ], check=True)
        
        if secret_result.returncode == 0:
            subprocess.run([
                'aws', 'configure', 'set', 'aws_secret_access_key', secret_result.stdout.strip()
            ], check=True)
        
        profile_info = profiles[profile_name]
        print(f"✅ Switched to AWS profile: {profile_name}")
        print(f"   Account: {profile_info.get('account', 'Unknown')}")
        print(f"   User: {profile_info.get('user', 'Unknown')}")
        print()
        print("🔄 Profile is now active for all AWS tools (CDK, CLI, etc.)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to switch profile: {e}")
        return False
    except Exception as e:
        print(f"❌ Error switching profile: {e}")
        return False


def show_current_profile():
    """Display the currently active AWS profile."""
    try:
        # Check what AWS CLI thinks is the current profile
        result = subprocess.run([
            'aws', 'configure', 'list'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'profile' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        profile_name = parts[1]
                        if profile_name != '<not' and profile_name != 'set>':
                            print(f"📍 Current profile: {profile_name}")
                            
                            # Get additional info about this profile
                            profiles = get_profiles()
                            if profile_name in profiles:
                                profile_info = profiles[profile_name]
                                print(f"   Account: {profile_info.get('account', 'Unknown')}")
                                print(f"   User: {profile_info.get('user', 'Unknown')}")
                            return
            
            # If we get here, no profile was found
            print("📍 No AWS profile currently active")
            print("💡 Switch to a profile with: awsprofile -p your-profile-name")
        else:
            print("❌ Could not determine current profile")
            print("💡 Make sure AWS CLI is installed and configured")
            
    except Exception as e:
        print(f"❌ Error checking current profile: {e}")


def list_profiles():
    """List all available AWS profiles."""
    profiles = get_profiles()
    current = get_current_profile()
    
    if not profiles:
        print("❌ No AWS profiles found.")
        print("💡 Run 'aws configure' to create your first profile.")
        return
    
    print(f"📋 Available profiles ({len(profiles)} total):")
    print("-" * 40)
    
    for i, (name, info) in enumerate(profiles.items(), 1):
        marker = "✅" if name == current else "  "
        print(f"{marker} {i}. {name}")
        print(f"       Account: {info.get('account', 'Unknown')}")
        print(f"       User: {info.get('user', 'Unknown')}")


def create_profile(profile_name: str):
    """Create a new AWS profile interactively."""
    print(f"🔧 Creating new profile: {profile_name}")
    
    try:
        access_key = input("AWS Access Key ID: ").strip()
        if not access_key:
            print("❌ Access Key ID is required")
            return False
            
        secret_key = input("AWS Secret Access Key: ").strip()
        if not secret_key:
            print("❌ Secret Access Key is required")
            return False
            
        region = input("Default region [us-east-1]: ").strip() or "us-east-1"
        output_format = input("Default output format [json]: ").strip() or "json"
        
        # Use AWS CLI to configure the profile
        subprocess.run([
            'aws', 'configure', 'set', 'aws_access_key_id', access_key,
            '--profile', profile_name
        ], check=True)
        
        subprocess.run([
            'aws', 'configure', 'set', 'aws_secret_access_key', secret_key,
            '--profile', profile_name
        ], check=True)
        
        subprocess.run([
            'aws', 'configure', 'set', 'region', region,
            '--profile', profile_name
        ], check=True)
        
        subprocess.run([
            'aws', 'configure', 'set', 'output', output_format,
            '--profile', profile_name
        ], check=True)
        
        print(f"✅ Profile '{profile_name}' created successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n❌ Profile creation cancelled")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create profile: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        return False


def delete_profile(profile_name: str):
    """Delete an AWS profile."""
    profiles = get_profiles()
    
    if profile_name not in profiles:
        print(f"❌ Profile '{profile_name}' not found.")
        if profiles:
            print(f"💡 Available profiles: {', '.join(profiles.keys())}")
        return False
    
    # Confirm deletion
    try:
        confirm = input(f"❓ Delete profile '{profile_name}'? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Deletion cancelled")
            return False
    except KeyboardInterrupt:
        print("\n❌ Deletion cancelled")
        return False
    
    try:
        # Remove from both credentials and config files
        config_file = Path.home() / '.aws' / 'config'
        credentials_file = Path.home() / '.aws' / 'credentials'
        
        # Remove from config
        if config_file.exists():
            content = config_file.read_text()
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for line in lines:
                if line.strip() == f'[profile {profile_name}]':
                    skip = True
                    continue
                elif line.startswith('[') and skip:
                    skip = False
                
                if not skip:
                    new_lines.append(line)
            
            config_file.write_text('\n'.join(new_lines))
        
        # Remove from credentials
        if credentials_file.exists():
            content = credentials_file.read_text()
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for line in lines:
                if line.strip() == f'[{profile_name}]':
                    skip = True
                    continue
                elif line.startswith('[') and skip:
                    skip = False
                
                if not skip:
                    new_lines.append(line)
            
            credentials_file.write_text('\n'.join(new_lines))
        
        print(f"✅ Profile '{profile_name}' deleted successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to delete profile: {e}")
        return False


def create_profile_interactive():
    """Create a profile interactively."""
    try:
        profile_name = input("Profile name: ").strip()
        if not profile_name:
            print("❌ Profile name is required")
            return False
        
        # Check if profile already exists
        profiles = get_profiles()
        if profile_name in profiles:
            print(f"❌ Profile '{profile_name}' already exists")
            return False
        
        return create_profile(profile_name)
        
    except KeyboardInterrupt:
        print("\n❌ Profile creation cancelled")
        return False


def clear_profile():
    """Clear the current AWS profile (unset default profile)."""
    try:
        config_file = Path.home() / '.aws' / 'config'
        credentials_file = Path.home() / '.aws' / 'credentials'
        
        # Clear default section from credentials file
        if credentials_file.exists():
            content = credentials_file.read_text()
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for line in lines:
                if line.strip() == '[default]':
                    skip = True
                    continue
                elif line.startswith('[') and skip:
                    skip = False
                
                if not skip:
                    new_lines.append(line)
            
            credentials_file.write_text('\n'.join(new_lines))
        
        # Clear default section from config file
        if config_file.exists():
            content = config_file.read_text()
            lines = content.split('\n')
            new_lines = []
            skip = False
            
            for line in lines:
                if line.strip() == '[default]':
                    skip = True
                    continue
                elif line.startswith('[') and skip:
                    skip = False
                
                if not skip:
                    new_lines.append(line)
            
            config_file.write_text('\n'.join(new_lines))
        
        print("✅ AWS profile cleared successfully!")
        print("💡 No default profile is now active")
        print("💡 Use 'awsprofile -p profile-name' to switch to a profile")
        return True
        
    except Exception as e:
        print(f"❌ Failed to clear profile: {e}")
        return False


def delete_profile_interactive(profiles: Dict[str, Dict]):
    """Delete a profile interactively."""
    if not profiles:
        print("❌ No profiles available to delete")
        return False
    
    print("\n📋 Available profiles:")
    profile_list = list(profiles.keys())
    for i, name in enumerate(profile_list, 1):
        print(f"   {i}. {name}")
    
    try:
        choice = input("\nSelect profile to delete (number or name): ").strip()
        
        # Try as number first
        try:
            profile_num = int(choice)
            if 1 <= profile_num <= len(profile_list):
                profile_name = profile_list[profile_num - 1]
            else:
                print(f"❌ Invalid number. Please choose 1-{len(profile_list)}")
                return False
        except ValueError:
            # Treat as profile name
            profile_name = choice
        
        return delete_profile(profile_name)
        
    except KeyboardInterrupt:
        print("\n❌ Deletion cancelled")
        return False


def interactive_mode():
    """Run interactive profile selection."""
    while True:  # Main loop
        profiles = get_profiles()
        
        if not profiles:
            print("❌ No AWS profiles found.")
            print("💡 Run 'aws configure' to create your first profile.")
            return
        
        print(f"\n🔧 AWS Profile Switcher v{VERSION}")
        print("=" * 50)
        
        current = get_current_profile()
        if current:
            print(f"📍 Current profile: {current}")
            if current in profiles:
                profile_info = profiles[current]
                print(f"   Account: {profile_info.get('account', 'Unknown')}")
                print(f"   User: {profile_info.get('user', 'Unknown')}")
        else:
            print("📍 No profile currently active")
        
        print(f"\n📋 Available profiles ({len(profiles)} total):")
        print("-" * 40)
        
        profile_list = list(profiles.items())
        for i, (name, info) in enumerate(profile_list, 1):
            marker = "✅" if name == current else "  "
            print(f"{marker} {i}. {name}")
            print(f"       Account: {info.get('account', 'Unknown')}")
        
        print(f"\n🔄 Options:")
        print(f"   1-{len(profiles)}: Switch to profile")
        print(f"   c: Create a new profile")
        print(f"   d: Delete a profile")
        print(f"   x: Clear current profile")
        print(f"   r: Refresh profile list")
        print(f"   q: Quit")
        
        try:
            choice = input("\nSelect option: ").strip().lower()
            
            if choice == 'q':
                print("👋 Goodbye!")
                break
            elif choice == 'c':
                if create_profile_interactive():
                    print("🔄 Returning to main menu...")
                continue  # Go back to start of loop to redisplay menu
            elif choice == 'd':
                if delete_profile_interactive(profiles):
                    print("🔄 Returning to main menu...")
                continue  # Go back to start of loop to redisplay menu
            elif choice == 'x':
                clear_profile()
                print("🔄 Returning to main menu...")
                continue  # Go back to start of loop to redisplay menu
            elif choice == 'r':
                print("🔄 Profile list refreshed!")
                continue  # Go back to start of loop to redisplay menu
            else:
                # Try to parse as profile number
                try:
                    profile_num = int(choice)
                    if 1 <= profile_num <= len(profiles):
                        selected_profile = profile_list[profile_num - 1][0]
                        if switch_profile(selected_profile):
                            # Ask if user wants to continue managing profiles
                            try:
                                continue_choice = input("\n🔄 Continue managing profiles? (Y/n): ").strip().lower()
                                if continue_choice in ['n', 'no']:
                                    print("👋 Goodbye!")
                                    break
                                else:
                                    print("🔄 Returning to main menu...")
                                    continue  # Go back to start of loop
                            except KeyboardInterrupt:
                                print("\n👋 Goodbye!")
                                break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(profiles)}")
                        input("Press Enter to continue...")  # Pause so user can read error
                        continue
                except ValueError:
                    print("❌ Please enter a valid option")
                    input("Press Enter to continue...")  # Pause so user can read error
                    continue
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="AWS Profile Switcher - Simple AWS profile management",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  awsprofile                         # Interactive mode (recommended)
  awsprofile list                    # List all profiles
  awsprofile current                 # Show current profile
  awsprofile clear                   # Clear current profile  
  awsprofile -p your-profile-name    # Switch to profile automatically
  awsprofile create my-new-profile   # Create new profile
  awsprofile delete old-profile      # Delete profile

Workflow:
  1. awsprofile                      # Select profile interactively
  2. Profile automatically becomes default
  3. aws configure list              # Shows new profile as active
  4. cdk deploy                      # Uses the new profile automatically

Note: Replace 'your-profile-name', 'my-new-profile' etc. with your actual AWS profile names.
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version', 
        version=f'AWS Profile Switcher v{VERSION}'
    )
    
    parser.add_argument(
        '-p', '--profile',
        metavar='NAME',
        help='Switch to specified profile automatically'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands'
    )
    
    # List command
    subparsers.add_parser(
        'list',
        help='List all available profiles'
    )
    
    # Current command  
    subparsers.add_parser(
        'current',
        help='Show current active profile'
    )
    
    # Clear command
    subparsers.add_parser(
        'clear',
        help='Clear current profile (unset default)'
    )
    
    # Create profile command
    create_parser = subparsers.add_parser(
        'create',
        help='Create a new profile'
    )
    create_parser.add_argument(
        'profile_name',
        help='Name of the profile to create'
    )
    
    # Delete profile command
    delete_parser = subparsers.add_parser(
        'delete',
        help='Delete an existing profile'
    )
    delete_parser.add_argument(
        'profile_name',
        help='Name of the profile to delete'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.profile:
        # Profile switching
        switch_profile(args.profile)
    elif args.command == 'list':
        list_profiles()
    elif args.command == 'current':
        show_current_profile()
    elif args.command == 'clear':
        clear_profile()
    elif args.command == 'create':
        create_profile(args.profile_name)
    elif args.command == 'delete':
        delete_profile(args.profile_name)
    else:
        # No command specified - run interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()