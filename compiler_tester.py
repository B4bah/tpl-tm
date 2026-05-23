from lexer import lexer, lex_errors, reset_errors as reset_lex_errors
from parser import parser, parse_errors, reset_errors as reset_parse_errors
from compiler import compile_to_c

tests = [
    # 1 – корректный простой цикл
    "i = 0 for lt i 10 i = add i 1 a[i] = mul i 2",
    # 2 – цикл с убывающим счётчиком и выражением в индексе
    "n = 5 for ne n 0 n = sub n 1 arr[ sub n 1 ] = div 10 n",
    # 3 – вещественные константы, sqrt, логические константы
    "x = 1.5e2 for and gt x 100 lt x 200 x = add x 0.5 data[ sqrt x ] = not false",
    # 4 – вложенное префиксное выражение
    "k = 0 for lt mul k 3 30 k = add k 1 b[k] = add mul 2 k div k 2",
    # 5 – ошибка: слишком длинный идентификатор
    "longident = 1 for lt i 5 i = add i 1 arr[i] = 0",
    # 6 – ошибка: пропущена операция сравнения (инфиксный +)
    "i = 0 for i 10 i = i + 1 a[i] = 0",
    # 7 – ошибка: отсутствует выражение итерации
    "i = 0 for lt i 10 a[i] = i",
    # 8 – ошибка: незавершённое присваивание
    "i = 0 for lt i 10 i = add i 1 arr[i] =",
]

for i, test in enumerate(tests, 1):
    print(f"\n=== Test {i} ===")
    print("Input:", test)
    
    # Сбрасываем ошибки перед каждым тестом
    reset_lex_errors()
    reset_parse_errors()
    
    try:
        ast = parser.parse(test, lexer=lexer)
        
        # Проверяем, были ли ошибки
        has_errors = len(lex_errors) > 0 or len(parse_errors) > 0
        
        if ast is None or has_errors:
            if ast is None and not has_errors:
                print("\033[31mParsing failed (AST is None).\033[0m")
            if has_errors:
                print(f"\033[31mTest FAILED with {len(lex_errors)} lexer error(s) and {len(parse_errors)} parser error(s).\033[0m")
        else:
            c_code = compile_to_c(ast)
            print("Generated C fragment:")
            print(f"\033[33m{c_code}\033[0m")
            print("\033[32mTest passed.\033[0m")
            
    except Exception as e:
        print(f"\033[31mException: {e}\033[0m")
        print("\033[31mTest FAILED with exception.\033[0m")