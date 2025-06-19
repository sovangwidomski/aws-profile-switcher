# 🔧 AWS Profile Switcher

A simple, interactive command-line tool to view and switch between AWS profiles with ease. Perfect for developers working with multiple AWS accounts.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS CLI](https://img.shields.io/badge/AWS-CLI-orange.svg)](https://aws.amazon.com/cli/)

## ✨ Features

- 📋 **List all available AWS profiles** with account information
- 🔄 **Interactive profile switching** with numbered selection
- ✅ **Profile validation** - tests credentials before switching
- 🎯 **Current profile highlighting** - see which profile is active
- ⚡ **Fast credential verification** - quick account ID lookup
- 🛡️ **Error handling** - graceful handling of invalid/expired credentials
- 💡 **Smart suggestions** - shows how to make profile changes permanent

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 
- AWS CLI v2 installed and configured
- At least one AWS profile configured (`aws configure`)

### Installation

#### Option 1: Direct Download (Recommended)

```bash
# Clone the repository
git clone https://github.com/sovangwidomski/aws-profile-switcher.git
cd aws-profile-switcher

# Install dependencies
pip3 install -r requirements.txt

# Run the tool
python3 src/awsprofile/cli.py
```

#### Option 2: Install as Package

```bash
# Clone and install
git clone https://github.com/sovangwidomski/aws-profile-switcher.git
cd aws-profile-switcher
pip3 install -e .

# Use anywhere
awsprofile
```

## 📖 Usage

### Interactive Mode (Recommended)

```bash
python3 src/awsprofile/cli.py
```

This opens an interactive menu where you can:
- See all profiles with account information
- Switch profiles by entering a number
- Refresh the profile list
- Quit when done

### Command Line Options

```bash
# List all profiles
python3 src/awsprofile/cli.py list

# Switch to specific profile
python3 src/awsprofile/cli.py work

# Show help
python3 src/awsprofile/cli.py --help

# Show version
python3 src/awsprofile/cli.py --version
```

## 📋 Example Output

```
🔧 AWS Profile Manager v1.0.0
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
   r: Refresh profile list
   q: Quit

Select option: 2

🔍 Testing profile 'work'...
✅ Successfully switched to profile 'work'
   Account: 987654321098
   User: admin

💡 To make this permanent for your terminal session:
   export AWS_PROFILE=work
```

## 🛠️ How It Works

The tool works by:

1. **Reading AWS credentials** from `~/.aws/credentials`
2. **Testing each profile** using `aws sts get-caller-identity`
3. **Displaying account information** for easy identification
4. **Setting the `AWS_PROFILE` environment variable** for the current session
5. **Providing instructions** for making changes permanent

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

### Debug Mode

For more detailed error information:
```bash
# Run with Python's verbose mode
python3 -v src/awsprofile/cli.py list
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

# Run tests (when available)
python3 -m pytest tests/

# Check code style
python3 -m flake8 src/
```

## 📝 Changelog

### v1.0.0 (2025-06-18)
- Initial release
- Interactive profile switching
- Profile validation and account information display
- Command-line interface with multiple usage modes
- Comprehensive error handling

## 🚀 Future Enhancements

Ideas for future versions:
- [ ] **Profile aliases** - create friendly names for profiles
- [ ] **MFA support** - handle multi-factor authentication
- [ ] **Profile templates** - quick setup for common configurations
- [ ] **Bash/Zsh completion** - tab completion for profile names
- [ ] **Config file validation** - check for common configuration issues
- [ ] **Cross-region switching** - easily switch default regions
- [ ] **Integration with AWS SSO** - support for AWS Single Sign-On

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for developers frustrated with AWS profile management
- Inspired by the need for simple, reliable tooling
- Thanks to the AWS CLI team for the excellent underlying tools

## 📞 Support

- 🐛 **Bug reports:** [Open an issue](https://github.com/sovangwidomski/aws-profile-switcher/issues)
- 💡 **Feature requests:** [Open an issue](https://github.com/sovangwidomski/aws-profile-switcher/issues)
- 📧 **Questions:** sovang.widomski.cert@gmail.com

---

**Made with ❤️ by [Sovang Widomski](https://github.com/sovangwidomski)**

*If this tool saved you time, please ⭐ star the repository!*