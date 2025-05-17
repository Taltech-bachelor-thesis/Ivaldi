def add(a, b):
    return a + b

def multiply_and_return_first(a, b):
    return a * b, a

def subtract(a, b):
    return a - b


if __name__ == "__main__":
    sum_result = add(2, 3)
    product_result, unused = multiply_and_return_first(
        sum_result, sum_result)
    final_result = subtract(product_result, sum_result)
