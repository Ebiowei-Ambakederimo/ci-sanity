"""
Runner compatibility validation rule.
"""

from typing import List, Dict, Any, Set

from ci_sanity.models import Issue
from ci_sanity.rules import Rule


class RunnerCompatibilityRule(Rule):
    """Validates runner configuration and compatibility."""
    
    VALID_GITHUB_RUNNERS: Set[str] = {
        'ubuntu-latest', 'ubuntu-22.04', 'ubuntu-20.04',
        'windows-latest', 'windows-2022', 'windows-2019',
        'macos-latest', 'macos-13', 'macos-12', 'macos-11',
    }
    
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        """Check for runner compatibility issues."""
        issues = []
        jobs = self.get_jobs(workflow)
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            
            # Check runs-on exists
            runs_on = job_config.get('runs-on')
            if not runs_on:
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job=job_name,
                    step=None,
                    message='missing runs-on',
                    fix='add runs-on: ubuntu-latest'
                ))
                continue
            
            # Normalize to list
            runners = [runs_on] if isinstance(runs_on, str) else runs_on
            
            # Check each runner
            for runner in runners:
                if not isinstance(runner, str):
                    continue
                
                # Skip variables
                if runner.startswith('${{'):
                    continue
                
                # Check validity
                is_valid = (
                    runner in self.VALID_GITHUB_RUNNERS or
                    runner.startswith('self-hosted')
                )
                
                if not is_valid:
                    issues.append(Issue(
                        severity='warning',
                        file=file_path,
                        job=job_name,
                        step=None,
                        message=f'unknown runner: {runner}',
                        fix='use ubuntu-latest, windows-latest, or macos-latest'
                    ))
                
                # Check for Docker on Windows
                if 'windows' in runner.lower():
                    issues.extend(
                        self._check_docker_on_windows(
                            job_config, job_name, file_path
                        )
                    )
        
        return issues
    
    def _check_docker_on_windows(
        self, 
        job_config: Dict[str, Any], 
        job_name: str, 
        file_path: str
    ) -> List[Issue]:
        """Check for Docker usage on Windows runners."""
        issues = []
        steps = self.get_steps(job_config)
        
        for i, step in enumerate(steps):
            uses = step.get('uses', '')
            run = step.get('run', '')
            
            # Check for Docker
            has_docker = (
                'docker' in uses.lower() or
                'docker' in run.lower()
            )
            
            if has_docker:
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job=job_name,
                    step=i,
                    message='uses docker but runner is windows. pick a side.',
                    fix='use ubuntu-latest for docker'
                ))
        
        return issues