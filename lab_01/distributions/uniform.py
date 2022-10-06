def uniform_cdf(x: float, a: float, b: float) -> float:
    if x >= b:
        result = 1.0
    elif x < a:
        result = 0.0
    else:
        result = (x - a) / (b - a)

    return result


def uniform_pdf(x: float, a: float, b: float) -> float:
    if a <= x <= b:
        result = 1 / (b - a)
    else:
        result = 0

    return result
