"""Local development entrypoint for the Nestora backend."""

from __future__ import annotations

import os
import subprocess
import sys


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = "8001"


def main() -> None:
    host = os.getenv(
        "NESTORA_DEV_HOST",
        DEFAULT_HOST,
    )

    port = os.getenv(
        "NESTORA_DEV_PORT",
        DEFAULT_PORT,
    )

    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            host,
            "--port",
            port,
            "--reload",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
