from sqlalchemy import text

from app.tickets.database import SessionLocal, create_tables


def main():
    create_tables()

    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1 AS ok")).mappings().one()
        print("PostgreSQL connection OK.")
        print(dict(result))
    finally:
        db.close()


if __name__ == "__main__":
    main()