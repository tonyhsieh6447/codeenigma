# pragma: no cover
try:
    # For Python 3.8-3.9, importlib.metadata is limited, so use backport
    try:
        from importlib_metadata import PackageNotFoundError, version
    except ImportError:
        # For Python 3.10+, importlib.metadata is available
        from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Fallback in case importlib.metadata is not available
    version = None
    PackageNotFoundError = Exception

try:
    __version__ = version("codeenigma")
except (PackageNotFoundError, TypeError):
    try:
        # For Python < 3.11, use tomli instead of tomllib
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        with open("pyproject.toml", "rb") as f:
            content = tomllib.load(f)
            __version__ = content["tool"]["poetry"]["version"]
    except FileNotFoundError:
        __version__ = "undefined"

__all__ = ["__version__"]
