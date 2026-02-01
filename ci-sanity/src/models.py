"""
Core data models for ci-sanity.
"""

from typing import Optional
from dataclasses import dataclass

@dataclass
class Issue:
    """Represents a problem found in a CI workflow."""
    severity: str # 'error' or 'warning'
    file: str
    job: str
    step: Optional[int]
    message: str
    fix: str
    line: Optional[int] = None

    def is_error(self) -> bool:
        """check if this is an error (vs warning)."""
        return self.severity == 'error'

    def is_warning(self) -> bool:
        """check if this is an warning."""
        return self.severity == 'warning'

class Colors:
    """Terminal color codes."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @classmethod
    def disable(cls):
        """Disable colors (for non-TTY output)."""
        cls.RED = ''
        cls.YELLOW = ''
        cls.GREEN = ''
        cls.BLUE = ''
        cls.GRAY = ''
        cls.BLOD = ''
        cls.END = ''