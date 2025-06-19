#!/usr/bin/env python3
"""Setup script for AWS Profile Switcher."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="aws-profile-switcher",
    version="1.0.0",
    author="Sovang Widomski",
    author_email="sovang.widomski.cert@gmail.com",
    description="A simple, interactive tool to view and switch between AWS profiles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sovangwidomski/aws-profile-switcher",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "boto3>=1.26.0",
    ],
    entry_points={
        "console_scripts": [
            "awsprofile=awsprofile.cli:main",
        ],
    },
    keywords="aws, cli, profile, switcher, credentials, development",
    project_urls={
        "Bug Reports": "https://github.com/sovangwidomski/aws-profile-switcher/issues",
        "Source": "https://github.com/sovangwidomski/aws-profile-switcher",
    },
)