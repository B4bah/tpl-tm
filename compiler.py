def compile_to_c(ast):
    code = []
    for stmt in ast:
        code.append(translate_stmt(stmt))
    return '\n'.join(code)

def translate_stmt(node):
    if node[0] == 'for':
        init = translate_expr(node[1])
        cond = translate_expr(node[2])
        iter = translate_expr(node[3])
        body = translate_assign(node[4])
        return f"for ({init}; {cond}; {iter}) {{\n    {body}\n}}"
    else:
        raise ValueError("Unknown statement")

def translate_assign(node):
    # node: ('assign', var, idx_expr, val_expr)
    var = node[1]
    idx = translate_expr(node[2])
    val = translate_expr(node[3])
    return f"{var}[{idx}] = {val};"

def translate_expr(expr):
    if isinstance(expr, tuple):
        if expr[0] == 'array':
            return f"{expr[1]}[{translate_expr(expr[2])}]"
        elif expr[0] == 'assign_var':
            return f"{expr[1]} = {translate_expr(expr[2])}"
        else:
            op = expr[0]
            if op in ('add','sub','mul','div','and','or','eq','ne','lt','gt','le','ge'):
                left = translate_expr(expr[1])
                right = translate_expr(expr[2])
                c_op = {
                    'add':'+','sub':'-','mul':'*','div':'/',
                    'and':'&&','or':'||',
                    'eq':'==','ne':'!=','lt':'<','gt':'>','le':'<=','ge':'>='
                }[op]
                return f"({left} {c_op} {right})"
            elif op == 'not':
                return f"!({translate_expr(expr[1])})"
            elif op == 'sqrt':
                return f"sqrt({translate_expr(expr[1])})"
            else:
                raise ValueError(f"Unknown operator {op}")
    elif isinstance(expr, bool):
        return '1' if expr else '0'
    else:
        return str(expr)