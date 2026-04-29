"""
SAAB-SUITE setup configuration.
"""
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="saab-suite",
    version="1.0.0",
    description="Full SAAB/GM diagnostic suite with Python engine, CAN tools, GDS2/Tech2Win integrations, SPS workflows, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="K1LLLAGT",
    url="https://github.com/K1LLLAGT/SAAB-SUITE",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "saab-suite=ui.app:main",
            "saab-tui=tui.app:main",
            "saab-scan=scripts.diagnostic_scan:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
)
