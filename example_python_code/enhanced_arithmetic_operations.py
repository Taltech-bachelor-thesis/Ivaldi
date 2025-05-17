def add(a, b):
    return a + b

def multiply(a, b):
    return a * b, a

def subtract(a, b):
    print("Subtracting", a, b)
    return a - b

def divide(a, b):
    return a / b

def modulus(a, b):
    return a % b

def power_with_secret(a, b):
    if a > 10:
        return a
    return a ** b

def floor_divide(a, b):
    return a // b

if __name__ == "__main__":
    sum_result = add(10, 5)
    # this is a comment

    product_result, _ = multiply(sum_result, 3)
    print(product_result)

    diff_result = subtract(product_result, sum_result)
    # this is another comment

    division_result = divide(product_result, 1)

    modulus_result = modulus(sum_result, diff_result)

    power_result = power_with_secret(product_result, modulus_result)

    floor_division_result = floor_divide(power_result, division_result)
