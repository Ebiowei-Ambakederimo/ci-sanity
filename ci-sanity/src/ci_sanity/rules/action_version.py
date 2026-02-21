"""
Action version validation rule.
"""

from typing import List, Dict, Any

from ci_sanity.models import Issue
from ci_sanity.rules import Rule


class ActionVersionRule(Rule):
    """Validates action version pinning."""
    
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        """Check for action version issues."""
        issues = []
        jobs = self.get_jobs(workflow)
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            
            steps = self.get_steps(job_config)
            
            for i, step in enumerate(steps):
                uses = step.get('uses')
                if not uses:
                    continue
                
                # Check for local actions (start with ./) - must come first
                if uses.startswith('./'):
                    continue
                
                # Check for Docker actions - must come before version checks
                if uses.startswith('docker://'):
                    continue
                
                # Check for @master or @main
                if '@master' in uses or '@main' in uses:
                    action_name = uses.split('@')[0]
                    # Detect which token matched
                    matched_ref = '@master' if '@master' in uses else '@main'
                    issues.append(Issue(
                        severity='warning',
                        file=file_path,
                        job=job_name,
                        step=i,
                        message=f'{action_name}{matched_ref} = chaos energy. pin a version.',
                        fix='use @v3 or a specific commit sha'
                    ))
                    continue
                
                # Check for missing version
                if '@' not in uses:
                    issues.append(Issue(
                        severity='error',
                        file=file_path,
                        job=job_name,
                        step=i,
                        message=f'action {uses} has no version',
                        fix='add @v3 or specific version'
                    ))
                    continue
        
        return issues