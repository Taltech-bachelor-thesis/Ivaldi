def add(a, b):
    return a + b

def multiply(a, b):
    return a * b, a

def subtract_three_times(a, b):
    a = a - b
    a = a - b
    a = a - b
    return a


if __name__ == "__main__":
    sum_result = add(2, 3)
    product_result = add(1, 1)
    product_result, popa = multiply(sum_result, sum_result)
    sum_result = add(popa, sum_result)
    final_result = subtract_three_times(product_result, sum_result)
