"""
Main checker logic for ci-sanity.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

from ci_sanity.models import Issue, Colors
from ci_sanity.config import Config
from ci_sanity.rules import Rule
from ci_sanity.rules.yaml_syntax import YAMLSyntaxRule
from ci_sanity.rules.runner_compat import RunnerCompatibilityRule
from ci_sanity.rules.action_version import ActionVersionRule
from ci_sanity.rules.secrets import SecretsRule
from ci_sanity.rules.step_order import StepOrderRule


class Checker:
    """Main CI workflow checker."""
    
    def __init__(self, config: Config):
        """Initialize checker with config."""
        self.config = config
        self.rules = self._init_rules()
    
    def _init_rules(self) -> List[Rule]:
        """Initialize all validation rules."""
        return [
            YAMLSyntaxRule(),
            RunnerCompatibilityRule(),
            ActionVersionRule(),
            SecretsRule(self.config.secrets),
            StepOrderRule(),
        ]
    
    def find_workflow_files(self, path: str) -> List[str, Any]:
        """Find all workflow files in directory."""
        path_obj = Path(path)
        workflows = []
        
        # GitHub Actions
        gh_workflows = path_obj / '.github' / 'workflows'
        if gh_workflows.exists() and gh_workflows.is_dir():
            workflows.extend([
                str(f) for f in gh_workflows.glob('*.yml')
            ])
            workflows.extend([
                str(f) for f in gh_workflows.glob('*.yaml')
            ])
        
        # GitLab CI
        gitlab_ci = path_obj / '.gitlab-ci.yml'
        if gitlab_ci.exists():
            workflows.append(str(gitlab_ci))
        
        return workflows
    
    def check_file(self, file_path: str) -> List[Issue]:
        """Check a single workflow file."""
        issues = []
        
        # Try to parse YAML
        try:
            with open(file_path) as f:
                workflow = yaml.safe_load(f)
        except yaml.YAMLError as e:
            # YAML parse error
            line = getattr(e, 'problem_mark', None)
            line_no = line.line + 1 if line else None
            
            error_msg = str(e).split(':', 1)[0] if ':' in str(e) else str(e)
            
            issues.append(Issue(
                severity='error',
                file=file_path,
                job='parse',
                step=None,
                message=f'invalid yaml: {error_msg}',
                fix='fix yaml syntax',
                line=line_no
            ))
            return issues
        except Exception as e:
            # File read error
            issues.append(Issue(
                severity='error',
                file=file_path,
                job='read',
                step=None,
                message=f'failed to read file: {e}',
                fix='check file permissions'
            ))
            return issues
        
        # Run all rules
        for rule in self.rules:
            try:
                rule_issues = rule.check(workflow, file_path)
                issues.extend(rule_issues)
            except Exception as e:
                # Rule execution error (shouldn't happen)
                issues.append(Issue(
                    severity='error',
                    file=file_path,
                    job='internal',
                    step=None,
                    message=f'rule check failed: {e}',
                    fix='report this as a bug'
                ))
        
        return issues
    
    def check_all(self, path: str = '.') -> List[Issue]:
        """Check all workflow files in directory."""
        workflows = self.find_workflow_files(path)
        
        all_issues = []
        for workflow_file in workflows:
            issues = self.check_file(workflow_file)
            all_issues.extend(issues)
        
        return all_issues
    
    def print_issues(self, issues: List[Issue]):
        """Print issues to console with formatting."""
        if not issues:
            print(f'{Colors.GREEN}✓ no issues found{Colors.END}')
            return
        
        # Group by file
        by_file: Dict[str, List[Issue]] = {}
        for issue in issues:
            if issue.file not in by_file:
                by_file[issue.file] = []
            by_file[issue.file].append(issue)
        
        # Print each file
        for file_path, file_issues in by_file.items():
            print(f'\n{Colors.BOLD}{file_path}{Colors.END}')
            
            # Group by job
            by_job: Dict[str, List[Issue]] = {}
            for issue in file_issues:
                if issue.job not in by_job:
                    by_job[issue.job] = []
                by_job[issue.job].append(issue)
            
            # Print each job
            for job, job_issues in by_job.items():
                print(f'  {Colors.BLUE}{job}{Colors.END}')
                
                # Print issues
                for issue in job_issues:
                    self._print_issue(issue)
    
    def _print_issue(self, issue: Issue):
        """Print a single issue."""
        # Color and symbol
        if issue.is_error():
            color = Colors.RED
            symbol = '✗'
        else:
            color = Colors.YELLOW
            symbol = '⚠'
        
        # Build location info
        location = ''
        if issue.step is not None:
            location += f' step[{issue.step}]'
        if issue.line is not None:
            location += f' line {issue.line}'
        
        # Print message and fix
        print(f'    {color}{symbol}{Colors.END} {issue.message}{location}')
        print(f'      {Colors.GRAY}→ {issue.fix}{Colors.END}')
    
    def get_exit_code(self, issues: List[Issue]) -> int:
        """Calculate exit code based on issues."""
        has_errors = any(i.is_error() for i in issues)
        has_warnings = any(i.is_warning() for i in issues)
        
        # Strict mode: warnings are errors
        if self.config.strict and has_warnings:
            return 2
        
        if has_errors:
            return 2
        
        if has_warnings:
            return 1
        
        return 0