"""
Secrets validation rule.
"""

import re
from typing import List, Dict, Any, Set, Optional

from ci_sanity.models import Issue
from ci_sanity.rules import Rule


class SecretsRule(Rule):
    """Validates secret references."""
    
    SECRET_PATTERN = re.compile(r'\$\{\{\s*secrets\.(\w+)\s*\}\}')
    
    def __init__(self, declared_secrets: List[str]):
        """Initialize with list of declared secrets."""
        self.declared_secrets: Set[str] = set(declared_secrets)
    
    def check(self, workflow: Dict[str, Any], file_path: str) -> List[Issue]:
        """Check for secret reference issues."""
        issues = []
        jobs = self.get_jobs(workflow)
        
        for job_name, job_config in jobs.items():
            if not isinstance(job_config, dict):
                continue
            
            # Check job-level env (coerce None to empty dict)
            env = job_config.get('env') or {}
            self._check_dict_for_secrets(
                env,
                job_name,
                None,
                file_path,
                issues
            )
            
            # Check steps
            steps = self.get_steps(job_config)
            for i, step in enumerate(steps):
                # Check step env (coerce None to empty dict)
                step_env = step.get('env') or {}
                self._check_dict_for_secrets(
                    step_env,
                    job_name,
                    i,
                    file_path,
                    issues
                )
                
                # Check with parameters (coerce None to empty dict)
                step_with = step.get('with') or {}
                self._check_dict_for_secrets(
                    step_with,
                    job_name,
                    i,
                    file_path,
                    issues
                )
                
                # Check run commands
                run_cmd = step.get('run', '')
                if run_cmd:
                    self._check_string_for_secrets(
                        run_cmd,
                        job_name,
                        i,
                        file_path,
                        issues
                    )
        
        return issues
    
    def _check_dict_for_secrets(
        self,
        d: Dict[str, Any],
        job: str,
        step: Optional[int],
        file: str,
        issues: List[Issue]
    ):
        """Check dictionary values for secret references."""
        for key, value in d.items():
            if isinstance(value, str):
                self._check_string_for_secrets(value, job, step, file, issues)
    
    def _check_string_for_secrets(
        self,
        s: str,
        job: str,
        step: Optional[int],
        file: str,
        issues: List[Issue]
    ):
        """Check string for secret references."""
        matches = self.SECRET_PATTERN.findall(s)
        
        for secret_name in matches:
            if secret_name not in self.declared_secrets:
                # Try to suggest correct name
                suggestion = self._suggest_secret(secret_name)
                
                fix_msg = 'add to .ci-sanity.yml secrets list'
                if suggestion:
                    fix_msg = f'did you mean {suggestion}? or add to .ci-sanity.yml'
                
                issues.append(Issue(
                    severity='warning',
                    file=file,
                    job=job,
                    step=step,
                    message=f'secret {secret_name} not found. typo or optimism?',
                    fix=fix_msg
                ))
    
    def _suggest_secret(self, name: str) -> Optional[str]:
        """Suggest correct secret name based on fuzzy match."""
        name_lower = name.lower()
        
        # Exact match (different case)
        for declared in self.declared_secrets:
            if declared.lower() == name_lower:
                return declared
        
        # Single character difference
        for declared in self.declared_secrets:
            if len(declared) == len(name):
                diff = sum(a != b for a, b in zip(declared.lower(), name_lower))
                if diff == 1:
                    return declared
        
        # Close match (edit distance = 2)
        for declared in self.declared_secrets:
            if abs(len(declared) - len(name)) <= 1:
                if self._edit_distance(declared.lower(), name_lower) <= 2:
                    return declared
        
        return None
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between strings."""
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        
        if len(s2) == 0:
            return len(s1)
        
        previous = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous[j + 1] + 1
                deletions = current[j] + 1
                substitutions = previous[j] + (c1 != c2)
                current.append(min(insertions, deletions, substitutions))
            previous = current
        
        return previous[-1]