def calculate(a, b, operator):
    if operator == '+':
        return a+b
    elif operator == '-':
        return a-b
    elif operator == '*':
        return a*b
    elif operator == '/':
        if b == 0:
            return "错误，除数不能为0"
        return a/b
    else:
        return "错误，不支持相关运算符"

if __name__ == '__main__':
    result = calculate(125, 36, "*")
    print(result)