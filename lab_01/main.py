from collections.abc import Iterable
from typing import Literal

import click
import matplotlib.pyplot as plt
import numpy as np

from distributions import uniform_cdf, uniform_pdf, exp_cdf, exp_pdf


def draw_graphics(
    x_values: Iterable[float],
    cdf_values: Iterable[float],
    pdf_values: Iterable[float],
    title: str,
) -> None:
    fig, axs = plt.subplots(2, figsize=(6, 7))

    fig.suptitle(title)
    axs[0].plot(x_values, cdf_values, color="green")
    axs[1].plot(x_values, pdf_values, color="green")

    axs[0].set_xlabel("x")
    axs[0].set_ylabel("F(x)")

    axs[1].set_xlabel("x")
    axs[1].set_ylabel("f(x)")

    axs[0].grid(True)
    axs[1].grid(True)
    plt.show()


def process_uniform(
    x_values: Iterable[float],
    a: float,
    b: float,
) -> tuple[list[float], list[float]]:
    cdf_res: list[float] = []
    pdf_res: list[float] = []

    for x in x_values:
        cdf_res.append(uniform_cdf(x, a, b))
        pdf_res.append(uniform_pdf(x, a, b))

    return cdf_res, pdf_res


def process_expo(
    x_values: Iterable[float],
    lambda_: float,
) -> tuple[list[float], list[float]]:
    cdf_res: list[float] = []
    pdf_res: list[float] = []

    for x in x_values:
        cdf_res.append(exp_cdf(x, lambda_))
        pdf_res.append(exp_pdf(x, lambda_))

    return cdf_res, pdf_res


def generate_x_values(start: float, end: float, step: float = 1e-3):
    delta = end - start
    return np.arange(start - delta / 2, end + delta / 2, step)


@click.command()
@click.option(
    "-distribution",
    required=True,
    help="Distribution kind ('uniform' or 'exp')",
)
def main(distribution: Literal["uniform"] | Literal["exp"]) -> None:
    if distribution not in ("uniform", "exp"):
        click.secho("\nУкажите верный тип распределения (см. --help)", fg="red", bold=True)
        return

    a = float(input("Введите a: "))
    b = float(input("Введите b: "))

    x_values = generate_x_values(a, b)

    if distribution == "exp":
        lambda_ = float(input("Введите параметр lambda: "))
        expo_cdf_res, expo_pdf_res = process_expo(x_values, lambda_)
        draw_graphics(
            x_values,
            cdf_values=expo_cdf_res,
            pdf_values=expo_pdf_res,
            title="Экспоненциальное распределение",
        )
    else:
        uniform_cdf_res, uniform_pdf_res = process_uniform(x_values, a, b)
        draw_graphics(
            x_values,
            cdf_values=uniform_cdf_res,
            pdf_values=uniform_pdf_res,
            title="Равномерное распределение",
        )


if __name__ == "__main__":
    main()
