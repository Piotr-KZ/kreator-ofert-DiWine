"""
CLI App — główna aplikacja Typer.
"""

import typer

app = typer.Typer(
    name="fasthub",
    help="WebCreator — komendy administracyjne SaaS",
    no_args_is_help=True,
)
