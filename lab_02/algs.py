from numpy import linalg

TIME_DELTA = 1e-3
EPS = 1e-5


def _create_coef_matrix(matrix: list[list[float]]) -> list[list[float]]:
    count = len(matrix)

    res = [[0.0 for _ in range(count)] for _ in range(count)]

    for i in range(count):
        for j in range(count):
            value = -sum(matrix[i]) + matrix[i][i] if i == j else matrix[j][i]
            res[i][j] = value

    return res


def _fill_last_row(
    matrix: list[list[float]], value: float
) -> list[list[float]]:
    matrix[-1] = [value] * len(matrix)
    return matrix


def calculate_probability(matrix: list[list[float]]) -> list[float]:
    count = len(matrix)

    coef_matrix = _create_coef_matrix(matrix)
    _fill_last_row(coef_matrix, 1.0)

    ordinate_values = [0 if i != count - 1 else 1 for i in range(count)]
    return linalg.solve(coef_matrix, ordinate_values).tolist()


def _calculate_probability_delta(
    matrix: list[list[float]],
    curr_prob: list[float],
) -> list[float]:
    count = len(matrix)

    prob_delta: list[float] = []
    coef_matrix = _create_coef_matrix(matrix)

    for i in range(count):
        for j in range(count):
            coef_matrix[i][j] *= curr_prob[j]

        prob_delta.append(sum(coef_matrix[i]) * TIME_DELTA)

    return prob_delta


def calculate_time(
    matrix: list[list[float]],
    prob: list[float],
) -> list[float]:
    count = len(matrix)

    time_curr = 0.0
    prob_curr: list[float] = [1.0 / count] * count
    time: list[float] = [0.0] * count

    while not all(time):
        prob_delta = _calculate_probability_delta(matrix, prob_curr)

        for i in range(count):
            if not time[i] and abs(prob_curr[i] - prob[i]) <= EPS:
                time[i] = time_curr

            prob_curr[i] += prob_delta[i]
        time_curr += TIME_DELTA

    return time
