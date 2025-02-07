"""Custom Database wrapper for the project"""

import os
import sys
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.logger import logger  # pylint: disable=import-error, wrong-import-position


class DashboardDB:
    """Database wrapper class"""

    def __init__(self, db_name="main/db/dashboard.db"):
        self.db_name = db_name
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

        self.create_table()

    def create_table(self):
        """Initialise database if it doesn't already exist"""
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
        logger.logger.debug("Initialised db")

    def add_record(self, underlying, letf):
        """Add record to the dashboard"""
        self.cursor.execute(
            """
            INSERT INTO portfolio (underlying_ticker, letf_ticker)
            VALUES (?, ?)
        """,
            (underlying, letf),
        )
        self.conn.commit()
        logger.logger.info(f"Added {underlying} and {letf} to db")

    def is_pair_present(self, underlying, letf):
        """Check if a pair is present in the dashboard"""
        self.cursor.execute(
            "SELECT * FROM portfolio WHERE underlying_ticker = ? AND letf_ticker = ?",
            (underlying, letf),
        )
        return self.cursor.fetchone() is not None

    def get_all_records(self):
        """Get every record for the database"""
        self.cursor.execute("SELECT * FROM portfolio")
        return self.cursor.fetchall()

    def delete_record(self, underlying, letf):
        """Delete a inputted record from the database"""
        self.cursor.execute(
            "DELETE FROM portfolio WHERE underlying_ticker = ? AND letf_ticker = ?",
            (underlying, letf),
        )
        self.conn.commit()
        logger.logger.info(f"Deleted {underlying} and {letf} from db")

    def close(self):
        """Close the database connection."""
        self.conn.close()


dashboard = DashboardDB()
