import os
import re
import setuptools

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = [\'\"](.+)[\'\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="fontCollector",
    url="https://github.com/moi15moi/FontCollector/",
    project_urls={
        "Source": "https://github.com/moi15moi/FontCollector/",
        "Tracker": "https://github.com/moi15moi/FontCollector/issues/",
    },
    author="moi15moi",
    author_email="moi15moismokerlolilol@gmail.com",
    description="FontCollector for Advanced SubStation Alpha file.",
    long_description_content_type="text/markdown",
    version=find_version("fontCollector.py"),
    python_requires=">=3.7",
    py_modules=['fontCollector'],
    install_requires=[
        'argparse',
        'ass',
        'fixedint',
        'fontTools',
        'matplotlib>=3.5',
        'colorama'
    ],
    entry_points={
        "console_scripts": ["fontCollector=fontCollector:main"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Other Audience",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    ],
    license="GNU LGPL 3.0 or later",
)