# src/ci_sanity/__init__.py
"""
ci-sanity: catch CI failures before you push.
"""

__version__ = '0.1.0'

from ci_sanity.checker import Checker
from ci_sanity.config import Config
from ci_sanity.models import Issue, Colors

__all__ = ['Checker', 'Config', 'Issue', 'Colors']