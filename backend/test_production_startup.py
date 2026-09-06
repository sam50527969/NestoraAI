from unittest.mock import patch

import start_production


def test_start_server_uses_platform_port(
    monkeypatch,
):
    monkeypatch.setenv("PORT", "9123")

    with patch(
        "start_production.os.execvp",
    ) as execvp:
        start_production.start_server()

    execvp.assert_called_once_with(
        start_production.sys.executable,
        [
            start_production.sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "9123",
        ],
    )


def test_start_server_defaults_to_port_8000(
    monkeypatch,
):
    monkeypatch.delenv(
        "PORT",
        raising=False,
    )

    with patch(
        "start_production.os.execvp",
    ) as execvp:
        start_production.start_server()

    assert execvp.call_args.args[1][-1] == "8000"


def test_run_migrations_prepares_production_database():
    with patch(
        "start_production.subprocess.run",
    ) as run:
        start_production.run_migrations()

    run.assert_called_once_with(
        [
            start_production.sys.executable,
            "prepare_production_database.py",
        ],
        check=True,
    )


def test_main_runs_migrations_before_server():
    call_order = []

    with (
        patch(
            "start_production.run_migrations",
            side_effect=lambda: call_order.append("migrations"),
        ) as migrations,
        patch(
            "start_production.start_server",
            side_effect=lambda: call_order.append("server"),
        ) as server,
    ):
        start_production.main()

    migrations.assert_called_once_with()
    server.assert_called_once_with()
    assert call_order == ["migrations", "server"]
