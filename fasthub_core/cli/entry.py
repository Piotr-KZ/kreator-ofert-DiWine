"""
Entry point — importuje komendy i uruchamia app.

W setup.py:
    entry_points={
        "console_scripts": [
            "fasthub = fasthub_core.cli.entry:main",
        ],
    }
"""

from fasthub_core.cli.app import app
# Import commands to register them
import fasthub_core.cli.commands  # noqa: F401


def main():
    app()


if __name__ == "__main__":
    main()
