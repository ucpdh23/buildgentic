from setuptools import setup, find_packages

# Function to read requirements from requirements.txt
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, "r") as file:
        return [line.strip() for line in file if line and not line.startswith("#")]

# Read requirements from requirements.txt
requirements = parse_requirements("requirements.txt")


setup(
    name="buildgentic",  # Replace with your project name
    version="0.1.0",           # Start with an initial version
    description="Agentic solution to generate itself",
    long_description=open("README.md").read(),  # Optional: Load a long description from README
    long_description_content_type="text/markdown",
    author="xan xan",
    url="https://github.com/ucpdh23/buildgentic",  # Replace with your project's URL
    packages=find_packages(),  # Automatically find and include all packages
    include_package_data=True, # Include any other data files specified in MANIFEST.in
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",  # Development dependencies, like testing frameworks
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choose your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "buildgentic = principal:startup",  # Optional: command-line interface
        ],
    },
)
