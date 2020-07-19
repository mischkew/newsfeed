from pathlib import Path
from setuptools import setup, find_packages

short_description = (
    """Personal email news feed for blogs and other websites which don't provide RSS"""
)
long_description = Path("./README.md").read_text("utf8").strip()

setup(
    name="feed",
    version=Path("./VERSION").read_text("utf8").strip(),
    description=short_description,
    long_description=long_description,
    url="https://github.com/mischkew/newsfeed",
    author="Sven Mischkewitz",
    author_email="sven.mkw@gmail.com",
    license="MIT License",
    packages=find_packages(),
    install_requires=["beautifulsoup4>=4.9.1,<5"],
    extras_require={"dev": ["ptvsd>=4.3.2,<5"]},
    include_package_data=True,
    entry_points={"console_scripts": ["feed = feed.cli:main"]},
)
