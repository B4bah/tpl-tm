# compiler_tester.py
from compiler import Compiler

class CompilerTester:
    def __init__(self):
        self.compiler = None
        self.passed = 0
        self.failed = 0
    
    def setup(self):
        """Create a new compiler instance for each test"""
        self.compiler = Compiler()
    
    def teardown(self):
        """Clean up after test"""
        if self.compiler:
            self.compiler.reset()
    
    def run_correct_tests(self):
        """Run tests that should succeed"""
        test_cases = [
            {
                "name": "Simple integer assignment",
                "input": "x := 42;",
                "expected": "x = 42;"
            },
            {
                "name": "Simple real assignment",
                "input": "pi := 3.14159;",
                "expected": "pi = 3.14159;"
            },
            {
                "name": "Assignment with real exponent",
                "input": "value := 3.14e-5;",
                "expected": "value = 3.14e-05;"
            },
            {
                "name": "Assignment with multiplication (prefix)",
                "input": "result := mul 5 3;",
                "expected": "result = (5 * 3);"
            },
            {
                "name": "Assignment with division (prefix)",
                "input": "quotient := div 10 2;",
                "expected": "quotient = (10 / 2);"
            },
            {
                "name": "Assignment with addition (prefix)",
                "input": "sum := add 5 3;",
                "expected": "sum = (5 + 3);"
            },
            {
                "name": "Assignment with subtraction (prefix)",
                "input": "diff := sub 10 3;",
                "expected": "diff = (10 - 3);"
            },
            {
                "name": "Assignment with square root",
                "input": "root := sqrt 16;",
                "expected": "root = sqrt(16);"
            },
            {
                "name": "Conditional with equality",
                "input": "x := 10; a eq b if x := 5;",
                "expected_contains": ["if ((a == b)) {", "x = 5;"]
            },
            {
                "name": "Conditional with not equal",
                "input": "status := 0; value neq threshold if status := 1;",
                "expected_contains": ["if ((value != threshold)) {", "status = 1;"]
            },
            {
                "name": "Conditional with OR",
                "input": "flag := 0; a eq b or c eq d if flag := 1;",
                "expected_contains": ["if (((a == b) || (c == d))) {", "flag = 1;"]
            },
            {
                "name": "Conditional with NOT",
                "input": "result := 0; not a eq b if result := 1;",
                "expected_contains": ["if (!((a == b))) {", "result = 1;"]
            },
            {
                "name": "Multiple statements",
                "input": "a := 1; b := 2; c := 3;",
                "expected": "a = 1;\nb = 2;\nc = 3;"
            },
            {
                "name": "Whitespace handling",
                "input": "x:=42;",
                "expected": "x = 42;"
            },
            {
                "name": "Comment handling",
                "input": "# This is a comment\nx := 42;",
                "expected": "x = 42;"
            }
        ]
        
        print("\n" + "=" * 80)
        print("RUNNING CORRECT TEST CASES")
        print("=" * 80)
        
        for i, test in enumerate(test_cases, 1):
            self.setup()
            try:
                result = self.compiler.compile(test["input"])
                
                if "expected" in test:
                    # Normalize whitespace for comparison
                    expected_normalized = test["expected"].strip()
                    result_normalized = result.strip()
                    
                    if result_normalized == expected_normalized:
                        print(f"✓ Test {i}: {test['name']} - PASSED")
                        self.passed += 1
                    else:
                        print(f"✗ Test {i}: {test['name']} - FAILED")
                        print(f"  Expected: '{test['expected']}'")
                        print(f"  Got: '{result}'")
                        self.failed += 1
                
                elif "expected_contains" in test:
                    all_found = all(part in result for part in test["expected_contains"])
                    if all_found:
                        print(f"✓ Test {i}: {test['name']} - PASSED")
                        self.passed += 1
                    else:
                        print(f"✗ Test {i}: {test['name']} - FAILED")
                        print(f"  Expected to contain: {test['expected_contains']}")
                        print(f"  Got: '{result}'")
                        self.failed += 1
                
                self.teardown()
                
            except Exception as e:
                print(f"✗ Test {i}: {test['name']} - FAILED with exception: {str(e)}")
                self.failed += 1
                self.teardown()
    
    def run_all_tests(self):
        """Run all test suites"""
        self.passed = 0
        self.failed = 0
        
        self.run_correct_tests()
        
        print("\n" + "=" * 80)
        print(f"FINAL RESULTS: {self.passed} passed, {self.failed} failed")
        print("=" * 80)
        
        return self.passed, self.failed
    
    def generate_test_report(self):
        """Generate a detailed test report"""
        report = f"""
TEST REPORT - VARIANT 11 COMPILER
=================================
Total Tests Run: {self.passed + self.failed}
Passed: {self.passed}
Failed: {self.failed}
Success Rate: {(self.passed/(self.passed+self.failed)*100) if (self.passed+self.failed) > 0 else 0:.1f}%

Variant Specifications:
- Syntax: Sequence of shortened conditional operators (statement if condition)
- Identifiers: Max 20 characters, delimiter-separated
- Keywords: Not marked with special symbols
- Operators: Service words (eq, neq, or, not, mul, div, add, sub, sqrt)
- Numbers: Real decimal with exponent
- Logical ops: NEQ, OR, NOT
- Arithmetic ops: ADD, SUB, MUL, DIV, SQRT
- Operand types: Integer constants, Integer variables, Real constants, Boolean variables
"""
        
        with open("test_report.txt", "w", encoding='utf-8') as f:
            f.write(report)
        
        print("\nTest report saved to test_report.txt")
        return report


if __name__ == "__main__":
    tester = CompilerTester()
    tester.run_all_tests()
    tester.generate_test_report()