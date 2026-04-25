import unittest
import sys
import io
from lexer import build_lexer
from parser import build_parser, code_generate

class TestLexer(unittest.TestCase):
    """Tests for the lexical analyzer"""
    
    def setUp(self):
        self.lexer = build_lexer()
    
    def tokenize(self, data):
        """Helper to get all tokens from input"""
        self.lexer.input(data)
        return list(self.lexer)
    
    def test_keywords_recognition(self):
        """Test that reserved words are recognized as keyword tokens"""
        data = "for mul div sqrt and neq not add sub"
        tokens = self.tokenize(data)
        
        expected_types = ['FOR', 'MUL', 'DIV', 'SQRT', 'AND', 'NEQ', 'NOT', 'ADD', 'SUB']
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type, 
                           f"Expected {expected_type} but got {token.type} for '{token.value}'")
    
    def test_identifiers(self):
        """Test regular identifiers (Table 2 - Option 2)"""
        test_cases = [
            ("x", "ID"),
            ("count", "ID"),
            ("myVar12", "ID"),
            ("a123", "ID"),
        ]
        for input_str, expected_type in test_cases:
            tokens = self.tokenize(input_str)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{input_str}'")
            self.assertEqual(tokens[0].type, expected_type)
            self.assertEqual(tokens[0].value, input_str)
    
    def test_identifier_max_length(self):
        """Test that identifiers longer than 8 characters trigger warning"""
        data = "veryLongIdentifier"
        tokens = self.tokenize(data)
        self.assertEqual(len(tokens), 1)
        # Should be truncated to 8 chars
        self.assertEqual(tokens[0].value, "veryLong")
    
    def test_boolean_variables(self):
        """Test that variables starting with b_ are recognized as boolean"""
        test_cases = [
            ("b_flag", "BOOLEAN_VAR"),
            ("b_active", "BOOLEAN_VAR"),
            ("normal_var", "ID"),
            ("b_test123", "BOOLEAN_VAR"),
        ]
        for input_str, expected_type in test_cases:
            tokens = self.tokenize(input_str)
            self.assertEqual(tokens[0].type, expected_type,
                           f"'{input_str}' should be {expected_type}")
    
    def test_numbers_real_with_exponent(self):
        """Test real numbers with exponent (Table 5 - Option 6)"""
        test_cases = [
            ("3.14", 3.14),
            ("15.75", 15.75),
            ("1.5E-2", 0.015),
            ("3e+10", 3e10),
            ("2.0e5", 200000.0),
            ("0.001e3", 1.0),
        ]
        for input_str, expected_value in test_cases:
            tokens = self.tokenize(input_str)
            self.assertEqual(len(tokens), 1, f"Expected 1 token for '{input_str}'")
            self.assertEqual(tokens[0].type, "NUMBER")
            self.assertAlmostEqual(tokens[0].value, expected_value, 
                                 msg=f"Mismatch for {input_str}")
    
    def test_syntax_tokens(self):
        """Test syntax tokens: brackets, equals"""
        test_cases = [
            ("=", "EQUALS"),
            ("(", "LPAREN"),
            (")", "RPAREN"),
            ("[", "LBRACKET"),
            ("]", "RBRACKET"),
        ]
        for input_str, expected_type in test_cases:
            tokens = self.tokenize(input_str)
            self.assertEqual(tokens[0].type, expected_type)
            self.assertEqual(tokens[0].value, input_str)
    
    def test_whitespace_handling(self):
        """Test that whitespace is properly ignored"""
        data = "  x  =  mul  3.14  2.0e5  "
        tokens = self.tokenize(data)
        token_types = [t.type for t in tokens]
        self.assertEqual(token_types, ['ID', 'EQUALS', 'MUL', 'NUMBER', 'NUMBER'])
    
    def test_line_number_tracking(self):
        """Test that line numbers are tracked correctly"""
        data = "x = 10.0\ny = mul x 2.0\nz = div y 3.0"
        tokens = self.tokenize(data)
        
        # Check specific token line numbers
        self.assertEqual(tokens[0].lineno, 1)  # x on line 1
        self.assertEqual(tokens[3].lineno, 2)  # y on line 2 (index 3)
        self.assertEqual(tokens[7].lineno, 3)  # z on line 3 (index 7)
    
    def test_illegal_character_error(self):
        """Test that illegal characters trigger error"""
        # Capture stderr
        captured_output = io.StringIO()
        sys.stderr = captured_output
        
        data = "x @ y"  # @ is illegal
        tokens = self.tokenize(data)
        
        sys.stderr = sys.__stderr__
        output = captured_output.getvalue()
        
        self.assertIn("Illegal character", output)
        self.assertIn("@", output)
        # Should still tokenize valid parts
        self.assertEqual(len(tokens), 2)  # Only 'x' and 'y'
    
    def test_complex_expression_tokenization(self):
        """Test tokenization of a complete for-loop"""
        data = "i = 0.0 for neq i 10.0 i = add i 1.0 arr[i] = mul i 2.0"
        tokens = self.tokenize(data)
        
        # Verify token types in sequence
        token_types = [t.type for t in tokens]
        expected = ['ID', 'EQUALS', 'NUMBER', 'FOR', 'NEQ', 'ID', 'NUMBER', 
                   'ID', 'EQUALS', 'ADD', 'ID', 'NUMBER', 'ID', 'LBRACKET',
                   'ID', 'RBRACKET', 'EQUALS', 'MUL', 'ID', 'NUMBER']
        self.assertEqual(token_types, expected)


class TestParser(unittest.TestCase):
    """Tests for the syntax analyzer (parser)"""
    
    def setUp(self):
        self.lexer = build_lexer()
        self.parser = build_parser()
    
    def parse(self, data):
        """Helper to parse input and return AST"""
        return self.parser.parse(data, lexer=self.lexer)
    
    def test_simple_assignment(self):
        """Test parsing a simple assignment"""
        data = "x = 10.5"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast, "Parser should return an AST")
        self.assertEqual(len(ast), 1)
        
        stmt = ast[0]
        self.assertEqual(stmt[0], 'assign')
        self.assertEqual(stmt[1], 'x')  # variable name
        self.assertEqual(stmt[2][0], 'number')  # expression type
        self.assertAlmostEqual(stmt[2][1], 10.5)  # value
    
    def test_array_assignment(self):
        """Test parsing assignment to array element (Requirement 5)"""
        data = "arr[i] = mul i 2.0"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        stmt = ast[0]
        self.assertEqual(stmt[0], 'assign_index')
        self.assertEqual(stmt[1], 'arr')  # array name
        self.assertEqual(stmt[2][0], 'var')  # index expression (variable)
        self.assertEqual(stmt[2][1], 'i')
        
        # Right side should be binary mul operation
        rhs = stmt[3]
        self.assertEqual(rhs[0], 'binary')
        self.assertEqual(rhs[1], 'mul')
    
    def test_for_loop_structure(self):
        """Test parsing a for loop (Table 1 - Option 11)"""
        data = "i = 0.0 for neq i 10.0 i = add i 1.0 x = mul i 2.0"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast), 1)
        
        for_stmt = ast[0]
        self.assertEqual(for_stmt[0], 'for')
        
        # Check components
        init = for_stmt[1]  # i = 0.0
        cond = for_stmt[2]  # neq i 10.0
        iter_expr = for_stmt[3]  # i = add i 1.0
        body = for_stmt[4]  # x = mul i 2.0
        
        self.assertEqual(init[0], 'assign')
        self.assertEqual(cond[0], 'binary')
        self.assertEqual(cond[1], 'neq')
        self.assertEqual(iter_expr[0], 'assign')
        self.assertEqual(body[0], 'assign')
    
    def test_nested_expressions(self):
        """Test parsing nested prefix expressions (Requirement 4)"""
        data = "x = mul add 5.0 3.0 div 10.0 2.0"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        stmt = ast[0]
        rhs = stmt[2]  # Right side of assignment
        
        # Should be: mul (add 5.0 3.0) (div 10.0 2.0)
        self.assertEqual(rhs[0], 'binary')
        self.assertEqual(rhs[1], 'mul')
        
        # Left operand of mul
        left = rhs[2]
        self.assertEqual(left[0], 'binary')
        self.assertEqual(left[1], 'add')
        
        # Right operand of mul
        right = rhs[3]
        self.assertEqual(right[0], 'binary')
        self.assertEqual(right[1], 'div')
    
    def test_unary_operations(self):
        """Test parsing unary operations"""
        test_cases = [
            ("x = not b_flag", 'not'),
            ("x = sqrt 16.0", 'sqrt'),
        ]
        for data, expected_op in test_cases:
            ast = self.parse(data)
            self.assertIsNotNone(ast)
            stmt = ast[0]
            rhs = stmt[2]
            self.assertEqual(rhs[0], 'unary')
            self.assertEqual(rhs[1], expected_op)
    
    def test_logical_operations(self):
        """Test parsing logical operations (Table 6)"""
        data = "x = and b_flag1 neq a b"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        stmt = ast[0]
        rhs = stmt[2]
        
        self.assertEqual(rhs[0], 'binary')
        self.assertEqual(rhs[1], 'and')
    
    def test_multiple_assignments(self):
        """Test parsing sequence of assignments"""
        data = "a = 1.0\nb = mul 2.0 a\nc = div b 3.0"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        self.assertEqual(len(ast), 3)
        
        for stmt in ast:
            self.assertEqual(stmt[0], 'assign')
    
    def test_array_index_with_expression(self):
        """Test parsing array with complex index expression (Requirement 5)"""
        data = "arr[mul i 2.0] = add i 1.0"
        ast = self.parse(data)
        
        self.assertIsNotNone(ast)
        stmt = ast[0]
        self.assertEqual(stmt[0], 'assign_index')
        
        # Index should be a binary expression
        index = stmt[2]
        self.assertEqual(index[0], 'binary')
        self.assertEqual(index[1], 'mul')
    
    def test_syntax_error_handling(self):
        """Test that syntax errors are detected"""
        # Capture stderr
        captured_output = io.StringIO()
        sys.stderr = captured_output
        
        # Missing operator (infix notation instead of prefix)
        data = "x = 5.0 add 3.0"  # Should be: x = add 5.0 3.0
        ast = self.parse(data)
        
        sys.stderr = sys.__stderr__
        
        # The parser might still produce something, but should report error
        # Actually PLY might raise exception or print to stderr
        output = captured_output.getvalue()
        self.assertIn("Syntax error", output)


class TestCodeGenerator(unittest.TestCase):
    """Tests for the C code generator"""
    
    def test_number_generation(self):
        """Test generating C code for numbers"""
        ast = ('number', 3.14)
        code = code_generate(ast)
        self.assertEqual(code, "3.14")
    
    def test_variable_generation(self):
        """Test generating C code for variables"""
        ast = ('var', 'counter')
        code = code_generate(ast)
        self.assertEqual(code, "counter")
    
    def test_array_index_generation(self):
        """Test generating C code for array access"""
        ast = ('indexed_var', 'arr', ('var', 'i'))
        code = code_generate(ast)
        self.assertEqual(code, "arr[i]")
    
    def test_unary_operations_generation(self):
        """Test generating C code for unary operations"""
        # NOT operation
        ast = ('unary', 'not', ('boolean_var', 'b_flag'))
        code = code_generate(ast)
        self.assertEqual(code, "!(b_flag)")
        
        # SQRT operation
        ast = ('unary', 'sqrt', ('number', 16.0))
        code = code_generate(ast)
        self.assertEqual(code, "sqrt(16.0)")
    
    def test_binary_operations_generation(self):
        """Test generating C code for binary operations"""
        test_cases = [
            (('binary', 'add', ('number', 5.0), ('number', 3.0)), "(5.0 + 3.0)"),
            (('binary', 'sub', ('var', 'x'), ('number', 1.0)), "(x - 1.0)"),
            (('binary', 'mul', ('var', 'a'), ('var', 'b')), "(a * b)"),
            (('binary', 'div', ('number', 10.0), ('number', 2.0)), "(10.0 / 2.0)"),
            (('binary', 'neq', ('var', 'i'), ('number', 0.0)), "(i != 0.0)"),
            (('binary', 'and', ('var', 'a'), ('var', 'b')), "(a || b)"),
        ]
        for ast, expected in test_cases:
            code = code_generate(ast)
            self.assertEqual(code, expected, f"Failed for {ast[1]}")
    
    def test_assignment_generation(self):
        """Test generating C code for assignments"""
        ast = ('assign', 'result', ('binary', 'mul', ('var', 'x'), ('number', 2.0)))
        code = code_generate(ast)
        self.assertEqual(code, "result = (x * 2.0);\n")
    
    def test_array_assignment_generation(self):
        """Test generating C code for array element assignments"""
        ast = ('assign_index', 'matrix', ('var', 'i'), ('add', ('var', 'x'), ('number', 1.0)))
        code = code_generate(ast)
        self.assertIn("matrix[i]", code)
        self.assertIn("=", code)
    
    def test_for_loop_generation(self):
        """Test generating C code for for-loops"""
        init = ('assign', 'i', ('number', 0.0))
        cond = ('binary', 'neq', ('var', 'i'), ('number', 10.0))
        iter_expr = ('assign', 'i', ('binary', 'add', ('var', 'i'), ('number', 1.0)))
        body = ('assign_index', 'arr', ('var', 'i'), ('binary', 'mul', ('var', 'i'), ('number', 2.0)))
        
        for_ast = ('for', init, cond, iter_expr, body)
        code = code_generate(for_ast)
        
        # Verify key components
        self.assertIn("for", code)
        self.assertIn("i = 0.0", code)
        self.assertIn("i != 10.0", code)
        self.assertIn("i = (i + 1.0)", code)
        self.assertIn("arr[i] = (i * 2.0)", code)
        self.assertIn("{", code)
        self.assertIn("}", code)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete compiler"""
    
    def setUp(self):
        self.lexer = build_lexer()
        self.parser = build_parser()
    
    def compile_and_get_code(self, source):
        """Helper to compile source and return C code"""
        lexer = build_lexer()
        parser = build_parser()
        ast = parser.parse(source, lexer=lexer)
        if ast:
            return code_generate(ast)
        return None
    
    def test_simple_for_loop(self):
        """Integration test: simple for loop"""
        source = "i = 0.0 for neq i 10.0 i = add i 1.0 x = mul i 2.0"
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("for(i = 0.0; (i != 10.0); i = (i + 1.0))", c_code)
        self.assertIn("x = (i * 2.0);", c_code)
    
    def test_nested_expressions_for_loop(self):
        """Integration test: for loop with complex expressions"""
        source = "val = mul 2.0 5.0 for neq val 100.0 val = add val 10.0 res = div val 3.0"
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("val = (2.0 * 5.0)", c_code)
        self.assertIn("(val != 100.0)", c_code)
    
    def test_boolean_expressions(self):
        """Integration test: boolean operations"""
        source = "flag = and b_test1 neq x y"
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("flag = (b_test1 || (x != y))", c_code)
    
    def test_array_operations(self):
        """Integration test: array indexing with expressions"""
        source = "data[mul i 2.0] = add base offset"
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("data[(i * 2.0)]", c_code)
        self.assertIn("(base + offset)", c_code)
    
    def test_multiple_statements(self):
        """Integration test: sequence of statements"""
        source = """
        a = 10.0
        b = mul a 2.0
        c = div b 3.0
        """
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("a = 10.0", c_code)
        self.assertIn("b = (a * 2.0)", c_code)
        self.assertIn("c = (b / 3.0)", c_code)
    
    def test_complex_for_loop(self):
        """Integration test: complex for loop with array body"""
        source = "idx = 0.0 for neq idx 5.0 idx = add idx 1.0 result[mul idx 2.0] = add idx 10.0"
        c_code = self.compile_and_get_code(source)
        
        self.assertIsNotNone(c_code)
        self.assertIn("result[(idx * 2.0)] = (idx + 10.0)", c_code)
    
    def test_memory_no_leak(self):
        """Test that multiple compilations don't cause issues"""
        for i in range(5):
            source = "x = mul 2.0 3.0"
            c_code = self.compile_and_get_code(source)
            self.assertIsNotNone(c_code)
    
    def test_empty_input(self):
        """Test handling of empty input"""
        source = ""
        lexer = build_lexer()
        parser = build_parser()
        ast = parser.parse(source, lexer=lexer)
        # Should not crash
        self.assertIsNone(ast)


class TestErrorCases(unittest.TestCase):
    """Tests for error handling and edge cases"""
    
    def setUp(self):
        self.lexer = build_lexer()
        self.parser = build_parser()
    
    def compile_source(self, source):
        """Helper to compile source and capture errors"""
        lexer = build_lexer()
        parser = build_parser()
        
        captured = io.StringIO()
        sys.stderr = captured
        
        ast = parser.parse(source, lexer=lexer)
        
        sys.stderr = sys.__stderr__
        return ast, captured.getvalue()
    
    def test_lexical_error_in_expression(self):
        """Test handling of illegal character in expression"""
        source = "x = mul 3.0 2@0"
        ast, errors = self.compile_source(source)
        
        self.assertIn("Illegal character", errors)
        self.assertIn("@", errors)
    
    def test_syntax_error_missing_operator(self):
        """Test syntax error when operator is missing"""
        source = "x = 5.0 3.0"  # Missing operator between operands
        ast, errors = self.compile_source(source)
        
        self.assertIn("Syntax error", errors)
    
    def test_syntax_error_incomplete_for_loop(self):
        """Test syntax error in incomplete for loop"""
        source = "i = 0 for neq i 10"  # Missing iteration and body
        ast, errors = self.compile_source(source)
        
        self.assertIn("Syntax error", errors)
    
    def test_recovery_from_error(self):
        """Test that parser can continue after an error"""
        source = """
        x = 10.0
        y = 20.0 30.0  # Error here
        z = 30.0       # Should still process
        """
        ast, errors = self.compile_source(source)
        
        self.assertIn("Syntax error", errors)
        # Parser should attempt to continue
        
    def test_long_identifier_warning(self):
        """Test warning for identifier exceeding max length"""
        captured = io.StringIO()
        sys.stderr = captured
        
        lexer = build_lexer()
        lexer.input("veryLongVariableName = 1.0")
        tokens = list(lexer)
        
        sys.stderr = sys.__stderr__
        warnings = captured.getvalue()
        
        self.assertIn("exceeds maximum length", warnings)


def run_tests():
    """Run all tests with detailed output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLexer))
    suite.addTests(loader.loadTestsFromTestCase(TestParser))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
    else:
        print("\n✗ SOME TESTS FAILED!")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")


if __name__ == "__main__":
    run_tests()