"""
Publish a new version:
- Change version number in pipecutter/__init__.py
- Add entry to CHANGELOG.md
- Make sure that everything is committed and pushed
$ pytest
$ git tag vX.Y.Z -m "Release X.Y.Z"
$ git push --tags
- Wait for tests on TravisCI to pass and make sure that code coverage is 100%
Use either pip or conda to upgrade twine and wheel
$ python3 -m pip install --upgrade twine wheel
$ python3 setup.py sdist bdist_wheel
$ python3 -m twine upload dist/*
"""
import setuptools
from pathlib import Path

import pipecutter

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="pipecutter",
    version=pipecutter.__version__,
    author="Stefan Binder",
    url="https://github.com/binste/pipecutter",
    description=(
        "Some tools for Luigi to cut down the length of your pipelines and work"
        " in interactive environments such as Jupyter notebooks."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    packages=["pipecutter"],
    keywords=[
        "luigi",
        "spotify",
        "pipeline",
        "plumber",
        "workflow",
        "batch",
        "dependency resolution",
        "jupyter",
        "interactive",
        "targets",
    ],
    python_requires=">=3.6,<3.8",
    license="MIT",
    classifiers=(
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 5 - Production/Stable",
    ),
)
