from math_utils import add, multiply, divide, square
from string_utils import reverse_string, to_uppercase, is_palindrome


def not_used():
    print("This function is not used.")


def return_argument(arg):
    return arg


if __name__ == "__main__":
    sum_result = add(12, 8)
    product_result = multiply(sum_result, 14)
    quotient_result = divide(sum_result, product_result)
    squared_result = square(product_result)

    reversed_str = reverse_string("level")
    uppercase_str = to_uppercase("popich")
    palindrome_check = is_palindrome(reversed_str)

    result = return_argument(sum_result)

    print("Sum:", sum_result)
    print("Product:", product_result)
    print("Quotient:", quotient_result)
    print("Square:", squared_result)

    print("Reversed String:", reversed_str)
    print("Uppercase String:", uppercase_str)
    print("Is Palindrome:", palindrome_check)
