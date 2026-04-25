import ply.yacc as yacc
from lexer import tokens

# --- Precedence and Associativity ---
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

def p_statement_list_1(p):
    '''statement_list : statement'''
    p[0] = [p[1]]

def p_statement_list_2(p):
    '''statement_list : statement_list statement'''
    p[0] = p[1] + [p[2]]

def p_statement(p):
    '''statement : for_statement
                 | assign_statement'''
    p[0] = p[1]

def p_for_statement(p):
    '''for_statement : assign_statement FOR expression assign_statement assign_statement'''
    init = p[1]
    cond = p[3]
    iter_expr = p[4]
    body = p[5]
    p[0] = ('for', init, cond, iter_expr, body)

def p_assign_statement_simple(p):
    '''assign_statement : ID EQUALS expression'''
    p[0] = ('assign', p[1], p[3])

def p_assign_statement_indexed(p):
    '''assign_statement : ID LBRACKET expression RBRACKET EQUALS expression'''
    p[0] = ('assign_index', p[1], p[3], p[6])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = ('number', p[1])

def p_expression_var(p):
    '''expression : ID'''
    p[0] = ('var', p[1])

def p_expression_bool(p):
    '''expression : BOOLEAN_VAR'''
    p[0] = ('boolean_var', p[1])

def p_expression_indexed(p):
    '''expression : ID LBRACKET expression RBRACKET'''
    p[0] = ('indexed_var', p[1], p[3])

def p_expression_unary(p):
    '''expression : unary_op expression'''
    p[0] = ('unary', p[1], p[2])

def p_expression_binary(p):
    '''expression : binary_op expression expression'''
    p[0] = ('binary', p[1], p[2], p[3])

# --- Operator Rules ---
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
        print(f"Syntax error at line {p.lineno}, token '{p.type}' with value '{p.value}'. Unexpected token.", 
              file=sys.stderr)
    else:
        print("Syntax error at EOF. Unexpected end of file.", file=sys.stderr)

# Build the parser
def build_parser():
    return yacc.yacc()

# --- Code Generation (Translating AST to C) ---
import sys

def code_generate(t):
    """Recursively generates C code string from the AST tuple."""
    if isinstance(t, list):
        return ''.join([code_generate(stmt) for stmt in t])
    elif t is None:
        return ""
    elif t[0] == 'number':
        return str(t[1])
    elif t[0] == 'var':
        return str(t[1])
    elif t[0] == 'boolean_var':
        return str(t[1])
    elif t[0] == 'indexed_var':
        return f"{t[1]}[{code_generate(t[2])}]"
    elif t[0] == 'unary':
        op_map = {'not': '!', 'sqrt': 'sqrt'}
        op = op_map.get(t[1], t[1])
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
        return f"({code_generate(t[2])} {op} {code_generate(t[3])})"
    elif t[0] == 'assign':
        return f"{t[1]} = {code_generate(t[2])};\n"
    elif t[0] == 'assign_index':
        return f"{t[1]}[{code_generate(t[2])}] = {code_generate(t[3])};\n"
    elif t[0] == 'for':
        init = code_generate(t[1]).rstrip('\n;') + ';'
        cond = code_generate(t[2])
        iter_expr = code_generate(t[3]).rstrip('\n;')
        body = code_generate(t[4])
        return f"\nfor({init} {cond}; {iter_expr}) {{\n    {body}}}\n"
    else:
        return f"/* Unknown AST: {t} */"