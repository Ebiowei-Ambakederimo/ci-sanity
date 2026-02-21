"""
Step order validation rule.
"""

from typing import List, Dict, Any

from ci_sanity.models import Issue
from ci_sanity.rules import Rule


class StepOrderRule(Rule):
    """Validates logical step ordering."""
    
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        """Check for step order issues."""
        issues = []
        jobs = self.get_jobs(workflow)
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            
            issues.extend(
                self._check_checkout_order(job_config, job_name, file_path)
            )
            issues.extend(
                self._check_cache_order(job_config, job_name, file_path)
            )
        
        return issues
    
    def _check_checkout_order(
        self, 
        job_config: Dict[str, Any], 
        job_name: str, 
        file_path: str
    ) -> List[Issue]:
        """Check that checkout happens before other actions."""
        issues = []
        steps = self.get_steps(job_config)
        
        has_checkout = False
        checkout_index = -1
        
        for i, step in enumerate(steps):
            uses = step.get('uses', '')
            
            # Found checkout
            if 'actions/checkout' in uses:
                has_checkout = True
                checkout_index = i
                continue
            
            # Action before checkout
            if uses and not has_checkout:
                # Skip certain actions that don't need checkout
                skip_actions = [
                    'actions/cache',
                    'actions/setup-',
                ]
                
                should_skip = any(skip in uses for skip in skip_actions)
                
                if not should_skip:
                    issues.append(Issue(
                        severity='warning',
                        file=file_path,
                        job=job_name,
                        step=i,
                        message='step runs before checkout',
                        fix='move actions/checkout to first step'
                    ))
        
        return issues
    
    def _check_cache_order(
        self, 
        job_config: Dict[str, Any], 
        job_name: str, 
        file_path: str
    ) -> List[Issue]:
        """Check that cache happens before install."""
        issues = []
        steps = self.get_steps(job_config)
        
        install_commands = [
            'npm install',
            'npm ci',
            'yarn install',
            'pip install',
            'poetry install',
            'bundle install',
        ]
        
        for i, step in enumerate(steps):
            run = step.get('run', '')
            
            # Check if this is an install step
            is_install = any(cmd in run.lower() for cmd in install_commands)
            
            if is_install:
                # Look for cache after this
                for j in range(i + 1, len(steps)):
                    future_step = steps[j]
                    future_uses = future_step.get('uses', '')
                    
                    if 'actions/cache' in future_uses:
                        issues.append(Issue(
                            severity='warning',
                            file=file_path,
                            job=job_name,
                            step=i,
                            message='install runs before cache',
                            fix='move cache step before install'
                        ))
                        break
        
        return issues