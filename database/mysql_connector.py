import mysql.connector
import os

class MySqlConnector:
    def __init__(self, db_name):
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = db_name or os.getenv("DB_NAME")

        if not all([user, password, host, port, database]):
            raise ValueError("Database connection environment variables not set")

        self.config = {
            'user': user,
            'password': password,
            'host': host,
            'port': int(port),
            'database': database,
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
