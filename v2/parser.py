# parser.py
import ply.yacc as yacc
from lexer import Lexer, tokens

class Parser:
    def __init__(self):
        self.lexer = Lexer()
        # Pass tokens explicitly to yacc
        self.tokens = tokens
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False, tabmodule='parsetab')
    
    # ------------------------------------------------------------------
    # GRAMMAR RULES
    # ------------------------------------------------------------------
    
    def p_program(self, p):
        '''program : statement_list'''
        p[0] = p[1]
    
    def p_statement_list(self, p):
        '''statement_list : statement SEMICOLON statement_list
                          | statement SEMICOLON'''
        if len(p) == 4:
            p[0] = p[1] + '\n' + p[3]
        else:
            p[0] = p[1]
    
    def p_statement(self, p):
        '''statement : assignment_statement
                     | conditional_statement'''
        p[0] = p[1]
    
    def p_assignment_statement(self, p):
        '''assignment_statement : IDENTIFIER ASSIGN expression'''
        p[0] = f"{p[1]} = {p[3]};"
    
    def p_conditional_statement(self, p):
        '''conditional_statement : statement IF condition'''
        p[0] = f"if ({p[3]}) {{\n    {p[1]}\n}}"
    
    def p_condition(self, p):
        '''condition : logical_expression'''
        p[0] = p[1]
    
    def p_logical_expression(self, p):
        '''logical_expression : logical_term OR logical_expression
                              | logical_term'''
        if len(p) == 4:
            p[0] = f"({p[1]} || {p[3]})"
        else:
            p[0] = p[1]
    
    def p_logical_term(self, p):
        '''logical_term : logical_factor
                        | logical_factor AND logical_term
                        | logical_factor logical_term'''
        if len(p) == 4 and p[2] == 'and':
            p[0] = f"({p[1]} && {p[3]})"
        elif len(p) == 2:
            p[0] = p[1]
        else:
            # For sequences in prefix form, take the first
            p[0] = p[1]
    
    def p_logical_factor(self, p):
        '''logical_factor : NOT logical_factor
                          | comparison'''
        if len(p) == 3:
            p[0] = f"!({p[2]})"
        else:
            p[0] = p[1]
    
    def p_comparison(self, p):
        '''comparison : arithmetic_expression EQ arithmetic_expression
                      | arithmetic_expression NEQ arithmetic_expression'''
        if p[2] == 'eq':
            p[0] = f"({p[1]} == {p[3]})"
        else:  # neq
            p[0] = f"({p[1]} != {p[3]})"
    
    def p_arithmetic_expression(self, p):
        '''arithmetic_expression : term
                                 | term ADD arithmetic_expression
                                 | term SUB arithmetic_expression'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[2] == 'add':
                p[0] = f"({p[1]} + {p[3]})"
            else:  # sub
                p[0] = f"({p[1]} - {p[3]})"
    
    def p_term(self, p):
        '''term : factor
                | factor MUL term
                | factor DIV term'''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 4:
            if p[2] == 'mul':
                p[0] = f"({p[1]} * {p[3]})"
            else:  # div
                p[0] = f"({p[1]} / {p[3]})"
    
    def p_factor(self, p):
        '''factor : SQRT factor
                  | ADD factor
                  | SUB factor
                  | IDENTIFIER
                  | INTEGER_CONST
                  | REAL_CONST
                  | LPAREN expression RPAREN'''
        if len(p) == 3:  # unary operators
            if p[1] == 'sqrt':
                p[0] = f"sqrt({p[2]})"
            elif p[1] == 'add':
                p[0] = f"(+{p[2]})"
            elif p[1] == 'sub':
                p[0] = f"(-{p[2]})"
        elif len(p) == 2:  # leaf nodes
            if isinstance(p[1], (int, float)):
                p[0] = str(p[1])
            else:
                p[0] = p[1]
        else:  # LPAREN expression RPAREN
            p[0] = f"({p[2]})"
    
    def p_expression(self, p):
        '''expression : arithmetic_expression
                      | logical_expression'''
        p[0] = p[1]
    
    # Error rule for syntax errors
    def p_error(self, p):
        if p:
            error_msg = f"Syntax error at '{p.value}' at line {p.lineno}"
            raise Exception(error_msg)
        else:
            error_msg = "Syntax error at EOF"
            raise Exception(error_msg)
    
    def parse(self, source_code):
        """Parse source code and return C code fragment"""
        try:
            # Reset lexer error
            self.lexer.lexer.lexer_error = None
            # Parse the source code
            result = self.parser.parse(source_code, lexer=self.lexer.lexer)
            if self.lexer.lexer.lexer_error:
                raise Exception(self.lexer.lexer.lexer_error)
            return result
        except Exception as e:
            raise Exception(f"Parsing error: {str(e)}")
    
    def reset(self):
        """Reset the parser state"""
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False, tabmodule='parsetab')


if __name__ == "__main__":
    # Test the parser
    parser = Parser()
    test_codes = [
        "x := 42;",
        "pi := 3.14159;",
        "result := mul 5 3;",
        "a eq b if x := 5;",
    ]
    
    for test_code in test_codes:
        print(f"\nTesting parser with: {test_code}")
        print("-" * 50)
        try:
            result = parser.parse(test_code)
            print(f"Parsed result:\n{result}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            parser.reset()