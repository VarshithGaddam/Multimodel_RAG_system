"""
Test runner script for the Multimodal RAG System.

This script runs all unit tests and displays results.
"""

import subprocess
import sys


def run_tests():
    """Run all unit tests."""
    print("=" * 60)
    print("Running Unit Tests for Multimodal RAG System")
    print("=" * 60)
    print()
    
    try:
        # Run pytest with verbose output
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=False,
            text=True
        )
        
        print()
        print("=" * 60)
        if result.returncode == 0:
            print("✓ All tests passed!")
        else:
            print("✗ Some tests failed. See output above.")
        print("=" * 60)
        
        return result.returncode
        
    except FileNotFoundError:
        print("✗ pytest not found. Install it with: pip install pytest")
        return 1
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1


def run_tests_with_coverage():
    """Run tests with coverage report."""
    print("=" * 60)
    print("Running Tests with Coverage")
    print("=" * 60)
    print()
    
    try:
        # Run pytest with coverage
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", 
             "--cov=app", "--cov-report=term-missing"],
            capture_output=False,
            text=True
        )
        
        print()
        print("=" * 60)
        if result.returncode == 0:
            print("✓ All tests passed with coverage report!")
        else:
            print("✗ Some tests failed. See output above.")
        print("=" * 60)
        
        return result.returncode
        
    except FileNotFoundError:
        print("✗ pytest-cov not found. Install it with: pip install pytest-cov")
        return 1
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--coverage":
        exit_code = run_tests_with_coverage()
    else:
        exit_code = run_tests()
        
        if exit_code == 0:
            print("\nTip: Run with --coverage flag for coverage report:")
            print("  python run_tests.py --coverage")
    
    sys.exit(exit_code)
