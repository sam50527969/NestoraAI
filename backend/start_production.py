"""Production entrypoint for the Nestora backend."""

from __future__ import annotations

import os
import sys


def start_server() -> None:
    """Replace this process with the production Uvicorn server."""
    port = os.getenv("PORT", "8000")

    os.execvp(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            port,
        ],
    )


def main() -> None:
    start_server()


if __name__ == "__main__":
    main()
