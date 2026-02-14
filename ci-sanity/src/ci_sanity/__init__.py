# """Top-level package for ci-sanity.

# This file makes the `ci_sanity` package explicit so editors and analyzers
# can resolve imports reliably.
# """

# __all__ = ["config", "models"]

# # Expose commonly used symbols for convenience
# from .config import Config  # noqa: F401
# from .models import *  # noqa: F401, F403
# src/ci_sanity/__init__.py
"""
ci-sanity: catch CI failures before you push.
"""

__version__ = '0.1.0'

from ci_sanity.checker import Checker
from ci_sanity.config import Config
from ci_sanity.models import Issue, Colors

__all__ = ['Checker', 'Config', 'Issue', 'Colors']