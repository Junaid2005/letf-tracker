import sqlite3
import os


class DashboardDB:
    def __init__(self, db_name="main/db/dashboard.db"):
        self.db_name = db_name
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                underlying_ticker TEXT NOT NULL,
                letf_ticker TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def add_record(self, underlying, letf):
        self.cursor.execute(
            """
            INSERT INTO portfolio (underlying_ticker, letf_ticker)
            VALUES (?, ?)
        """,
            (underlying, letf),
        )
        self.conn.commit()

    def get_all_records(self):
        self.cursor.execute("SELECT * FROM portfolio")
        return self.cursor.fetchall()

    def delete_record(self, underlying):
        self.cursor.execute(
            "DELETE FROM portfolio WHERE underlying_ticker = ?", (underlying,)
        )
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()
