from pathlib import Path


def get_version():
    versionfile = Path(__file__).parent.parent / "VERSION"
    if not versionfile.is_file():
        raise FileNotFoundError(
            "VERSION file not found. Did you install the package correctly?"
        )
    return "v" + versionfile.read_text("utf-8").strip()
