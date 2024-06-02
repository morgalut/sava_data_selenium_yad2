import sqlite3

def create_tables():
    conn = sqlite3.connect('yad2_apartments.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_data_to_db(data):
    conn = sqlite3.connect('yad2_apartments.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO apartments (title, price, description) VALUES (?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()
