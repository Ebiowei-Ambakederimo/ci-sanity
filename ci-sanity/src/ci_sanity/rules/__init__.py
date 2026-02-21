# src/ci_sanity/rules/__init__.py
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
        """
        Check workflow for issues.
        
        Args:
            workflow: Parsed workflow dictionary
            file_path: Path to workflow file
            
        Returns:
            List of issues found
        """
        pass
    
    def get_jobs(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to safely get jobs from workflow."""
        jobs = workflow.get('jobs', {})
        if not isinstance(jobs, dict):
            return {}
        return jobs
    
    def get_steps(self, job_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Helper to safely get steps from job."""
        steps = job_config.get('steps', [])
        if not isinstance(steps, list):
            return []
        return [s for s in steps if isinstance(s, dict)]


__all__ = ['Rule']