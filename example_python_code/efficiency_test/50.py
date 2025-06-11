def mix4_fn0(x, y):
    return (x + 1) * (y + 1)

def mix2_fn1(x, y):
    return (x * 2 + y) / 3

def add_fn2(x, y):
    return x + y

def pow_fn3(x, y):
    return x ** y

def div_fn4(x, y):
    return x / y

def mix1_fn5(x, y):
    return (x + y) * 0.5

def add_fn6(x, y):
    return x + y

def mix2_fn7(x, y):
    return (x * 2 + y) / 3

def mix4_fn8(x, y):
    return (x + 1) * (y + 1)

def mix2_fn9(x, y):
    return (x * 2 + y) / 3

def mul_fn10(x, y):
    return x * y

def mix4_fn11(x, y):
    return (x + 1) * (y + 1)


if __name__ == '__main__':
    v0 = 1.0
    v1 = 2.0
    v2 = mix4_fn0(v0, v0)
    v3 = mix2_fn1(v0, v2)
    v4 = add_fn2(v2, v1)
    v5 = pow_fn3(v3, v3)
    v6 = div_fn4(v1, v4)
    v7 = mix1_fn5(v6, v0)
    v8 = add_fn6(v1, v1)
    v9 = mix2_fn7(v0, v0)
    v10 = mix4_fn8(v4, v2)
    v11 = mix2_fn9(v9, v3)
    v12 = mul_fn10(v7, v5)
    v13 = mix4_fn11(v7, v11)
