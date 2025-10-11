from .sqlite_connector import SqliteConnector
from .mysql_connector import MySqlConnector

def get_database_connector(db_type, db_name):
    if db_type == "sqlite":
        return SqliteConnector(db_name)
    elif db_type == "mysql":
        return MySqlConnector(db_name)
    else:
        raise ValueError("Invalid database type")