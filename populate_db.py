
import sqlite3

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
    populate_tables()
