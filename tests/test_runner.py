#!/usr/bin/env python
"""
Test runner for Layer Painter add-on.

Usage:
  python test_runner.py                 # Run all tests
  python test_runner.py --qw1           # Run QW-1 tests only
  python test_runner.py --performance   # Run performance tests
  python test_runner.py --coverage      # Run with coverage report
  python test_runner.py -v              # Verbose output
"""

import sys
import pytest
import argparse
from pathlib import Path


def main():
    """Run test suite with appropriate configuration."""
    parser = argparse.ArgumentParser(description="Run Layer Painter test suite")
    
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--qw1', action='store_true',
                        help='Run QW-1 (UID duplication) tests only')
    parser.add_argument('--qw2', action='store_true',
                        help='Run QW-2 (input validation) tests only')
    parser.add_argument('--qw3', action='store_true',
                        help='Run QW-3 (depsgraph optimization) tests only')
    parser.add_argument('--qw4', action='store_true',
                        help='Run QW-4 (image import) tests only')
    parser.add_argument('--performance', action='store_true',
                        help='Run performance tests only')
    parser.add_argument('--coverage', action='store_true',
                        help='Generate coverage report')
    parser.add_argument('--html', action='store_true',
                        help='Generate HTML report')
    parser.add_argument('-k', '--keyword', type=str,
                        help='Run tests matching keyword')
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    # Verbosity
    if args.verbose:
        pytest_args.append('-vv')
    else:
        pytest_args.append('-v')
    
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Test selection
    if args.qw1:
        pytest_args.append(str(test_dir / 'test_qw1_uid_duplication.py'))
    elif args.qw2:
        pytest_args.append(str(test_dir / 'test_qw2_input_validation.py'))
    elif args.qw3:
        pytest_args.append(str(test_dir / 'test_qw3_depsgraph_optimization.py'))
    elif args.qw4:
        pytest_args.append(str(test_dir / 'test_qw4_image_import.py'))
    else:
        # All tests
        pytest_args.append(str(test_dir))
    
    # Keyword filter
    if args.keyword:
        pytest_args.append(f'-k={args.keyword}')
    
    # Performance tests
    if not args.performance:
        pytest_args.append('-m=not performance')
    
    # Coverage
    if args.coverage:
        pytest_args.extend([
            '--cov=layer_painter',
            '--cov-report=term-missing',
        ])
        if args.html:
            pytest_args.append('--cov-report=html')
    
    # HTML report
    if args.html and not args.coverage:
        pytest_args.append('--html=report.html')
        pytest_args.append('--self-contained-html')
    
    # Show output
    pytest_args.append('-s')
    
    # Run tests
    return pytest.main(pytest_args)


if __name__ == '__main__':
    sys.exit(main())
