"""gitpulse CLI — Git repository health analyzer — commit velocity, hot files, author stats, activity patterns"""

import sys

import click

from .core import fetch, to_csv, to_json, to_table, to_text
from .introspect import get_introspect_json, get_skill_md

_ACLI_COMMANDS = {"introspect", "skill"}


def _handle_acli_command(cmd: str) -> None:
    if cmd == "introspect":
        print(get_introspect_json())
    elif cmd == "skill":
        print(get_skill_md())


@click.command()
@click.argument("path", required=False, default=None)
@click.option("--limit", "-n", default=10, show_default=True, help="How many items to fetch.")
@click.option(
    "--output",
    "-o",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json", "table", "csv"]),
    help="Output format.",
)
def main(path, limit, output):
    """Git repository health analyzer — commit velocity, hot files, author stats, activity patterns

    Special commands: gitpulse introspect | gitpulse skill
    """
    if path in _ACLI_COMMANDS:
        _handle_acli_command(path)
        sys.exit(0)

    items = fetch(path, limit=limit)

    if output == "text":
        click.echo(to_text(items))
    elif output == "json":
        click.echo(to_json(items))
    elif output == "table":
        click.echo(to_table(items))
    else:
        click.echo(to_csv(items), nl=False)


if __name__ == "__main__":
    main()
