import ply.lex as lex

reserved = {
    'for': 'FOR',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'eq': 'EQ',
    'ne': 'NE',
    'lt': 'LT',
    'gt': 'GT',
    'le': 'LE',
    'ge': 'GE',
    'add': 'ADD',
    'sub': 'SUB',
    'mul': 'MUL',
    'div': 'DIV',
    'sqrt': 'SQRT',
    'true': 'TRUE',
    'false': 'FALSE',
}

tokens = ['ID', 'INTEGER_CONST', 'REAL_CONST',
          'ASSIGN', 'LBRACKET', 'RBRACKET'] + list(reserved.values())

t_ASSIGN = r'='
t_LBRACKET = r'\['
t_RBRACKET = r'\]'

t_ignore = ' \t'

MAX_ID_LEN = 8

def t_REAL_CONST(t):
    r'((\d+\.\d*([eE][+-]?\d+)?)|(\d+[eE][+-]?\d+)|(\.\d+([eE][+-]?\d+)?))'
    t.value = float(t.value)
    return t

def t_INTEGER_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    if t.type == 'ID' and len(t.value) > MAX_ID_LEN:
        print(f"Lexer error: identifier '{t.value}' too long (max {MAX_ID_LEN} chars)")
        return None
    if t.type == 'TRUE':
        t.value = True
    elif t.type == 'FALSE':
        t.value = False
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Lexer error: illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()