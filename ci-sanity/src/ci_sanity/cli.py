"""
Command-line interface for ci-sanity.
"""

import sys
import argparse

from ci_sanity.config import Config
from ci_sanity.checker import Checker
from ci_sanity.models import Colors


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='ci-sanity',
        description='catch CI failures before you push',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
examples:
  ci-sanity check
  ci-sanity check --path ./my-repo
  ci-sanity check --strict
  ci-sanity check --config custom-config.yml
        '''
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='check',
        help='command to run (default: check)'
    )
    
    parser.add_argument(
        '--path',
        default='.',
        help='path to check (default: current directory)'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='treat warnings as errors'
    )
    
    parser.add_argument(
        '--config',
        help='path to config file (default: .ci-sanity.yml)'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='disable colored output'
    )
    
    args = parser.parse_args()
    
    # Handle command
    if args.command != 'check':
        print(f'{Colors.RED}unknown command: {args.command}{Colors.END}')
        print('use: ci-sanity check')
        return 1
    
    # Disable colors if requested
    if args.no_color or not sys.stdout.isatty():
        Colors.disable()
    
    # Load config
    config = Config(args.config)
    
    # Apply strict mode
    if args.strict:
        config.set_strict(True)
    
    # Create checker
    checker = Checker(config)
    
    # Find workflows
    workflows = checker.find_workflow_files(args.path)
    
    if not workflows:
        print(f'{Colors.YELLOW}no workflow files found{Colors.END}')
        print(f'{Colors.GRAY}looking for .github/workflows/*.yml or .gitlab-ci.yml{Colors.END}')
        return 0
    
    # Check workflows
    issues = checker.check_all(args.path)
    
    # Print results
    checker.print_issues(issues)
    
    # Get exit code
    exit_code = checker.get_exit_code(issues)
    
    # Print summary
    if issues:
        error_count = sum(1 for i in issues if i.is_error())
        warning_count = sum(1 for i in issues if i.is_warning())
        
        print()
        if error_count > 0:
            print(f'{Colors.RED}{error_count} error(s){Colors.END}', end='')
            if warning_count > 0:
                print(f', {Colors.YELLOW}{warning_count} warning(s){Colors.END}')
            else:
                print()
        else:
            print(f'{Colors.YELLOW}{warning_count} warning(s){Colors.END}')
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())