import ply.lex as lex

# --- Token List ---
tokens = (
    'FOR',
    'ID',
    'NUMBER',
    'BOOLEAN_VAR',
    # Operators (Keywords)
    'MUL', 'DIV', 'SQRT',
    'AND', 'NEQ', 'NOT',
    'ADD', 'SUB',
    # Syntax
    'EQUALS',
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
)

# --- Reserved Words (Keywords mapped to tokens) ---
reserved = {
    'for': 'FOR',
    'mul': 'MUL',
    'div': 'DIV',
    'sqrt': 'SQRT',
    'and': 'AND',
    'neq': 'NEQ',
    'not': 'NOT',
    'add': 'ADD',
    'sub': 'SUB',
}

# --- Simple Tokens (Non-Keyword Syntax) ---
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

# --- Complex Token Rules ---
def t_NUMBER(t):
    r'\d+\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+|\.\d+([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Check if it's a reserved word FIRST
    token_type = reserved.get(t.value, 'ID')
    
    # For regular identifiers (not keywords), apply length check
    if token_type == 'ID' and len(t.value) > 8:
        print(f"Lexical error at line {t.lexer.lineno}: Identifier '{t.value}' exceeds maximum length of 8.")
        t.value = t.value[:8]  # Truncate to first 8 characters
    
    # After truncation (or not), check if what remains is a reserved word
    if token_type == 'ID':
        # Check if truncated value is reserved
        if t.value in reserved:
            token_type = reserved[t.value]
        # Check if it's a boolean variable (starts with b_)
        elif t.value.startswith('b_'):
            token_type = 'BOOLEAN_VAR'
    
    t.type = token_type
    return t

# --- Handling Comments ---
def t_COMMENT(t):
    r'\#.*'
    pass  # Ignore comments (no return value discards token)

# --- Tracking Line Numbers ---
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Ignored Characters (Whitespace) ---
t_ignore = ' \t'

# --- Error Handling ---
def t_error(t):
    print(f"Lexical error at line {t.lexer.lineno}: Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
def build_lexer():
    return lex.lex()