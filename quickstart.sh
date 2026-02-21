#!/bin/bash
# Quick setup script for ci-sanity development

set -e

echo "Setting up ci-sanity..."

# Create directory structure
echo "Creating directory structure..."
mkdir -p src/ci_sanity/rules

# Create __init__.py files
echo "Creating package files..."

cat > src/ci_sanity/__init__.py << 'EOF'
"""
ci-sanity: catch CI failures before you push.
"""

__version__ = '0.1.0'

from ci_sanity.checker import Checker
from ci_sanity.config import Config
from ci_sanity.models import Issue, Colors

__all__ = ['Checker', 'Config', 'Issue', 'Colors']
EOF

cat > src/ci_sanity/rules/__init__.py << 'EOF'
"""
Validation rules for ci-sanity.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ci_sanity.models import Issue


class Rule(ABC):
    """Base class for all validation rules."""
    
    @abstractmethod
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        pass
    
    def get_jobs(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        jobs = workflow.get('jobs', {})
        if not isinstance(jobs, dict):
            return {}
        return jobs
    
    def get_steps(self, job_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        steps = job_config.get('steps', [])
        if not isinstance(steps, list):
            return []
        return [s for s in steps if isinstance(s, dict)]


__all__ = ['Rule']
EOF

echo "Directory structure created."
echo ""
echo "Next steps:"
echo "1. Copy all Python files to src/ci_sanity/ and src/ci_sanity/rules/"
echo "2. Run: pip install -e ."
echo "3. Test: ci-sanity check"
echo ""
echo "To publish to PyPI:"
echo "1. Install build tools: pip install build twine"
echo "2. Build package: python -m build"
echo "3. Upload to TestPyPI: python -m twine upload --repository testpypi dist/*"
echo "4. Test install: pip install --index-url https://test.pypi.org/simple/ ci-sanity"
echo "5. Upload to PyPI: python -m twine upload dist/*"
echo ""
echo "Done!"