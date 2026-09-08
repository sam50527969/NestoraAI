from __future__ import annotations

from types import SimpleNamespace


def test_monitoring_is_disabled_without_dsn(monkeypatch):
    from app.bootstrap import monitoring

    monkeypatch.setattr(monitoring, "SENTRY_DSN", "")

    called = False

    def fake_init(**kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(
        monitoring,
        "sentry_sdk",
        SimpleNamespace(init=fake_init),
    )

    assert monitoring.initialize_monitoring() is False
    assert called is False


def test_monitoring_initializes_when_dsn_is_configured(monkeypatch):
    from app.bootstrap import monitoring

    captured = {}

    monkeypatch.setattr(
        monitoring,
        "SENTRY_DSN",
        "https://example.invalid/123",
    )
    monkeypatch.setattr(
        monitoring,
        "APP_ENV",
        "production",
    )
    monkeypatch.setattr(
        monitoring,
        "APP_VERSION",
        "1.0.0",
    )
    monkeypatch.setattr(
        monitoring,
        "SENTRY_TRACES_SAMPLE_RATE",
        0.1,
    )

    def fake_init(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(
        monitoring,
        "sentry_sdk",
        SimpleNamespace(init=fake_init),
    )

    assert monitoring.initialize_monitoring() is True

    assert captured["dsn"] == "https://example.invalid/123"
    assert captured["environment"] == "production"
    assert captured["release"] == "nestora-backend@1.0.0"
    assert captured["traces_sample_rate"] == 0.1
    assert captured["send_default_pii"] is False


def test_monitoring_initialization_is_idempotent(monkeypatch):
    from app.bootstrap import monitoring

    calls = []

    monkeypatch.setattr(
        monitoring,
        "SENTRY_DSN",
        "https://example.invalid/123",
    )
    monkeypatch.setattr(
        monitoring,
        "_initialized",
        False,
    )

    def fake_init(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(
        monitoring,
        "sentry_sdk",
        SimpleNamespace(init=fake_init),
    )

    assert monitoring.initialize_monitoring() is True
    assert monitoring.initialize_monitoring() is True
    assert len(calls) == 1
