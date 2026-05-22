# main.py
import sys
from compiler import Compiler
from lexer import Lexer
from parser import Parser
from compiler_tester import CompilerTester

def print_usage():
    """Print usage information"""
    print("""
Usage:
    python main.py compile <source_file>        - Compile a source file
    python main.py compile-string "<code>"      - Compile a string of code
    python main.py tokens <source_file>         - Show tokens from source file
    python main.py test                         - Run all tests
    python main.py demo                         - Run demo compilation
    
Examples:
    python main.py compile program.txt
    python main.py compile-string "x := 42;"
    python main.py tokens program.txt
    python main.py test
    python main.py demo
""")

def compile_file(filename):
    """Compile a source file"""
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
        
        compiler = Compiler()
        result = compiler.compile(source_code)
        
        print("\n" + "=" * 60)
        print("COMPILATION RESULT")
        print("=" * 60)
        print("\nC Code Fragment:")
        print("-" * 60)
        print(result)
        print("=" * 60)
        
        return result
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def compile_string(code_string):
    """Compile a string of code"""
    try:
        compiler = Compiler()
        result = compiler.compile(code_string)
        
        print("\n" + "=" * 60)
        print("COMPILATION RESULT")
        print("=" * 60)
        print(f"\nInput: {code_string}")
        print(f"\nOutput: {result}")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def show_tokens(filename):
    """Show tokens from a source file"""
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
        
        lexer = Lexer()
        tokens = lexer.tokenize(source_code)
        
        print("\n" + "=" * 60)
        print("TOKENS")
        print("=" * 60)
        for token in tokens:
            print(f"Line {token.lineno}: {token.type} = '{token.value}'")
        print("=" * 60)
        
        return tokens
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_demo():
    """Run a demo compilation"""
    print("\n" + "=" * 60)
    print("DEMO COMPILATION - VARIANT 11")
    print("=" * 60)
    
    demo_program = """
    # This is a sample program in the custom language
    count := 0;
    value := 10;
    status := 0;
    
    # Conditional statement
    a eq b or not c eq d if count := 5;
    
    # Arithmetic operations
    result := mul 5 3;
    quotient := div 10 2;
    root := sqrt 16;
    
    # Nested conditionals
    x := 1;
    condition1 eq condition2 if x := 2;
    condition3 eq condition4 if x := 3;
    
    # Final assignment
    final := 100;
    """
    
    print("\nINPUT (Custom Language):")
    print("-" * 60)
    print(demo_program)
    
    try:
        compiler = Compiler()
        result = compiler.compile(demo_program)
        
        print("\nOUTPUT (C Code Fragment):")
        print("-" * 60)
        print(result)
        print("=" * 60)
        
    except Exception as e:
        print(f"\nCompilation failed: {e}")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "compile" and len(sys.argv) >= 3:
        compile_file(sys.argv[2])
    
    elif command == "compile-string" and len(sys.argv) >= 3:
        compile_string(sys.argv[2])
    
    elif command == "tokens" and len(sys.argv) >= 3:
        show_tokens(sys.argv[2])
    
    elif command == "test":
        tester = CompilerTester()
        tester.run_all_tests()
        tester.generate_test_report()
    
    elif command == "demo":
        run_demo()
    
    else:
        print_usage()

if __name__ == "__main__":
    main()