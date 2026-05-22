# compiler.py
from lexer import Lexer
from parser import Parser

class Compiler:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
    
    def compile(self, source_code):
        """
        Compile source code to C fragment
        
        Args:
            source_code: String containing source code in the custom language
            
        Returns:
            String containing C code fragment
        """
        # First tokenize to check for lexical errors
        tokens = self.lexer.tokenize(source_code)
        
        # Then parse and generate C code
        c_code = self.parser.parse(source_code)
        
        return c_code
    
    def compile_with_tokens(self, source_code):
        """
        Compile and also return tokens for debugging
        
        Returns:
            Tuple (c_code, tokens)
        """
        tokens = self.lexer.tokenize(source_code)
        c_code = self.parser.parse(source_code)
        return c_code, tokens
    
    def reset(self):
        """Reset the compiler state"""
        self.lexer.reset()
        self.parser.reset()


if __name__ == "__main__":
    # Test the compiler
    compiler = Compiler()
    test_cases = [
        "x := 42;",
        "pi := 3.14159;",
        "value := 3.14e-5;",
        "result := mul 5 3;",
        "quotient := div 10 2;",
        "root := sqrt 16;",
        "a eq b if x := 5;",
    ]
    
    print("Testing Compiler")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\nInput: {test}")
        try:
            result = compiler.compile(test)
            print(f"Output: {result}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            compiler.reset()