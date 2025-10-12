
import sqlite3
import datetime
import random

def get_random_timestamp():
    return datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 365), hours=random.randint(0, 24), minutes=random.randint(0, 60), seconds=random.randint(0, 60))

def populate_tables():
    conn = sqlite3.connect('Chinook.db')
    cursor = conn.cursor()

    # Populate users table
    users_data = [
        (1, 'Alice', 'alice@example.com', datetime.datetime.now()),
        (2, 'Bob', 'bob@example.com', datetime.datetime.now()),
        (3, 'Charlie', 'charlie@example.com', datetime.datetime.now())
    ]
    cursor.executemany("INSERT INTO users (id, name, email, timestamp) VALUES (?, ?, ?, ?)", users_data)

    # Populate products table
    products_data = [
        (1, 'Laptop', 999.99, get_random_timestamp()),
        (2, 'Mouse', 29.99, get_random_timestamp()),
        (3, 'Keyboard', 49.99, get_random_timestamp())
    ]
    cursor.executemany("INSERT INTO products (id, name, price, timestamp) VALUES (?, ?, ?, ?)", products_data)

    # Populate orders table
    orders_data = [
        (1, 1, 1, 1, get_random_timestamp()),
        (2, 1, 2, 2, get_random_timestamp()),
        (3, 2, 3, 1, get_random_timestamp()),
        (4, 3, 1, 1, get_random_timestamp())
    ]
    cursor.executemany("INSERT INTO orders (id, user_id, product_id, quantity, timestamp) VALUES (?, ?, ?, ?, ?)", orders_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    populate_tables()
