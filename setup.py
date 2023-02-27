import os
import re
import setuptools
from setuptools.command.develop import develop
from setuptools.command.install import install


here = os.path.abspath(os.path.dirname(__file__))


class PostDevelopCommand(develop):
    """
    Post-installation for development mode.
    From https://stackoverflow.com/a/36902139/15835974
    """

    def run(self):
        develop.run(self)
        from font_collector import FontLoader

        FontLoader.discard_generated_font_cache()
        FontLoader.discard_system_font_cache()


class PostInstallCommand(install):
    """
    Post-installation for installation mode.
    From https://stackoverflow.com/a/36902139/15835974
    """

    def run(self):
        install.run(self)
        from font_collector import FontLoader

        FontLoader.discard_generated_font_cache()
        FontLoader.discard_system_font_cache()


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
    name="FontCollector",
    url="https://github.com/moi15moi/FontCollector/",
    project_urls={
        "Source": "https://github.com/moi15moi/FontCollector/",
        "Tracker": "https://github.com/moi15moi/FontCollector/issues/",
    },
    author="moi15moi",
    author_email="moi15moismokerlolilol@gmail.com",
    description="FontCollector for Advanced SubStation Alpha file.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    version=find_version("font_collector", "_version.py"),
    packages=["font_collector"],
    python_requires=">=3.8",
    install_requires=[
        "ass",
        "ass-tag-analyzer",
        "fontTools>=4.38.0",
        "freetype-py",
        "matplotlib>=3.6",
    ],
    entry_points={"console_scripts": ["fontcollector=font_collector.__main__:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Other Audience",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    license="GNU LGPL 3.0 or later",
    cmdclass={
        "develop": PostDevelopCommand,
        "install": PostInstallCommand,
    },
)
