import os  # built-in: read environment variables

import psycopg2  # Python driver for PostgreSQL
from dotenv import load_dotenv  # loads settings from the .env file

load_dotenv()  # reads the .env file


def get_connection():
    """Open a connection to the bank360 Postgres database."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


if __name__ == "__main__":
    # quick self-test: run this file directly to check the connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            print(cur.fetchone())