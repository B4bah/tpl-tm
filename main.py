import sys
from lexer import build_lexer
from parser import build_parser, code_generate

def main():
    # Build the lexer and parser
    lexer = build_lexer()
    parser = build_parser()

    # Example input based on your variant (Table 1, Option 11)
    # Loop from i=0 to i < 10
    data = """
    i = 0.0 for neq i 10.0 i = add i 1.0 arr[ i ] = mul i 2.0
    """
    
    # Test with some errors to show localisation
    # data_err = "i = 0 for neq i 10 i = add i 1 x = i + 2" # Infix error

    print("Input Source Code:\n", data)
    print("\n--- Tokenizing (Lexer) ---")
    lexer.input(data)
    for tok in lexer:
        print(tok)

    print("\n--- Parsing & Code Generation (Parser) ---")
    # Reset lexer for parser
    lexer = build_lexer()
    parser = build_parser()
    try:
        ast = parser.parse(data, lexer=lexer)
        if ast:
            c_code = code_generate(ast)
            print("\nGenerated C Code Fragment:\n")
            print(c_code)
        else:
            print("Parsing failed due to syntax errors.")
    except Exception as e:
        print(f"An error occurred during parsing: {e}")

if __name__ == "__main__":
    main()