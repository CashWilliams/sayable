from importlib.metadata import PackageNotFoundError, version

from .config import ConfigError, load_config
from .normalizer import normalize_text
from .pipeline import transform

try:
    __version__ = version("sayable")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "ConfigError",
    "load_config",
    "normalize_text",
    "transform",
    "__version__",
]
