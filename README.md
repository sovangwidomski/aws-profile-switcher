# 🔧 AWS Profile Switcher v1.2.0

A simple, interactive command-line tool to create, view, switch, and delete AWS profiles with ease. Perfect for developers working with multiple AWS accounts, especially when using tools like AWS CDK in virtual environments.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS CLI](https://img.shields.io/badge/AWS-CLI-orange.svg)](https://aws.amazon.com/cli/)

## ✨ New Features in v1.2.0

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
🔧 AWS Profile Manager v1.2.0
============================================================
📍 Current profile: default
   Account: 123456789012
   User: sovang

📋 Available profiles (3 total):
----------------------------------------
✅  1. default
       Account: 123456789012
   2. work
       Account: 987654321098
   3. personal
       Account: 555666777888

🔄 Options:
   1-3: Switch to profile
   c: Create a new profile
   d: Delete a profile
   r: Refresh profile list
   q: Quit

Select option: c

🔧 Profile creation mode
Enter new profile name: staging

🔧 Creating AWS profile: 'staging'
==================================================
📝 Enter AWS credentials:
   AWS Access Key ID: AKIA1234567890123456
   AWS Secret Access Key: [hidden]
   Default region (us-east-1): us-west-2
   Output format (json): json

🔍 Testing credentials for profile 'staging'...
✅ Credentials validated successfully!
   Account: 555999888777
   User: staging-user

📋 Backed up credentials to /home/user/.aws/credentials.backup
📋 Backed up config to /home/user/.aws/config.backup
✅ Added 'staging' to credentials file
✅ Added 'staging' to config file

🎉 Successfully created profile 'staging'!
💡 Test it with: awsprofile staging
```

### Profile Creation

```bash
# Create a new profile interactively
awsprofile create staging

# Output:
🔧 Creating AWS profile: 'staging'
==================================================
📝 Enter AWS credentials:
   AWS Access Key ID: AKIA1234567890123456
   AWS Secret Access Key: [hidden]
   Default region (us-east-1): us-west-2
   Output format (json): json

🔍 Testing credentials for profile 'staging'...
✅ Credentials validated successfully!
   Account: 555999888777
   User: staging-user

✅ Added 'staging' to credentials file
✅ Added 'staging' to config file
🎉 Successfully created profile 'staging'!
```

### Profile Deletion

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

# Switch AWS profile for this shell session
awsp work

# Now CDK uses the 'work' profile
cdk deploy
cdk synth
```

The profile switch persists for:
- The current shell session
- Any virtual environments activated in that shell
- All AWS CLI commands and tools (CDK, SAM, etc.)
- Any subprocesses launched from that shell

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
- Don't use `awsprofile` directly - use `awsp <profile>` instead
- Verify with `aws sts get-caller-identity` after switching

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