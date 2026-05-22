# lexer.py
import ply.lex as lex

# Reserved keywords (all operations are keywords)
reserved = {
    'if': 'IF',
    'eq': 'EQ',      # equal
    'neq': 'NEQ',    # not equal
    'or': 'OR',      # disjunction
    'and': 'AND',    # conjunction
    'not': 'NOT',    # negation
    'sqrt': 'SQRT',  # square root
    'mul': 'MUL',    # multiplication
    'div': 'DIV',    # division
    'add': 'ADD',    # addition
    'sub': 'SUB',    # subtraction
}

tokens = [
    'IDENTIFIER',
    'INTEGER_CONST',
    'REAL_CONST',
    'ASSIGN',
    'LPAREN',
    'RPAREN',
    'SEMICOLON',
] + list(reserved.values())

# Regular expressions for simple tokens
t_ASSIGN = r':='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_SEMICOLON = r';'

# Identifiers: max 20 chars, end determined by delimiter
def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    # Check if it's a reserved word
    t.type = reserved.get(t.value, 'IDENTIFIER')
    # Check identifier length (max 20 characters)
    if t.type == 'IDENTIFIER' and len(t.value) > 20:
        error_msg = f"Identifier '{t.value}' exceeds maximum length of 20 characters"
        t.lexer.lexer_error = error_msg
        raise Exception(error_msg)
    return t

# Integer constants
def t_INTEGER_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Real decimal with exponent (вещественные десятичные с порядком)
def t_REAL_CONST(t):
    r'\d+\.\d+(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+'
    t.value = float(t.value)
    return t

# Track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignore whitespace and comments
t_ignore = ' \t'

def t_comment(t):
    r'\#.*'
    # Skip comments
    pass

# Error handling
def t_error(t):
    error_msg = f"Illegal character '{t.value[0]}' at line {t.lineno}"
    t.lexer.lexer_error = error_msg
    raise Exception(error_msg)

def build_lexer():
    """Build and return the lexer"""
    lexer_obj = lex.lex()
    lexer_obj.lexer_error = None
    return lexer_obj


# Lexer class for better encapsulation
class Lexer:
    def __init__(self):
        self.lexer = build_lexer()
        self.tokens_list = []
    
    def tokenize(self, source_code):
        """Tokenize source code and return list of tokens"""
        self.lexer.lexer_error = None
        self.lexer.input(source_code)
        tokens_list = []
        
        try:
            for token in self.lexer:
                tokens_list.append(token)
        except Exception as e:
            raise Exception(f"Lexical error: {str(e)}")
        
        return tokens_list
    
    def reset(self):
        """Reset the lexer"""
        self.lexer = build_lexer()


if __name__ == "__main__":
    # Test the lexer
    lexer = Lexer()
    test_codes = [
        "x := 42;",
        "pi := 3.14159;",
        "value := 3.14e-5;",
        "result := mul 5 3;",
        "a eq b if x := 5;",
    ]
    
    for test_code in test_codes:
        print(f"\nTesting lexer with: {test_code}")
        print("-" * 50)
        try:
            tokens = lexer.tokenize(test_code)
            for token in tokens:
                print(f"Token({token.type}, {token.value}, line={token.lineno})")
        except Exception as e:
            print(f"Error: {e}")