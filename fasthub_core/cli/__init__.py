"""
FastHub CLI — komendy administracyjne.

Użycie:
    fasthub seed            — załaduj plany, role, uprawnienia
    fasthub create-admin    — stwórz pierwszego administratora
    fasthub check           — sprawdź połączenia (DB, Redis, Stripe)
    fasthub show-config     — pokaż aktualną konfigurację
    fasthub shell           — interaktywna konsola

Rozszerzanie (w aplikacji):
    from fasthub_core.cli import app as cli_app

    @cli_app.command()
    def my_command():
        typer.echo("Custom command")

    # W setup.py lub pyproject.toml:
    # [project.scripts]
    # myapp = "my_app.cli:cli_app"
"""

from fasthub_core.cli.app import app

__all__ = ["app"]
