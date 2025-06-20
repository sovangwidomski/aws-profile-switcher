"""
AWS Profile Switcher - Simple AWS profile management for local development

A lightweight tool for switching between AWS profiles with ease.
Uses AWS CLI commands via subprocess for maximum compatibility.

Key Features:
- Interactive profile selection with account info display
- Direct profile switching via command line
- Profile creation, deletion, and management
- Clear current profile functionality
- Zero Python dependencies (uses AWS CLI)

Usage:
    from awsprofile import main, get_profiles, switch_profile
    
    # Programmatic usage
    profiles = get_profiles()
    switch_profile('my-profile')
    
    # CLI usage
    main()  # Interactive mode
"""

__version__ = "1.5.1"
__author__ = "sovangwidomski"  # Update this to your actual name
__email__ = "your.email@example.com"  # Update this to your actual email
__description__ = "Simple AWS profile switcher for easy local development"
__url__ = "https://github.com/sovangwidomski/aws-profile-switcher"
__license__ = "MIT"

# Import main CLI function
try:
    from .cli import (
        main,
        get_profiles,
        get_current_profile,
        switch_profile,
        list_profiles,
        show_current_profile,
        create_profile,
        delete_profile,
        clear_profile,
        interactive_mode
    )
except ImportError as e:
    # Graceful handling if cli module can't be imported
    import sys
    print(f"Warning: Could not import awsprofile.cli: {e}", file=sys.stderr)
    print("This might indicate a broken installation.", file=sys.stderr)
    
    # Define placeholder functions to prevent import errors
    def main():
        """Placeholder main function - installation may be broken."""
        raise ImportError(f"awsprofile.cli could not be imported: {e}")
    
    # Set other functions to None so they're available in __all__ but will raise errors
    get_profiles = get_current_profile = switch_profile = None
    list_profiles = show_current_profile = create_profile = None
    delete_profile = clear_profile = interactive_mode = None

# Public API - these functions are available when someone does `from awsprofile import *`
__all__ = [
    # CLI entry point
    'main',
    
    # Core functionality
    'get_profiles',
    'get_current_profile', 
    'switch_profile',
    
    # Display functions
    'list_profiles',
    'show_current_profile',
    
    # Profile management
    'create_profile',
    'delete_profile',
    'clear_profile',
    
    # Interactive mode
    'interactive_mode',
    
    # Metadata
    '__version__',
    '__author__',
    '__description__',
]

# Package metadata for introspection
__package_info__ = {
    'name': 'aws-profile-switcher',
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'url': __url__,
    'license': __license__,
    'python_requires': '>=3.6',
    'system_requires': ['AWS CLI'],
}

def get_package_info():
    """Return package metadata as a dictionary."""
    return __package_info__.copy()

def print_version():
    """Print version information."""
    print(f"AWS Profile Switcher v{__version__}")
    print(f"Author: {__author__}")
    print(f"URL: {__url__}")

# Add version info to __all__ for convenience
__all__.extend(['get_package_info', 'print_version'])