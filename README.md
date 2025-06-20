# 🔧 AWS Profile Switcher v1.4.0

A simple, interactive command-line tool to create, view, switch, and delete AWS profiles with ease. Perfect for developers working with multiple AWS accounts, especially when using tools like AWS CDK in virtual environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS CLI](https://img.shields.io/badge/AWS-CLI-orange.svg)](https://aws.amazon.com/cli/)

> **🎯 NEW in v1.4.0**: Namespace conflicts eliminated! You can now have profiles named 'list', 'current', 'create', etc. 
> 
> Use **`awsprofile -p <profile-name>`** for explicit profile switching. All commands work reliably without conflicts!

## ⚡ Quick Start

```bash
# Install
pip3 install git+https://github.com/sovangwidomski/aws-profile-switcher.git

# One-time setup for shell integration
awsprofile setup-shell
source ~/.zshrc  # or ~/.bashrc

# See your actual profile names:
awsprofile list

# Switch profiles using the explicit -p flag:
awsprofile -p my-company-prod    # ← Use YOUR real profile name here
awsprofile -p personal-aws       # ← Use YOUR real profile name here  
awsprofile -p client-staging     # ← Use YOUR real profile name here
```

> **⚠️ Important**: "my-company-prod", "personal-aws" are just **examples**! 
> Use `awsprofile list` to see YOUR actual profile names, then use those with `-p`.

## ✨ New Features in v1.4.0

- 🎯 **Namespace conflicts eliminated** - Commands never conflict with profile names
- 🔧 **Explicit profile switching** - Use `-p` flag for clear intent: `awsprofile -p <name>`
- 🛡️ **Robust argument parsing** - Professional argparse-based CLI with proper subcommands
- 📚 **Comprehensive help** - Shell integration commands documented in `--help`
- ⚡ **Any profile name works** - Have profiles named 'list', 'current', 'create', etc.

## ✨ Features from Previous Versions

- 🔧 **Profile creation** - Create new AWS profiles interactively with credential validation (v1.2.0)
- 🛡️ **Credential testing** - Validates AWS credentials before saving profiles (v1.2.0)
- 📁 **Smart backups** - Automatic backup before modifying credentials/config files (v1.2.0)
- 💫 **Complete CRUD** - Create, Read, Update, Delete - full profile lifecycle management (v1.2.0)
- 🗑️ **Profile deletion** - Remove profiles safely with backup (v1.1.0)
- 🐚 **Shell integration** - Works with CDK, virtual environments, and any shell tools (v1.1.0)
- 🔄 **Better environment handling** - Properly exports AWS_PROFILE to current shell (v1.1.0)
- 📝 **Tab completion** - Auto-complete profile names in bash/zsh (v1.1.0)

## ✨ All Features

- ⚡ **Namespace conflict-free** - Commands and profiles never interfere 
- 🔧 **Create new AWS profiles** with interactive credential input and validation
- 📋 **List all available AWS profiles** with account information
- 🔄 **Interactive profile switching** with numbered selection
- 🗑️ **Safe profile deletion** with automatic backups
- ✅ **Profile validation** - tests credentials before switching
- 🎯 **Current profile highlighting** - see which profile is active
- ⚡ **Fast credential verification** - quick account ID lookup
- 🛡️ **Error handling** - graceful handling of invalid/expired credentials
- 🐚 **Shell integration** - works with CDK, virtual environments, and shell tools
- 💡 **Smart suggestions** - shows how to make profile changes permanent

## 📦 Installation & Setup

### Method 1: Simple Install (Recommended)

```bash
# 1. Install the tool
pip3 install git+https://github.com/username/aws-profile-switcher.git

# 2. One-time setup (automatically configures shell integration)
awsprofile setup-shell

# 3. Reload your shell config
source ~/.zshrc    # for zsh
# OR
source ~/.bashrc   # for bash

# 4. That's it! Now use the simple commands:
awsp work          # Switch to 'work' profile
awsl               # List all profiles  
awsi               # Interactive mode
awsc               # Show current profile
awsclear           # Clear profile
```

### Method 2: Manual Setup (If you prefer)

```bash
# Install
pip3 install git+https://github.com/username/aws-profile-switcher.git

# Manually add shell integration
echo 'awsp() { eval "$(awsprofile -p "$1" --shell)"; }' >> ~/.zshrc
source ~/.zshrc
```

## 🔍 Find Your Profile Names First!

Before using the tool, see what AWS profiles you actually have:

```bash
# List your profiles (shows account info too):
awsprofile list

# Example output:
📋 Available profiles (3 total):
----------------------------------------
✅  1. default
       Account: 123456789012
   2. my-company-prod
       Account: 987654321098  
   3. john-personal
       Account: 555666777888
```

**Now use YOUR actual profile names:**
```bash
awsprofile -p my-company-prod    # ← Use YOUR profile name here
awsprofile -p john-personal      # ← Use YOUR profile name here
awsprofile -p default            # ← This one everyone has
```

> **📝 Note**: Profile names like "work", "staging", "production" in this README are just **examples**. Your actual profile names might be "my-company-dev", "client-xyz", "personal-aws", etc. Always use YOUR real profile names with the `-p` flag!

## 🐚 Shell Integration (The Easy Way!)

### One-Time Setup
```bash
# This does everything automatically:
awsprofile setup-shell
source ~/.zshrc  # or ~/.bashrc
```

**That's it!** The tool automatically:
- Detects your shell (bash/zsh)
- Adds all the integration functions
- Sets up tab completion
- Creates backups of your config files

### Now You Have These Commands:

> **⚠️ Remember**: Replace the example profile names below with YOUR actual profile names!

```bash
# First, see what profiles YOU have:
awsprofile list                 # List YOUR profiles

# Then switch using YOUR actual profile names:
awsp my-company-prod            # ← Example: replace with YOUR profile name
awsp john-dev                   # ← Example: replace with YOUR profile name  
awsp client-staging             # ← Example: replace with YOUR profile name

# Other useful commands:
awsl                           # List all profiles (same as: awsprofile list)
awsi                           # Interactive mode (same as: awsprofile)
awsc                           # Show current profile (same as: awsprofile current)
awsclear                       # Clear AWS_PROFILE environment variable
```

### Perfect for CDK Development:
```bash
cd my-cdk-project
python -m venv venv
source venv/bin/activate

# First see your profiles:
awsprofile list
# Output might show: default, my-company-prod, my-personal

# Switch to YOUR actual profile:
awsp my-company-prod           # ← Use YOUR real profile name here
cdk deploy                     # Uses 'my-company-prod' profile ✅
aws s3 ls                      # Uses 'my-company-prod' profile ✅
```

### ❌ Don't Do This:
```bash
awsp work                      # ❌ Only works if you actually have a profile named "work"
awsp production                # ❌ Only works if you actually have a profile named "production"
```

### ✅ Do This Instead:
```bash
awsprofile list                # First, see YOUR actual profile names
awsp <YOUR-REAL-PROFILE-NAME>  # Use whatever the list showed you
```

## 🚀 Basic Usage

### Step 1: See What Profiles You Have
```bash
awsprofile list         # Detailed list with account info
```

### Step 2: Use YOUR Actual Profile Names

**New v1.4.0 explicit syntax (recommended):**
```bash
# Use the explicit -p flag for profile switching:
awsprofile -p company-prod       # Switch to 'company-prod' profile  
awsprofile -p personal-aws       # Switch to 'personal-aws' profile
awsprofile -p client-dev         # Switch to 'client-dev' profile

# These are just examples! Use whatever 'awsprofile list' showed you.
```

**Real example:**
```bash
$ awsprofile list
📋 Available profiles (3 total):
----------------------------------------
   1. default
       Account: 123456789012
   2. my-work-account  
       Account: 987654321098
   3. johns-personal
       Account: 555666777888

$ awsprofile -p my-work-account  # ← Use the actual name from the list above
✅ Switched to AWS profile: my-work-account
   Account: 987654321098
```

### Available Commands:
```bash
# Core commands (no conflicts with profile names!):
awsprofile list                    # List all profiles
awsprofile current                 # Show current profile
awsprofile setup-shell             # One-time shell setup

# Profile switching (explicit with -p flag):
awsprofile -p <YOUR-PROFILE-NAME>  # Switch profiles (use YOUR real name!)
awsprofile --profile <name>        # Long form flag
awsprofile -p <name> --shell       # Output shell export command

# Profile management:
awsprofile create new-client       # Create a new profile
awsprofile delete old-profile      # Delete a profile

# Help and info:
awsprofile --help                  # Show comprehensive help
awsprofile --version               # Show version
```

### After Shell Integration Setup:
```bash
# Simple shell commands (after awsprofile setup-shell):
awsp <YOUR-PROFILE-NAME>           # Switch profiles (persists in shell)
awsl                               # List all profiles
awsi                               # Interactive mode
awsc                               # Show current profile
awsclear                           # Clear profile
```

> **💡 Tip**: Use tab completion! After setup, type `awsp ` and press Tab to see your profile names.

## 🛠️ Key Improvement in v1.4.0: No More Namespace Conflicts!

**Before v1.4.0 (problematic):**
```bash
awsprofile list          # ❌ Might be treated as profile named "list"
awsprofile current       # ❌ Might be treated as profile named "current"
```

**v1.4.0+ (works perfectly):**
```bash
awsprofile list          # ✅ Always the list command
awsprofile current       # ✅ Always the current command  
awsprofile -p list       # ✅ Switch to profile named "list" (if you have one)
awsprofile -p current    # ✅ Switch to profile named "current" (if you have one)
```

**You can now have profiles with ANY names** - including 'list', 'current', 'create', 'delete', 'setup-shell' - without conflicts!

## 🛠️ CDK and Virtual Environment Usage

The shell integration makes this tool perfect for CDK development:

```bash
# In any project directory or virtual environment
cd my-cdk-project
python -m venv venv
source venv/bin/activate

# First, see what profiles you have:
awsprofile list
# Example output: default, company-prod, company-staging, personal

# Switch AWS profile for this shell session (use YOUR real profile name):
awsp company-prod       # ← Replace with YOUR actual profile name

# Now CDK uses your chosen profile:
cdk deploy
cdk synth
aws s3 ls               # All AWS commands use the profile you set
```

**Real-world example:**
```bash
$ cd my-react-app-cdk
$ python -m venv venv  
$ source venv/bin/activate
$ awsprofile list
📋 Available profiles (4 total):
----------------------------------------
   1. default
       Account: 123456789012
   2. acme-corp-production
       Account: 987654321098
   3. acme-corp-staging
       Account: 555666777888
   4. john-personal
       Account: 111222333444

$ awsp acme-corp-staging    # Using the real profile name from the list
✅ Switched to AWS profile: acme-corp-staging
   Account: 555666777888

$ cdk deploy MyReactAppStack
# Deploys to the acme-corp-staging account ✅
```

The profile switch persists for:
- The current shell session
- Any virtual environments activated in that shell
- All AWS CLI commands and tools (CDK, SAM, etc.)
- Any subprocesses launched from that shell

### Multiple Projects Example:
```bash
# Terminal 1 - Production deployment
cd project-a
awsp company-prod       # ← Your real production profile name
cdk deploy

# Terminal 2 - Development work  
cd project-b
awsp company-dev        # ← Your real development profile name
cdk deploy

# Each terminal remembers its own profile!
```

> **⚠️ Important**: Always replace "company-prod", "company-dev", etc. with YOUR actual AWS profile names. Use `awsprofile list` to see what profiles you really have.

## 🔧 Interactive Mode

```
🔧 AWS Profile Manager v1.4.0
============================================================
📍 Current profile: default
   Account: 123456789012
   User: john

📋 Available profiles (4 total):
----------------------------------------
✅  1. default
       Account: 123456789012
   2. acme-corp-prod
       Account: 987654321098
   3. acme-corp-staging  
       Account: 555666777888
   4. john-personal
       Account: 111222333444

🔄 Options:
   1-4: Switch to profile
   c: Create a new profile
   d: Delete a profile
   r: Refresh profile list
   q: Quit

Select option: c

🔧 Profile creation mode
Enter new profile name: client-xyz-dev

🔧 Creating AWS profile: 'client-xyz-dev'
==================================================
📝 Enter AWS credentials:
   AWS Access Key ID: AKIA1234567890123456
   AWS Secret Access Key: [hidden]
   Default region (us-east-1): us-west-2
   Output format (json): json

🔍 Testing credentials for profile 'client-xyz-dev'...
✅ Credentials validated successfully!
   Account: 777888999000
   User: dev-user

📋 Backed up credentials to /home/user/.aws/credentials.backup
📋 Backed up config to /home/user/.aws/config.backup
✅ Added 'client-xyz-dev' to credentials file
✅ Added 'client-xyz-dev' to config file

🎉 Successfully created profile 'client-xyz-dev'!
💡 Test it with: awsprofile -p client-xyz-dev
```

> **📝 Note**: The profile names shown above (like "acme-corp-prod", "john-personal") are just examples. YOUR profiles will have different names based on how you set them up.

### Profile Creation

```bash
# Create a new profile interactively (you choose the name)
awsprofile create client-xyz-staging    # ← You pick the name

# Output:
🔧 Creating AWS profile: 'client-xyz-staging'
==================================================
📝 Enter AWS credentials:
   AWS Access Key ID: AKIA1234567890123456
   AWS Secret Access Key: [hidden]
   Default region (us-east-1): us-west-2
   Output format (json): json

🔍 Testing credentials for profile 'client-xyz-staging'...
✅ Credentials validated successfully!
   Account: 555999888777
   User: staging-user

✅ Added 'client-xyz-staging' to credentials file
✅ Added 'client-xyz-staging' to config file
🎉 Successfully created profile 'client-xyz-staging'!
```

> **💡 Tip**: Choose descriptive profile names like "company-prod", "client-staging", "personal-dev" instead of generic names like "work" or "test".

### Profile Deletion

```bash
# Delete a profile (use the actual name from your list)
awsprofile delete old-unused-profile    # ← Replace with real profile name

# Example with real profile names:
$ awsprofile list
📋 Available profiles (4 total):
----------------------------------------
   1. default
       Account: 123456789012
   2. company-prod
       Account: 987654321098
   3. old-client-profile  
       Account: 555666777888
   4. personal
       Account: 111222333444

$ awsprofile delete old-client-profile
⚠️  Are you sure you want to delete profile 'old-client-profile'?
   This will remove it from both credentials and config files.
   Type 'yes' to confirm: yes

📋 Backed up credentials to /home/user/.aws/credentials.backup
📋 Backed up config to /home/user/.aws/config.backup
✅ Removed 'old-client-profile' from credentials file
✅ Removed 'old-client-profile' from config file
✅ Successfully deleted profile 'old-client-profile'
```

## 🔍 Troubleshooting

### Common Issues

**"awsprofile: error: unrecognized arguments"**
```bash
# Problem: Using old syntax after v1.4.0 upgrade
awsprofile my-profile        # ❌ Old way (may conflict)

# Solution: Use explicit -p flag  
awsprofile -p my-profile     # ✅ New explicit way
```

**"Profile 'list' not found" (pre-v1.4.0 issue, now fixed!)**
```bash
# This was the old namespace conflict problem, solved in v1.4.0
# Now commands and profiles never conflict:
awsprofile list              # ✅ Always the list command
awsprofile -p list           # ✅ Profile named "list" (if you have one)
```

**"No AWS credentials file found"**
```bash
# Solution: Configure your first AWS profile
aws configure
```

**"AWS CLI not found"**
```bash
# Solution: Install AWS CLI v2
# macOS (Homebrew)
brew install awscli

# Or download from: https://aws.amazon.com/cli/
```

**"Profile validation failed"**
- Check your AWS credentials are correct
- Ensure your AWS account is active
- Verify network connectivity to AWS

**"Profile switch doesn't work with CDK"**
- Make sure you're using the shell integration (`awsp` command)
- Don't use `awsprofile -p` directly for persistent switching
- Use `awsp <YOUR-PROFILE-NAME>` instead for shell persistence
- Verify with `aws sts get-caller-identity` after switching

**"I don't know what profile names to use"**
```bash
# See YOUR actual profile names:
awsprofile list

# Use whatever names are shown in the output with -p flag
awsprofile -p <name-from-list>
```

**"Tab completion doesn't work"**
```bash
# Make sure you ran the setup:
awsprofile setup-shell
source ~/.zshrc    # or ~/.bashrc
```

**"Shell integration commands not found (awsp, awsl, etc.)"**
```bash
# Run setup and source your shell config:
awsprofile setup-shell
source ~/.zshrc    # or ~/.bashrc

# Verify with:
awsprofile --help  # Should show shell integration commands in help
```

### Debug Mode

For more detailed error information:
```bash
# Run with Python's verbose mode
python3 -v awsprofile list
```

## 📝 Changelog

### v1.4.0 (2025-06-19) 
- 🎯 **Namespace conflicts eliminated**: Commands never conflict with profile names
- 🔧 **Explicit profile switching**: Use `-p`/`--profile` flag for clear intent
- 🛡️ **Robust argument parsing**: Professional argparse-based CLI with proper subcommands
- 📚 **Comprehensive help**: Shell integration commands documented in `--help` output
- ⚡ **Any profile name works**: Users can have profiles named 'list', 'current', 'create', etc.
- 🎯 **Breaking change**: Profile switching now requires `-p` flag for disambiguation
- 🧪 **Enhanced testing**: All edge cases and argument combinations tested
- 💡 **Better UX**: Clear error messages and improved discoverability

### v1.3.0 (2025-06-19) 
- 🎯 **One-command setup**: `awsprofile setup-shell` automatically configures everything
- 🧠 **Smart shell detection**: Automatically detects bash/zsh and adds appropriate config
- 📝 **Auto tab completion**: Profile name completion included in automated setup
- 💡 **Helpful suggestions**: Tool suggests shell integration when beneficial
- 🔄 **Current profile command**: `awsprofile current` shows active profile and account info
- 🔧 **Enhanced help**: Updated documentation with simplified workflows
- 🧪 **Improved testing**: Additional tests for shell integration setup

### v1.2.0 (2025-06-19)
- ✨ Added interactive profile creation with credential validation
- ✨ Added command-line profile creation: `awsprofile create <profile-name>`
- ✨ Added automatic credential testing before saving profiles
- ✨ Added 'c' option in interactive mode for creating profiles
- 🔧 Enhanced backup system for both creation and deletion
- 🔧 Improved error handling for invalid credentials
- 📚 Updated documentation with profile creation examples
- 🧪 Added comprehensive tests for profile creation functionality

### v1.1.0 (2025-06-19)
- ✨ Added profile deletion functionality with automatic backups
- ✨ Added shell integration for CDK and virtual environment support
- ✨ Added `--shell` mode for proper environment variable export
- ✨ Added tab completion for bash and zsh
- ✨ Added `awsp`, `awsl`, `awsi`, `awsc`, `awsclear` shell aliases
- 🔧 Improved error handling and user feedback
- 📚 Enhanced documentation with CDK usage examples

### v1.0.0 (2025-06-18)
- Initial release
- Interactive profile switching
- Profile validation and account information display
- Command-line interface with multiple usage modes
- Comprehensive error handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for developers who work with multiple AWS accounts
- Inspired by the need for better AWS profile management in CDK projects
- Thanks to the AWS CLI team for providing the foundation
```
📞 Support

🐛 Bug reports: Open an issue
💡 Feature requests: Open an issue
📧 Questions: sovang.widomski.cert@gmail.com


Made with ❤️ by Sovang Widomski