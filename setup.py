from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent.resolve()

# The text of the README file
README = (HERE / "README.md").read_text(encoding="utf-8")

# This call to setup() does all the work
setup(
    name="pyneevo",
    version="1.0.0",
    author="davidflypei",
    description="Python library for interacting with the Neevo API",
    long_description=README,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=("tests", "tests.*", "*.tests.*", ".tests", "dist")),
    install_requires=["requests"],
    keywords="neevo, propane, tank, api",
    python_requires=">=3.6",
    url="https://github.com/davidflypei/pyneevo",
    project_urls={
        "Bug Tracker": "https://github.com/davidflypei/pyneevo/issues",
    },
)