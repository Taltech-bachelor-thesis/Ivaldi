import random
import re
import string


class StringUtil:

    @staticmethod
    def generate_random_string(length):
        """Generate a random string of the specified length."""
        # Define the possible characters for the random string
        characters = string.ascii_letters + string.digits + string.punctuation
        # Generate a random string using the specified characters
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    @staticmethod
    def generate_random_valid_string(length):
        """Generate a random string of the specified length using valid identifier characters."""
        # Only use letters, digits, and underscores
        characters = string.ascii_letters + string.digits + "_"
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    @staticmethod
    def generate_new_variable_name_from(variable_name: str) -> str:
        """Generate a new variable name by appending a random suffix."""
        suffix = StringUtil.generate_random_valid_string(10)
        # Ensure the variable name is also valid
        if not variable_name.isidentifier():
            variable_name = '_' + ''.join(c if c.isalnum() or c == '_' else '_' for c in variable_name)
        return f"{variable_name}_{suffix}"

    @staticmethod
    def generate_new_variable_name() -> str:
        """Generate a new variable name by appending a random suffix."""
        suffix = StringUtil.generate_random_valid_string(10)
        return f"var_{suffix}"

    @staticmethod
    def replace_nth_occurrence(text, old, new, n):
        matches = list(re.finditer(re.escape(old), text))
        if len(matches) < n:
            return text  # Not enough occurrences

        # Get the start and end of the nth match
        start, end = matches[n - 1].span()
        return text[:start] + new + text[end:]
