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

if (
    APP_ENV.lower() == "production"
    and AUTH_SECRET_KEY.startswith(
        "nestora-development-secret"
    )
):
    raise RuntimeError(
        "AUTH_SECRET_KEY must be configured "
        "in production."
    )
