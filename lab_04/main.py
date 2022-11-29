import click

from event_model import EventModel
from step_model import StepModel

from distributions import UniformGenerator, ExponentialProcessor


@click.command()
@click.option("-a", required=False, help="a param", default=1)
@click.option("-b", required=False, help="b param", default=10)
@click.option("-lambda_value", required=False, help="lambda param", default=0.2)
@click.option("-tasks_qty", required=False, help="Tasks quantity", default=1000)
@click.option("-repeat_percent", required=False, help="Repeat %", default=0.0)
@click.option("-step", required=False, help="Step", default=0.01)
def main(
    a: int,
    b: int,
    lambda_value: int,
    tasks_qty: int,
    repeat_percent: float,
    step: float,
):
    generator = UniformGenerator(a, b)
    processor = ExponentialProcessor(lambda_value)
    event_model = EventModel(generator, processor, tasks_qty, repeat_percent)
    step_model = StepModel(
        generator, processor, tasks_qty, repeat_percent, step
    )

    print()
    click.secho(f"event_model: {event_model.run()}", bold=True, bg="red")
    click.secho(f"step_model: {step_model.run()}", bold=True, bg="blue")


if __name__ == "__main__":
    main()
