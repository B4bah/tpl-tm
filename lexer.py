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
    'ADD', 'SUB', # Although not in your original set, ADD is used in the loop iteration example. We'll include common ones.
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
    r'\d+\.\d+([eE][+-]?\d+)?|\d+[eE][+-]?\d+' # Matches 15.75, 1.5E-2, 3e+10
    t.value = float(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID') # Check for reserved words
    # Enforce max length of 8 for non-reserved identifiers (Table 2, Option 2)
    if t.type == 'ID' and len(t.value) > 8:
        print(f"Lexical error at line {t.lineno}: Identifier '{t.value}' exceeds maximum length of 8.")
        t.lexer.skip(1) # Skip the problematic identifier? Or just report. We'll just report and keep the ID.
        t.value = t.value[:8] # Truncate it for compilation, but this is a design choice.
    # Placeholder for boolean variables. In a real compiler, you'd have a symbol table.
    # Here, we simply assume variables starting with 'b_' are boolean.
    # This is a huge simplification for the assignment.
    if t.type == 'ID' and t.value.startswith('b_'):
        t.type = 'BOOLEAN_VAR'
    return t

# --- Tracking Line Numbers ---
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Ignored Characters (Whitespace and possible tabs) ---
t_ignore = ' \t'

# --- Error Handling ---
def t_error(t):
    print(f"Lexical error at line {t.lineno}: Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
def build_lexer():
    return lex.lex()