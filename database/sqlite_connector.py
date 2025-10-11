import sqlite3

class SqliteConnector:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def close_connection(self, connection):
        connection.close()

    def get_tables_query(self):
        return "SELECT name FROM sqlite_master WHERE type='table';"

    def get_table_schema_query(self, table_name):
        return f"PRAGMA table_info({table_name})"