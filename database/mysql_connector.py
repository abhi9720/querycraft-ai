import mysql.connector

class MySqlConnector:
    def __init__(self, db_name):
        # You would typically get these from a config file
        self.config = {
            'user': 'user',
            'password': 'password',
            'host': 'host',
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
        return f"DESCRIBE {table_name};"