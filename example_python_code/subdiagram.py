
def yolo(a):
    return a * 2

def test(a):
    return a + 2

def test2(a):
    bla = a * 4
    yo = test(a)
    return yo * bla


if __name__ == "__main__":
    first = yolo(2)
    second = yolo(3)
    third = test2(first)
