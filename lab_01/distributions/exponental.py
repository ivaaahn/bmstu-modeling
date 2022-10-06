import math


def exp_cdf(x: float, lambda_: float) -> float:
    if x < 0.0:
        result = 0.0
    else:
        result = 1 - math.exp(-lambda_ * x)

    return result


def exp_pdf(x: float, lambda_: float) -> float:
    if x < 0:
        result = 0.0
    else:
        result = lambda_ * math.exp(-lambda_ * x)

    return result
