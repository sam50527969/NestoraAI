import os

from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./nestora.db",
)


APP_NAME = os.getenv(
    "APP_NAME",
    "Nestora AI Backend",
)

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0",
)

SENTRY_DSN = os.getenv(
    "SENTRY_DSN",
    "",
).strip()

SENTRY_TRACES_SAMPLE_RATE = float(
    os.getenv(
        "SENTRY_TRACES_SAMPLE_RATE",
        "0.0",
    )
)

EMAIL_PROVIDER = os.getenv(
    "EMAIL_PROVIDER",
    "disabled",
).strip().lower()

RESEND_API_KEY = os.getenv(
    "RESEND_API_KEY",
    "",
).strip()

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "",
).strip()


CORS_ALLOWED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        (
            "http://localhost:5173,"
            "http://localhost:5174,"
            "http://localhost:5175,"
            "http://localhost:5176"
        ),
    ).split(",")
    if origin.strip()
]

AUTH_SECRET_KEY = os.getenv(
    "AUTH_SECRET_KEY",
    (
        "nestora-development-secret-"
        "replace-before-production"
    ),
)

AUTH_ALGORITHM = "HS256"

AUTH_ACCESS_TOKEN_MINUTES = int(
    os.getenv(
        "AUTH_ACCESS_TOKEN_MINUTES",
        "60",
    )
)

if APP_ENV.lower() == "production":
    if not CORS_ALLOWED_ORIGINS:
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS must contain "
            "at least one production origin."
        )

    if "*" in CORS_ALLOWED_ORIGINS:
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS must not contain "
            "a wildcard in production."
        )

    if any(
        origin.startswith(
            (
                "http://localhost",
                "https://localhost",
                "http://127.0.0.1",
                "https://127.0.0.1",
            )
        )
        for origin in CORS_ALLOWED_ORIGINS
    ):
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS must not contain "
            "localhost origins in production."
        )

    if AUTH_SECRET_KEY.startswith(
        "nestora-development-secret"
    ):
        raise RuntimeError(
            "AUTH_SECRET_KEY must be configured "
            "in production."
        )

    if DATABASE_URL.lower().startswith("sqlite"):
        raise RuntimeError(
            "DATABASE_URL must use a production "
            "database in production."
        )
