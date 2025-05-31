#!/usr/bin/env python3
"""
Test Runner for File Compression and Indexing System
This script runs all tests and generates a comprehensive report
"""

import unittest
import os
import sys
import time
import datetime
import argparse
from pathlib import Path
import json

# Configure test environment
TEST_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "tests")))
TEST_RESULTS_DIR = TEST_DIR / "test_results"
TEST_RESULTS_DIR.mkdir(exist_ok=True)

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def discover_tests(test_type=None):
    """
    Discover tests in the test directory
    
    Args:
        test_type (str, optional): Type of tests to run ('unit', 'integration', 'performance', 'user_acceptance')
                                   If None, runs all tests.
    
    Returns:
        unittest.TestSuite: Test suite containing discovered tests
    """
    if test_type:
        if test_type not in ['unit', 'integration', 'performance', 'user_acceptance']:
            print(f"Invalid test type: {test_type}")
            sys.exit(1)
        
        test_dir = TEST_DIR / test_type
        return unittest.defaultTestLoader.discover(str(test_dir), pattern="test_*.py")
    else:
        return unittest.defaultTestLoader.discover(str(TEST_DIR), pattern="test_*.py")

def run_tests(test_suite, verbosity=2):
    """
    Run tests and return results
    
    Args:
        test_suite (unittest.TestSuite): Test suite to run
        verbosity (int): Verbosity level (1-3)
    
    Returns:
        unittest.TestResult: Results of test run
    """
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(test_suite)

def generate_report(result, test_type=None, execution_time=None):
    """
    Generate a test report
    
    Args:
        result (unittest.TestResult): Test results
        test_type (str, optional): Type of tests run
        execution_time (float, optional): Execution time in seconds
    
    Returns:
        dict: Report data
    """
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "test_type": test_type if test_type else "all",
        "total_tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "successful": result.testsRun - len(result.failures) - len(result.errors),
        "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100 if result.testsRun > 0 else 0,
        "execution_time": execution_time
    }
    
    # Add detailed failure and error information
    report["failure_details"] = []
    for test, traceback in result.failures:
        report["failure_details"].append({
            "test": str(test),
            "traceback": traceback
        })
    
    report["error_details"] = []
    for test, traceback in result.errors:
        report["error_details"].append({
            "test": str(test),
            "traceback": traceback
        })
    
    return report

def save_report(report, test_type=None):
    """
    Save test report to a file
    
    Args:
        report (dict): Report data
        test_type (str, optional): Type of tests run
    
    Returns:
        Path: Path to the saved report
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = TEST_RESULTS_DIR / f"test_report_{report['test_type']}_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_file

def print_report_summary(report):
    """
    Print a summary of the test report
    
    Args:
        report (dict): Report data
    """
    print("\n=======================================")
    print(f"TEST REPORT: {report['test_type'].upper()} TESTS")
    print("=======================================")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Total Tests: {report['total_tests']}")
    print(f"Successful: {report['successful']} ({report['success_rate']:.1f}%)")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Execution time: {report['execution_time']:.2f} seconds")
    print("=======================================")
    
    # Print failure summary if any
    if report['failures']:
        print("\nFAILURES:")
        for i, failure in enumerate(report['failure_details'], 1):
            print(f"{i}. {failure['test']}")
    
    # Print error summary if any
    if report['errors']:
        print("\nERRORS:")
        for i, error in enumerate(report['error_details'], 1):
            print(f"{i}. {error['test']}")
    
    print("\n")

def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="Run tests for the File Compression and Indexing System")
    
    parser.add_argument('--type', '-t', choices=['unit', 'integration', 'performance', 'user_acceptance'], 
                        help="Type of tests to run (default: all)")
    parser.add_argument('--verbose', '-v', action='count', default=1,
                        help="Increase verbosity (can be used multiple times)")
    parser.add_argument('--generate-test-data', '-g', action='store_true',
                        help="Generate test data before running tests")
    
    args = parser.parse_args()
    
    # Generate test data if requested
    if args.generate_test_data:
        from tests.test_config import generate_test_dataset
        print("Generating test data...")
        generate_test_dataset()
        print("Test data generation complete.")
    
    print(f"Running {'all' if not args.type else args.type} tests...")
    start_time = time.time()
    
    test_suite = discover_tests(args.type)
    result = run_tests(test_suite, verbosity=args.verbose)
    
    execution_time = time.time() - start_time
    
    # Generate and save report
    report = generate_report(result, args.type, execution_time)
    report_file = save_report(report, args.type)
    
    # Print report summary
    print_report_summary(report)
    print(f"Detailed report saved to {report_file}")
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main())