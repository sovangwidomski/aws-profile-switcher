# AWS Profile Switcher v1.5.1

A dead-simple tool to list, switch, and manage AWS profiles for local development.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![AWS CLI](https://img.shields.io/badge/AWS-CLI-orange.svg)](https://aws.amazon.com/cli/)

## What It Does

1. **Lists your AWS profiles** - see what's configured with account details
2. **Shows current profile** - know which profile is active  
3. **Switches profiles automatically** - makes the selected profile the default
4. **Manages profiles** - create, delete, and clear profiles easily

## Installation

### Option 1: Install from GitHub (Recommended)
```bash
# Install directly from GitHub (replace with your actual repository URL)
pip install git+https://github.com/sovangwidomski/aws-profile-switcher.git

# Verify installation
awsprofile --version
```

### Option 2: Install from Source
```bash
# Clone the repository (replace with your actual repository URL)
git clone https://github.com/sovangwidomski/aws-profile-switcher.git
cd aws-profile-switcher

# Install
pip install .

# Verify installation
awsprofile --version
```

### First Time Setup
```bash
# Check if you have AWS profiles configured
aws configure list-profiles

# If no profiles exist, create your first one
aws configure

# Test the tool
awsprofile list
```

## Installation Complete! 

## Quick Start

```bash
# See what profiles you have
awsprofile list

# Switch to a profile automatically
awsprofile -p your-profile-name

# Clear current profile
awsprofile clear

# Interactive mode (recommended for discovery)
awsprofile
```

## Usage

### Interactive Mode (Recommended)
```bash
awsprofile
```

Shows a menu where you can:
- **Switch profiles** by selecting a number
- **Create new profiles** with `c`
- **Delete profiles** with `d`
- **Clear current profile** with `x`
- **Refresh the list** with `r`
- **Quit** with `q`

### Command Line Interface
```bash
# Help and version
awsprofile -h / --help              # Show help
awsprofile -v / --version           # Show version

# Profile information
awsprofile list                     # List all profiles with details
awsprofile current                  # Show current active profile
awsprofile clear                    # Clear current profile (unset)

# Profile switching (automatic)
awsprofile -p your-profile-name     # Switch to profile automatically
awsprofile --profile dev-account    # Switch to profile automatically

# Profile management
awsprofile create my-new-profile    # Create new profile interactively
awsprofile delete old-profile       # Delete profile with confirmation
```

## Example Interactive Session

```
🔧 AWS Profile Switcher v1.5.1
==================================================
📍 Current profile: company-dev
   Account: 123456789012
   User: arn:aws:iam::123456789012:user/my-username

📋 Available profiles (3 total):
----------------------------------------
✅  1. company-dev
       Account: 123456789012
   2. personal-account  
       Account: 987654321098
   3. client-staging
       Account: 555666777888

🔄 Options:
   1-3: Switch to profile
   c: Create a new profile
   d: Delete a profile
   x: Clear current profile
   r: Refresh profile list
   q: Quit

Select option: 2

✅ Switched to AWS profile: personal-account
   Account: 987654321098
   User: arn:aws:iam::987654321098:user/personal-user

🔄 Profile is now active for all AWS tools (CDK, CLI, etc.)
```

## Example Command Line Usage

```bash
# See what profiles you have
awsprofile list

# Switch to your work profile  
awsprofile -p company-staging
# ✅ Profile automatically activated!

# Verify it worked
aws configure list   # Shows company-staging credentials as default
cdk deploy          # Uses company-staging profile automatically

# Create a new profile
awsprofile create client-project
# Prompts for AWS credentials interactively

# Delete an old profile
awsprofile delete unused-profile
# Asks for confirmation before deleting

# Clear current profile
awsprofile clear
# Unsets the default profile
```

## Automatic Profile Switching

After switching, all AWS tools automatically use the new profile:
```bash
aws configure list    # Shows the new profile as default
cdk deploy           # Uses the switched profile
aws s3 ls            # Uses the switched profile
terraform plan       # Uses the switched profile
sam deploy           # Uses the switched profile
```

Perfect for CDK development:
```bash
cd my-cdk-project
python -m venv .venv
source .venv/bin/activate

awsprofile -p my-dev-account    # Switch profile
cdk deploy                      # Deploy with selected profile
```

## How It Works

The tool copies your selected profile's credentials and settings to the `[default]` section of your AWS config files (`~/.aws/config` and `~/.aws/credentials`). This makes AWS CLI, CDK, and all AWS tools use that profile automatically without needing environment variables or additional configuration.

## Why This Approach?

- **Automatic**: No export commands or environment variables needed
- **Simple**: Just select a profile and it works immediately
- **Reliable**: Uses AWS CLI's native configuration system
- **Compatible**: Works with CDK, AWS CLI, Terraform, and all AWS tools
- **Persistent**: Stays active until you switch to another profile
- **Complete**: Full profile management (create, read, update, delete)

## Requirements

- Python 3.6+
- AWS CLI installed and available in PATH
- At least one AWS profile configured (`aws configure`)

## Profile Name Examples

All profile names in this documentation (like `company-dev`, `personal-account`, etc.) are examples. Replace them with your actual AWS profile names. Use `awsprofile list` to see your configured profiles.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog
### v1.5.1 (2025-06-20)
- Fix refresh not redisplaying menu
- Fix profile switching exiting interactive mode

### v1.5.0 (2025-06-19)
- 🎯 **Back to simplicity**: Automatic profile switching without shell complexity
- ✅ **Full CRUD operations**: Create, read, update, delete profiles
- 🔧 **Improved CLI**: Better argument parsing with `-h`, `--help`, `-v`, `--version`
- 🎨 **Clean interface**: Simplified interactive mode and command structure
- 🚀 **CDK ready**: Perfect for CDK development workflows

### v1.4.0 (2025-06-19)
- 🎯 Namespace conflicts eliminated with explicit `-p` flag
- 🛡️ Robust argument parsing with proper subcommands
- 📚 Comprehensive help and shell integration
- ⚡ Support for any profile name without conflicts

### v1.3.0 (2025-06-19)
- 🎯 One-command setup with `awsprofile setup-shell`
- 🧠 Smart shell detection and auto-configuration
- 📝 Auto tab completion included

### v1.2.0 (2025-06-19)
- ✨ Interactive profile creation with credential validation
- ✨ Command-line profile creation and deletion
- 🔧 Enhanced backup system and error handling

### v1.1.0 (2025-06-19)
- ✨ Profile deletion with automatic backups
- ✨ Shell integration for CDK support
- ✨ Tab completion for bash and zsh

### v1.0.0 (2025-06-18)
- 🎉 Initial release with interactive profile switching
- ✅ Profile validation and account information display
- 🔧 Comprehensive error handling