def reverse_string(s: str) -> str:
    return s[::-1]

def duplicate_string(s: str) -> str:
    return (s + " ") * 2

def prepend_hello(s: str) -> str:
    prefix = "Hello, "
    return prefix + s

def string_length_times_five(s: str) -> int:
    return len(s) * 5

def uppercase_middle(s: str) -> str:
    half = len(s) // 2
    return s[:half] + s[half:].upper()
