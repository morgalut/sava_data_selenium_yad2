import sqlite3
import os

class Database:
    def __init__(self, db_name='yad2_apartments.db', base_path=None):
        if base_path is None:
            base_path = os.path.dirname(__file__)  # Get the directory of the current script
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
                token TEXT UNIQUE
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
                token TEXT,
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
            date = item.get('date', 'N/A')
            token = item['token']
            
            c.execute('SELECT id, price FROM apartments WHERE token = ?', (token,))
            apartment_row = c.fetchone()
            
            if apartment_row:
                apartment_id = apartment_row[0]
                old_price = apartment_row[1]
                if old_price != price:
                    c.execute('UPDATE apartments SET price = ?, date = ? WHERE id = ?', (price, date, apartment_id))
                    c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, token) VALUES (?, ?, ?, ?, ?, ?)',
                              (apartment_id, title, old_price, description, date, token))
            else:
                c.execute('INSERT INTO apartments (title, price, description, date, token) VALUES (?, ?, ?, ?, ?)', (title, price, description, date, token))
                apartment_id = c.lastrowid
                c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, token) VALUES (?, ?, ?, ?, ?, ?)', 
                          (apartment_id, title, price, description, date, token))
        
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
    base_path = "C:\\Users\\Mor\\Desktop\\test\\yad2_scraper"
    db = Database(base_path=base_path)
