
import json
import sqlite3

def create_tables():
    with open('schema.json', 'r') as f:
        schema = json.load(f)

    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()

    for table_name, table_data in schema.items():
        columns = table_data['columns']
        column_definitions = []
        for column in columns:
            column_definitions.append(f"{column['name']} {column['type']}")
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
        cursor.execute(create_table_sql)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
