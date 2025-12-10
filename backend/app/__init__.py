"""
Основной пакет приложения
"""

from . import model
from . import schemes
from . import crud
from . import core
from . import api

# Версия приложения
__version__ = "1.0.0"

__all__ = [
    "model",
    "schemes",
    "crud",
    "api",
    "core",
    "__version__",
]