import math
from math import factorial
from . import enhanced_arithmetic_operations

def add_factorials(a, b):
    return factorial(a) + math.factorial(b)

def multiply(a, b):
    return a * b, a

def subtract(a, b):
    import diagram
    return a - b

import json

def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

if __name__ == "__main__":
    sum_result = add_factorials(2, 3)
    product_result, popa = multiply(sum_result, sum_result)
    final_result = subtract(product_result, sum_result)
    yolo = read_json_file("example_python_code/test.json")
