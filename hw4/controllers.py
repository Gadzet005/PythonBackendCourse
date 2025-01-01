def operation(a: int | None, b: int | None) -> int | None:
    if (a == None) or (b == None):
        return None
    return a + b
