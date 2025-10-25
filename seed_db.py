import json
import sqlite3

def create_tables():
    with open('schema.json', 'r') as f:
        schema = json.load(f)

    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    for table_name, table_data in schema.items():
        columns = table_data['columns']
        column_definitions = []
        for column in columns:
            col_def = f"{column['name']} {column['type']}"
            # Optionally mark 'id' columns as PRIMARY KEY
            if column['name'] == 'id':
                col_def += " PRIMARY KEY"
            column_definitions.append(col_def)

        # Add foreign key constraints for orders table
        if table_name == 'orders':
            column_definitions.append("FOREIGN KEY(user_id) REFERENCES users(id)")
            column_definitions.append("FOREIGN KEY(product_id) REFERENCES products(id)")

        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_definitions)});"
        cursor.execute(create_table_sql)

    conn.commit()
    conn.close()

def clear_db():
    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()

    # Drop all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")

    conn.commit()
    conn.close()

def populate_tables():
    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()

    # Populate users table
    users_data = [
        (1, 'Alice', 'alice@example.com'),
        (2, 'Bob', 'bob@example.com'),
        (3, 'Charlie', 'charlie@example.com')
    ]
    cursor.executemany("INSERT INTO users (id, name, email) VALUES (?, ?, ?)", users_data)

    # Populate products table
    products_data = [
        (1, 'Laptop', 999.99),
        (2, 'Mouse', 29.99),
        (3, 'Keyboard', 49.99)
    ]
    cursor.executemany("INSERT INTO products (id, name, price) VALUES (?, ?, ?)", products_data)

    # Populate orders table
    orders_data = [
        (1, 1, 1, 1),
        (2, 1, 2, 2),
        (3, 2, 3, 1),
        (4, 3, 1, 1)
    ]
    cursor.executemany("INSERT INTO orders (id, user_id, product_id, quantity) VALUES (?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Clearing database...")
    clear_db()
    print("Creating tables...")
    create_tables()
    print("Populating tables...")
    populate_tables()
    print("Database setup complete.")