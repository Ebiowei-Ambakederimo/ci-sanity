"""
Runner compatibility validation rule.
"""

from typing import List, Dict, Any, Set
import re

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
            
            # Normalize to list or keep single value
            runners = [runs_on] if isinstance(runs_on, str) else runs_on

            # If runs-on is a list-like configuration, accept it if it contains
            # a self-hosted entry (exact or prefixed), otherwise validate
            # that at least one listed runner is in the known set.
            if isinstance(runners, list):
                # Filter non-string entries
                runners_str = [r for r in runners if isinstance(r, str)]

                # Skip variables like ${{ ... }}
                runners_str = [r for r in runners_str if not r.strip().startswith('${{')]

                has_self_hosted = (
                    'self-hosted' in runners_str or
                    any(r.startswith('self-hosted') for r in runners_str)
                )

                if not has_self_hosted:
                    # If none are self-hosted, require at least one known runner
                    if not any(r in self.VALID_GITHUB_RUNNERS for r in runners_str):
                        # Report unknown runner(s)
                        issues.append(Issue(
                            severity='warning',
                            file=file_path,
                            job=job_name,
                            step=None,
                            message=f'unknown runner list: {runners}',
                            fix='use ubuntu-latest, windows-latest, or macos-latest'
                        ))

                # For Windows docker checks, if any runner string looks like windows,
                # run the docker-on-windows validation once for the job.
                if any(isinstance(r, str) and 'windows' in r.lower() for r in runners):
                    issues.extend(
                        self._check_docker_on_windows(job_config, job_name, file_path)
                    )
            else:
                # Single runner string path
                runner = runners
                if not isinstance(runner, str):
                    continue

                # Skip variables
                if runner.startswith('${{'):
                    continue

                # Check validity for single string
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

                if 'windows' in runner.lower():
                    issues.extend(
                        self._check_docker_on_windows(job_config, job_name, file_path)
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
        
        # Prepare regex for docker CLI operations (case-insensitive)
        docker_cli_re = re.compile(r'(?i)(^|\s)docker\s+(run|build|compose|login|pull|push)\b')

        # Known actions that require Docker daemon (explicit identifiers)
        known_docker_actions = {
            'docker/build-push-action',
            'docker/login-action',
            'docker/setup-buildx-action',
        }

        for i, step in enumerate(steps):
            uses = step.get('uses', '') or ''
            run = step.get('run', '') or ''

            # Detect a job-level container declaration
            has_container = bool(job_config.get('container')) or ('container' in job_config)

            # Detect docker CLI usage in non-comment lines
            found_docker_cli = False
            for line in str(run).splitlines():
                stripped = line.lstrip()
                if not stripped or stripped.startswith('#'):
                    continue
                if docker_cli_re.search(line):
                    found_docker_cli = True
                    break

            # Detect known docker actions by checking explicit action ids
            uses_lower = uses.lower()
            found_docker_action = any(a in uses_lower for a in known_docker_actions) or uses_lower.startswith('docker/')

            has_docker = has_container or found_docker_cli or found_docker_action

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