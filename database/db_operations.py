import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='yad2_apartments.db', base_path=None):
        if base_path is None:
            base_path = os.path.dirname(__file__)
        db_path = os.path.join(base_path, db_name)
        self.db_path = db_path
        self.ensure_directory_exists()
        self.create_tables()

    def ensure_directory_exists(self):
        directory = os.path.dirname(self.db_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def create_tables(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS apartments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                price TEXT,
                description TEXT,
                date TEXT,
                hour TEXT,
                token TEXT UNIQUE,
                link TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS apartment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                apartment_id INTEGER,
                title TEXT,
                price TEXT,
                description TEXT,
                date TEXT,
                hour TEXT,
                token TEXT,
                link TEXT,
                FOREIGN KEY(apartment_id) REFERENCES apartments(id)
            )
        ''')
        conn.commit()
        conn.close()

    def save_data_to_db(self, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        for item in data:
            title = item['title']
            price = item['price']
            description = item['description']
            date = item.get('date', datetime.now().strftime('%Y-%m-%d'))
            hour = item.get('hour', datetime.now().strftime('%H:%M:%S'))
            token = item['token']
            link = item['link']
            
            try:
                c.execute('SELECT id, price FROM apartments WHERE token = ?', (token,))
                apartment_row = c.fetchone()
                
                if apartment_row:
                    apartment_id = apartment_row[0]
                    old_price = apartment_row[1]
                    if old_price != price:
                        c.execute('UPDATE apartments SET price = ?, date = ?, hour = ? WHERE id = ?', (price, date, hour, apartment_id))
                        c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                (apartment_id, title, old_price, description, date, hour, token, link))
                else:
                    c.execute('INSERT INTO apartments (title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                              (title, price, description, date, hour, token, link))
                    apartment_id = c.lastrowid
                    c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                              (apartment_id, title, price, description, date, hour, token, link))
            
            except Exception as e:
                print(f"Error inserting data into DB: {e}")
                conn.rollback()
            else:
                conn.commit()
            
        conn.close()

    def view_price_trends(self, token):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT a.title, a.price as current_price, a.date as current_date, h.price as historical_price, h.date as historical_date
            FROM apartments a
            LEFT JOIN apartment_history h ON a.id = h.apartment_id
            WHERE a.token = ?
            ORDER BY h.date DESC
        ''', (token,))
        rows = c.fetchall()
        conn.close()
        
        for row in rows:
            print(f"Title: {row[0]}")
            print(f"Current Price: {row[1]} (Date: {row[2]})")
            if row[3] is not None:
                print(f"Historical Price: {row[3]} (Date: {row[4]})")
            print("---")

# Usage example:
if __name__ == "__main__":
    BASE_PATH = "C:\\Users\\Mor\\Desktop\\test\\yad2_scraper"
    DB = Database(base_path=BASE_PATH)
