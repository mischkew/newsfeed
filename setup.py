# TODO: install invoke

from pathlib import Path
from setuptools import setup, find_packages


setup(
    name="feed",
    version=Path("./VERSION").read_text("utf8").strip(),
    # description=short_description,
    # long_description=long_description,
    # url="https://github.com/thinksono/predictor",
    author="Sven Mischkewitz",
    author_email="sven.mkw@gmail.com",
    license="Private License",
    packages=find_packages(),
    install_requires=["beautifulsoup4>=4.9.1,<5"],
    extras_require={"dev": ["ptvsd>=4.3.2,<5"]},
    include_package_data=True,
    # scripts=scripts,
    entry_points={"console_scripts": ["feed = feed.cli:main"]},
)
