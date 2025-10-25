
import sqlite3

class SqliteConnector:
    def __init__(self, db_name):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def close_connection(self, connection):
        connection.close()

    def get_tables_query(self):
        return "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

    def get_create_table_statement(self, table_name, cursor):
        """Fetches the CREATE TABLE statement for a given table."""
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = cursor.fetchone()
        return result[0] if result else None

    def get_table_schema_query(self, table_name):
        return f"PRAGMA table_info({table_name})"

    def create_table(self, table_name, columns):
        return f"CREATE TABLE {table_name} ({columns});"

    def delete_table(self, table_name):
        return f"DROP TABLE {table_name};"
