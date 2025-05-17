def add(a, b):
    return a + b

def multiply(a, b):
    return a * b, a

def subtract(a, b):
    return a - b


if __name__ == "__main__":
    sum_result = add(add(2, 3), 3) + multiply(4, 2)[0]
    product_result, popa = multiply(sum_result, sum_result)
    final_result = subtract(product_result, sum_result)
