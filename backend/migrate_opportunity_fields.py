import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "nestora.db"

NEW_COLUMNS = {
    "opportunity_score": "INTEGER",
    "estimated_value": "INTEGER",
    "closing_probability": "INTEGER",
    "business_potential": "VARCHAR",
    "opportunity_recommendation": "TEXT",
}


def get_existing_columns(cursor):
    cursor.execute("PRAGMA table_info(leads)")
    return {
        row[1]
        for row in cursor.fetchall()
    }


def run_migration():
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()
        existing_columns = get_existing_columns(cursor)

        added_columns = []

        for column_name, column_type in NEW_COLUMNS.items():
            if column_name in existing_columns:
                print(
                    f"Already exists: {column_name}"
                )
                continue

            cursor.execute(
                f"ALTER TABLE leads "
                f"ADD COLUMN {column_name} {column_type}"
            )

            added_columns.append(column_name)
            print(f"Added: {column_name}")

        connection.commit()

        if added_columns:
            print(
                "\nMigration completed successfully."
            )
        else:
            print(
                "\nNo changes were required."
            )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    run_migration()