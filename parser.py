import ply.yacc as yacc
from lexer import tokens

# Список для сбора синтаксических ошибок
parse_errors = []

def p_program(p):
    '''program : for_list'''
    p[0] = p[1]

def p_for_list(p):
    '''for_list : for_stmt
                | for_stmt for_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_for_stmt(p):
    '''for_stmt : expression FOR expression expression assign_stmt'''
    p[0] = ('for', p[1], p[3], p[4], p[5])

def p_assign_stmt(p):
    '''assign_stmt : ASSIGN array_ref expression'''
    p[0] = ('assign', p[2][1], p[2][2], p[3])

def p_array_ref(p):
    '''array_ref : ID LBRACKET expression RBRACKET'''
    p[0] = ('array', p[1], p[3])

def p_expression_assign_var(p):
    '''expression : ASSIGN ID expression'''
    p[0] = ('assign_var', p[2], p[3])

def p_expression_binary(p):
    '''expression : ADD expression expression
                  | SUB expression expression
                  | MUL expression expression
                  | DIV expression expression
                  | AND expression expression
                  | OR expression expression
                  | EQ expression expression
                  | NE expression expression
                  | LT expression expression
                  | GT expression expression
                  | LE expression expression
                  | GE expression expression'''
    p[0] = (p[1], p[2], p[3])

def p_expression_unary(p):
    '''expression : NOT expression
                  | SQRT expression'''
    p[0] = (p[1], p[2])

def p_expression_operand(p):
    '''expression : ID
                  | INTEGER_CONST
                  | REAL_CONST
                  | TRUE
                  | FALSE
                  | array_ref'''
    p[0] = p[1]

def p_error(p):
    if p:
        error_msg = f"\033[31mSyntax error at token '{p.value}' (line {p.lineno})\033[0m"
        parse_errors.append(error_msg)
        print(error_msg)
    else:
        error_msg = "\033[31mSyntax error at end of input\033[0m"
        parse_errors.append(error_msg)
        print(error_msg)

# Функция для сброса ошибок
def reset_errors():
    parse_errors.clear()

parser = yacc.yacc()