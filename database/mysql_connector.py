import mysql.connector
import os
from urllib.parse import urlparse

class MySqlConnector:
    def __init__(self, db_name):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL environment variable not set")

        parsed_url = urlparse(db_url)
        
        self.config = {
            'user': parsed_url.username,
            'password': parsed_url.password,
            'host': parsed_url.hostname,
            'port': parsed_url.port,
            'database': db_name,
            'raise_on_warnings': True
        }

    def get_connection(self):
        return mysql.connector.connect(**self.config)

    def close_connection(self, connection):
        connection.close()
    
    def get_tables_query(self):
        return "SHOW TABLES;"

    def get_table_schema_query(self, table_name):
        return f"SELECT column_name, column_type FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = '{self.config['database']}';"

    def create_table(self, table_name, columns):
        return f"CREATE TABLE {table_name} ({columns});"

    def delete_table(self, table_name):
        return f"DROP TABLE {table_name};"

    def get_create_table_statement(self, table_name, cursor):
        """Fetches the CREATE TABLE statement for a given table."""
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        result = cursor.fetchone()
        return result[1] if result else None
