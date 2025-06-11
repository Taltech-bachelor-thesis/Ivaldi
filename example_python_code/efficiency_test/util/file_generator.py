import random

function_templates = [
    "def add_fn{id}(x, y):\n    return x + y\n",
    "def sub_fn{id}(x, y):\n    return x - y\n",
    "def mul_fn{id}(x, y):\n    return x * y\n",
    "def div_fn{id}(x, y):\n    return x / y\n",
    "def pow_fn{id}(x, y):\n    return x ** y\n",
    "def mod_fn{id}(x, y):\n    return x % y\n",
    "def mix1_fn{id}(x, y):\n    return (x + y) * 0.5\n",
    "def mix2_fn{id}(x, y):\n    return (x * 2 + y) / 3\n",
    "def mix3_fn{id}(x, y):\n    return x * x + y * y\n",
    "def mix4_fn{id}(x, y):\n    return (x + 1) * (y + 1)\n"
]

target_lines = 5000
function_lines = 3
init_lines = 2
main_call_line = 1
function_count = (target_lines - init_lines) // (function_lines + main_call_line)

functions = []
for i in range(function_count):
    tmpl = random.choice(function_templates)
    functions.append(tmpl.format(id=i) + "\n")

main_block = ["if __name__ == '__main__':\n", "    v0 = 1.0\n    v1 = 2.0\n"]
current_var = 2

for i in range(function_count):
    arg1 = random.randint(0, current_var - 1)
    arg2 = random.randint(0, current_var - 1)
    func_name = functions[i].split('(')[0].split()[1]
    main_block.append(f"    v{current_var} = {func_name}(v{arg1}, v{arg2})\n")
    current_var += 1

full_code = "".join(functions) + "\n" + "".join(main_block)

file_name = f"../{target_lines}.py"
with open(file_name, "w") as f:
    f.write(full_code)
