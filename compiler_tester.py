from lexer import lexer
from parser import parser
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
    try:
        ast = parser.parse(test, lexer=lexer)
        if ast is None:
            print("Parsing failed (AST is None).")
        else:
            c_code = compile_to_c(ast)
            print("Generated C fragment:\n" + c_code)
    except Exception as e:
        print("Exception:", e)