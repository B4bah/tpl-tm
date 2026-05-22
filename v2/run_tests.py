# run_tests.py
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def main():
    print("\n" + "=" * 80)
    print("RUNNING VARIANT 11 COMPILER TESTS")
    print("=" * 80)
    
    # Import here to avoid circular imports
    from compiler_tester import CompilerTester
    
    tester = CompilerTester()
    passed, failed = tester.run_all_tests()
    
    # Generate detailed report
    tester.generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()