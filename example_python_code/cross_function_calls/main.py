from example_python_code.cross_function_calls.utils import reverse_string, prepend_hello, duplicate_string, \
    uppercase_middle, string_length_times_five


def shout_reversed_greeting(name: str) -> str:
    # Uses reverse_string and prepend_hello
    reversed_name = reverse_string(name)
    greeting = prepend_hello(reversed_name)
    return greeting.upper()

def transform_and_measure(s: str) -> tuple:
    # Uses duplicate_string, string_length_times_five, and uppercase_middle
    duplicated = duplicate_string(s)
    transformed = uppercase_middle(duplicated)
    size_metric = string_length_times_five(transformed)
    return transformed, size_metric

if __name__ == "__main__":
    name = "Alice"
    greeting = shout_reversed_greeting(name)
    reversed_greeting = reverse_string(greeting)
    transformed_string, size_metric = transform_and_measure(greeting)
    print(f"Greeting: {greeting}")
