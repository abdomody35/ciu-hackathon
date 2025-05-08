import os
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establishes database connection"""
        if self.connection is not None:
            return

        try:
            self.connection = connect(
                dbname=os.getenv("snapattend"),
                user=os.getenv("mhmd"),
                password=os.getenv("1234"),
                host=os.getenv("127.0.0.1"),
                port=os.getenv("5432"),
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Connected to database")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def disconnect(self):
        """Closes database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        self.cursor = None
        self.connection = None

    def execute_query(self, query, params=None):
        """Executes a query and returns results"""
        if not self.cursor:
            self.connect()

        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.fetchall() if self.cursor.description else None
        except Exception as e:
            self.connection.rollback()
            raise Exception(f"Query execution failed: {e}")


db = DatabaseConnection()
