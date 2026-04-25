import ply.yacc as yacc
from lexer import tokens # Import the token list

# --- Abstract Syntax Tree (Simple tuple representation) ---
# We'll just print C code directly. This is simpler for a "fragment of C code" output.

# --- Precedence and Associativity (Not strictly necessary for pure prefix, but good practice) ---
# Lower precedence value = higher priority? PLY docs: precedence is from top to bottom (top = lowest).
precedence = (
    ('left', 'AND', 'NEQ'),
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV'),
    ('right', 'NOT', 'SQRT'),
)

# --- Grammar Rules ---

def p_program(p):
    '''program : statement_list'''
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement
                      | statement_list statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : for_statement
                 | assign_statement'''
    p[0] = p[1]

def p_for_statement(p):
    '''for_statement : assign_statement FOR expression assign_statement assign_statement'''
    init = p[1]
    cond = p[3]
    iter = p[4]
    body = p[5]
    p[0] = ('for', init, cond, iter, body)

def p_assign_statement(p):
    '''assign_statement : ID EQUALS expression
                        | ID LBRACKET expression RBRACKET EQUALS expression'''
    if len(p) == 4:
        # Simple variable assignment: ID = expr
        p[0] = ('assign', p[1], p[3])
    else:
        # Indexed variable assignment: ID[expr1] = expr2
        p[0] = ('assign_index', p[1], p[3], p[6])

def p_expression(p):
    '''expression : NUMBER
                  | ID
                  | BOOLEAN_VAR
                  | ID LBRACKET expression RBRACKET
                  | unary_op expression
                  | binary_op expression expression'''
    if len(p) == 2:
        # Single operand
        if isinstance(p[1], float):
            p[0] = ('number', p[1])
        elif str(p[1]).startswith('b_'): # Polymorphic ID handling (should be fine)
            p[0] = ('boolean_var', p[1])
        else:
            p[0] = ('var', p[1])
    elif len(p) == 3:
        # Unary operation
        p[0] = ('unary', p[1], p[2])
    elif len(p) == 4:
        # Binary operation
        p[0] = ('binary', p[1], p[2], p[3])
    elif len(p) == 5:
        # Indexed variable reference: ID[expr]
        p[0] = ('indexed_var', p[1], p[3])

# --- Operator Rules (Mapping grammar names to internal representation) ---
# unary_op and binary_op are non-terminals that just pass the operator type up.
def p_unary_op(p):
    '''unary_op : NOT
                | SQRT'''
    p[0] = p[1]

def p_binary_op(p):
    '''binary_op : NEQ
                 | AND
                 | MUL
                 | DIV
                 | ADD
                 | SUB'''
    p[0] = p[1]

# --- Error Handling Rule ---
def p_error(p):
    if p:
        print(f"Syntax error at line {p.lineno}, token '{p.type}' with value '{p.value}'. Unexpected token.")
        # Attempt recovery by skipping the erroneous token (basic approach)
        # parser.errok() # If you want to attempt to continue, but might get messy.
    else:
        print("Syntax error at EOF. Unexpected end of file.")

# Build the parser
def build_parser():
    return yacc.yacc()

# --- Code Generation (Translating AST to C) ---
def code_generate(t):
    """Recursively generates C code string from the AST tuple."""
    if t[0] == 'number':
        return str(t[1])
    elif t[0] == 'var':
        return str(t[1])
    elif t[0] == 'boolean_var':
        # C doesn't have a native boolean type in C89, but we can use int.
        return str(t[1])
    elif t[0] == 'indexed_var':
        return f"{t[1]}[{code_generate(t[2])}]"
    elif t[0] == 'unary':
        op_map = {'not': '!', 'sqrt': 'sqrt'}
        op = op_map.get(t[1], t[1]) # Use C equivalent
        # Special handling for NOT: prefix ! in C
        if op == '!':
            return f"!({code_generate(t[2])})"
        else:
            return f"{op}({code_generate(t[2])})"
    elif t[0] == 'binary':
        op_map = {
            'neq': '!=', 'and': '||', 'mul': '*', 'div': '/',
            'add': '+', 'sub': '-'
        }
        op = op_map.get(t[1], t[1])
        # C allows infix. We must convert from prefix AST.
        return f"({code_generate(t[2])} {op} {code_generate(t[3])})"
    elif t[0] == 'assign':
        return f"{t[1]} = {code_generate(t[2])};\n"
    elif t[0] == 'assign_index':
        return f"{t[1]}[{code_generate(t[2])}] = {code_generate(t[3])};\n"
    elif t[0] == 'for':
        init = code_generate(t[1]).rstrip('\n;') + '; ' # Remove trailing ; and newline
        cond = code_generate(t[2])
        iter = code_generate(t[3]).rstrip('\n;') # Remove trailing ; and newline
        body = code_generate(t[4])
        return f"\nfor({init} {cond}; {iter}) {{\n    {body}}}\n"
    elif isinstance(t, list):
        return ''.join([code_generate(stmt) for stmt in t])
    else:
        return f"/* Unknown AST: {t} */"