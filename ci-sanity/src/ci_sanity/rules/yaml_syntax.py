"""
YAML syntax validation rule.
"""


from typing import List, Dict, Any
from ci_sanity.models import Issue
from ci_sanity.rules import Rule

class YAMLSyntaxRule(Rule):
    """Validates YAML structure and syntax."""
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        """Check for YAML structure issues."""
        issues = []
        
        # Check workflow is a dict
        if not isinstance(workflow, dict):
            issues.append(Issue(
                severity='error',
                file=file_path,
                job='root',
                step=None,
                message='workflow file must be a dictionary',
                fix='check your YAML structure'
            ))
            return issues
        
        # GitHub Actions: validate jobs structure
        if 'jobs' in workflow:
            if not isinstance(workflow['jobs'], dict):
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job='jobs',
                    step=None,
                    message='jobs must be a dictionary',
                    fix='format: jobs:\n  job-name:\n    steps: []'
                ))
        
        # Validate each job has required fields
        jobs = self.get_jobs(workflow)
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job=job_name,
                    step=None,
                    message=f'job {job_name} must be a dictionary',
                    fix='check job structure'
                ))
                continue
            
            # Check for steps or uses (reusable workflows may use 'uses' instead of 'steps')
            if 'steps' not in job_config and 'uses' not in job_config:
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job=job_name,
                    step=None,
                    message='job missing steps or uses',
                    fix='add steps: [] to job or uses: for reusable workflow'
                ))
            elif 'steps' in job_config and not isinstance(job_config['steps'], list):
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job=job_name,
                    step=None,
                    message='steps must be a list',
                    fix='format: steps:\n  - name: step1'
                ))
        
        return issues