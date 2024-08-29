from importlib import resources

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# Version of the realpython-reader package
__version__ = "0.0.1"

# Read URL of the Real Python feed from config file
_cfg = tomllib.loads(resources.read_text("htms", "config.toml"))
URL = _cfg["feed"]["url"]
