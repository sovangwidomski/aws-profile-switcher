# 🔧 AWS Profile Switcher v1.3.0

A simple, interactive command-line tool to create, view, switch, and delete AWS profiles with ease. Perfect for developers working with multiple AWS accounts, especially when using tools like AWS CDK in virtual environments.

## ⚡ Quick Start

```bash
# Install
pip3 install git+https://github.com/username/aws-profile-switcher.git

# One-time setup for shell integration
awsprofile setup-shell
source ~/.zshrc  # or ~/.bashrc

# Find your actual profile names:
awsl            # List YOUR profiles

# Use YOUR actual profile names (not "work"!):
awsp production    # ← Replace "production" with YOUR profile name
awsp staging       # ← Replace "staging" with YOUR profile name  
awsp personal      # ← Replace "personal" with YOUR profile name
```

> **⚠️ Important**: "production", "staging", "personal" are just **examples**! 
> Use `awsl` to see YOUR actual profile names, then use those names with `awsp`.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS CLI](https://img.shields.io/badge/AWS-CLI-orange.svg)](https://aws.amazon.com/cli/)

## ✨ New Features in v1.3.0

- 🎯 **One-command setup** - `awsprofile setup-shell` does everything automatically
- 🧠 **Smart detection** - Automatically detects shell type and sets up integration
- 📝 **Auto tab completion** - Profile name completion included in setup
- 💡 **Helpful suggestions** - Tool suggests using shell integration when available
- 🔄 **Current profile command** - `awsprofile current` shows active profile

## ✨ Features from v1.2.0

- 🔧 **Profile creation** - Create new AWS profiles interactively with credential validation
- 🛡️ **Credential testing** - Validates AWS credentials before saving profiles
- 📁 **Smart backups** - Automatic backup before modifying credentials/config files
- 💫 **Complete CRUD** - Create, Read, Update, Delete - full profile lifecycle management

## ✨ Features from v1.1.0

- 🗑️ **Profile deletion** - Remove profiles safely with backup
- 🐚 **Shell integration** - Works with CDK, virtual environments, and any shell tools
- 🔄 **Better environment handling** - Properly exports AWS_PROFILE to current shell
- 📝 **Tab completion** - Auto-complete profile names in bash/zsh

## ✨ All Features

- ⚡ **One-command setup** - `setup-shell` automatically configures everything
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

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- AWS CLI v2 installed and configured
- At least one AWS profile configured (`aws configure`)

### Installation

#### Step 1: Install the Tool

```bash
# Clone the repository
git clone https://github.com/sovangwidomski/aws-profile-switcher.git
cd aws-profile-switcher

# Install dependencies
pip3 install -r requirements.txt

# Install as package (recommended)
pip3 install -e .
```

#### Step 2: Set Up Shell Integration (Recommended)

For the best experience with CDK and virtual environments:

```bash
# Download the shell integration
curl -O https://raw.githubusercontent.com/sovangwidomski/aws-profile-switcher/main/shell_integration.sh

# Add to your shell config
echo "source $(pwd)/shell_integration.sh" >> ~/.zshrc   # For zsh
echo "source $(pwd)/shell_integration.sh" >> ~/.bashrc  # For bash

# Reload your shell
source ~/.zshrc  # or source ~/.bashrc
```

Or manually add this function to your `~/.zshrc` or `~/.bashrc`:

```bash
awsp() {
    if [ $# -eq 0 ]; then
        awsprofile
    else
        local output
        output=$(awsprofile "$1" --shell 2>&1)
        if echo "$output" | grep -q "export AWS_PROFILE"; then
            eval "$output"
            echo "✅ Switched to AWS profile: $1"
            aws sts get-caller-identity --output text --query 'Account' 2>/dev/null | sed 's/^/   Account: /'
        else
            echo "$output"
        fi
    fi
}
```

## 📖 Usage

### Shell Integration (Recommended for CDK/Virtual Environments)

After setting up shell integration:

```bash
# Switch profiles (works in any directory, virtual environment, etc.)
awsp work          # Switch to 'work' profile
awsp personal      # Switch to 'personal' profile
awsp default       # Switch to 'default' profile

# List profiles
awsl

# Interactive mode
awsi

# Show current profile
awsc

# Clear profile (use default)
awsclear
```

### Interactive Mode

```bash
awsprofile
```

This opens an interactive menu where you can:
- See all profiles with account information
- Switch profiles by entering a number
- Create new profiles with guided setup
- Delete profiles safely
- Refresh the profile list
- Quit when done

### Command Line Options

```bash
# List all profiles
awsprofile list

# Switch to specific profile
awsprofile work

# Switch with shell export (for scripts)
eval "$(awsprofile work --shell)"

# Create a new profile
awsprofile create staging

# Delete a profile
awsprofile delete old-profile

# Show help
awsprofile --help

# Show version
awsprofile --version
```

## 📋 Example Output

### Interactive Mode with New Features

```
🔧 AWS Profile Manager v1.3.0
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
💡 Test it with: awsprofile client-xyz-dev
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
$ awsl
default
company-prod
old-client-profile  
personal

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

```
Select option: d

🗑️  Profile deletion mode
Available profiles:
   1. default
   2. work
   3. personal

Enter profile number to delete (or 'c' to cancel): 3

⚠️  Are you sure you want to delete profile 'personal'?
   This will remove it from both credentials and config files.
   Type 'yes' to confirm: yes

📋 Backed up credentials to /home/user/.aws/credentials.backup
📋 Backed up config to /home/user/.aws/config.backup
✅ Removed 'personal' from credentials file
✅ Removed 'personal' from config file
✅ Successfully deleted profile 'personal'
```

## 🛠️ CDK and Virtual Environment Usage

The shell integration makes this tool perfect for CDK development:

```bash
# In any project directory or virtual environment
cd my-cdk-project
python -m venv venv
source venv/bin/activate

# First, see what profiles you have:
awsl
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
$ awsl
default
acme-corp-production
acme-corp-staging
john-personal

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

> **⚠️ Important**: Always replace "company-prod", "company-dev", etc. with YOUR actual AWS profile names. Use `awsl` to see what profiles you really have.

## ⚙️ Configuration

### AWS Profiles Setup

If you haven't set up AWS profiles yet:

```bash
# Configure your first profile (becomes 'default')
aws configure

# Configure additional profiles
aws configure --profile work
aws configure --profile personal
```

### Profile Files Location

- **Credentials:** `~/.aws/credentials`
- **Config:** `~/.aws/config`
- **Backups:** `~/.aws/credentials.backup`, `~/.aws/config.backup` (created before deletion)

## 🔍 Troubleshooting

### Common Issues

**"Profile 'work' not found"**
```bash
# Problem: You're using an example name that doesn't exist
awsp work                    # ❌ 

# Solution: Use YOUR actual profile names
awsl                         # See what profiles you really have
awsp my-actual-profile-name  # ✅ Use the real name
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
- Don't use `awsprofile` directly - use `awsp <YOUR-PROFILE-NAME>` instead
- Verify with `aws sts get-caller-identity` after switching

**"I don't know what profile names to use"**
```bash
# See YOUR actual profile names:
awsprofile list
# OR
awsl

# Use whatever names are shown in the output
```

**"Tab completion doesn't work"**
```bash
# Make sure you ran the setup:
awsprofile setup-shell
source ~/.zshrc    # or ~/.bashrc
```

### Debug Mode

For more detailed error information:
```bash
# Run with Python's verbose mode
python3 -v awsprofile list
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/aws-profile-switcher.git
cd aws-profile-switcher

# Install development dependencies
pip3 install -r requirements.txt

# Install in development mode
pip3 install -e .

# Test the tool
awsprofile --help
```

## 📝 Changelog

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

## 🚀 Future Enhancements

Ideas for future versions:
- [ ] **MFA support** - handle multi-factor authentication seamlessly
- [ ] **Profile templates** - quick setup for common configurations with predefined settings
- [ ] **Config file validation** - check for common configuration issues
- [ ] **Cross-region switching** - easily switch default regions per profile
- [ ] **Integration with AWS SSO** - support for AWS Single Sign-On
- [ ] **Profile aliases** - create friendly names for profiles
- [ ] **Automatic profile backup/restore** - version control for profiles
- [ ] **Bulk operations** - create/delete multiple profiles at once
- [ ] **Profile import/export** - share profile configurations (without credentials)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for developers frustrated with AWS profile management
- Inspired by the need for simple, reliable tooling that works with CDK
- Thanks to the AWS CLI team for the excellent underlying tools
- Special thanks to the CDK community for feedback on virtual environment issues

## 📞 Support

- 🐛 **Bug reports:** [Open an issue](https://github.com/sovangwidomski/aws-profile-switcher/issues)
- 💡 **Feature requests:** [Open an issue](https://github.com/sovangwidomski/aws-profile-switcher/issues)
- 📧 **Questions:** sovang.widomski.cert@gmail.com

---

**Made with ❤️ by [Sovang Widomski](https://github.com/sovangwidomski)**

*If this tool saved you time (especially with CDK!), please ⭐ star the repository!*