import sqlite3

def create_tables():
    conn = sqlite3.connect('yad2_apartments.db')
    c = conn.cursor()
    
    # Create main apartments table with price
    c.execute('''
        CREATE TABLE IF NOT EXISTS apartments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            description TEXT,
            date TEXT
        )
    ''')

    # Create history table to track price changes
    c.execute('''
        CREATE TABLE IF NOT EXISTS apartment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apartment_id INTEGER,
            price TEXT,
            date TEXT,
            FOREIGN KEY(apartment_id) REFERENCES apartments(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def save_data_to_db(item):
    conn = sqlite3.connect('yad2_apartments.db')
    c = conn.cursor()
    
    title = item['title']
    price = item['price']
    description = item['description']
    date = item.get('date', 'N/A')  # Assuming 'date' might not be present
    
    # Check if the apartment already exists
    c.execute('''
        SELECT id, price FROM apartments WHERE title = ? AND description = ?
    ''', (title, description))
    
    apartment_row = c.fetchone()
    
    if apartment_row:
        apartment_id = apartment_row[0]
        old_price = apartment_row[1]
        # Check if the price has changed
        if old_price != price:
            # Update the price in the main table
            c.execute('''
                UPDATE apartments SET price = ?, date = ? WHERE id = ?
            ''', (price, date, apartment_id))

            # Insert new price record into history
            c.execute('''
                INSERT INTO apartment_history (apartment_id, price, date) VALUES (?, ?, ?)
            ''', (apartment_id, price, date))
    else:
        # Insert new apartment record with current price
        c.execute('''
            INSERT INTO apartments (title, price, description, date) VALUES (?, ?, ?, ?)
        ''', (title, price, description, date))
        
        apartment_id = c.lastrowid
        
        # Insert price record into history
        c.execute('''
            INSERT INTO apartment_history (apartment_id, price, date) VALUES (?, ?, ?)
        ''', (apartment_id, price, date))
    
    conn.commit()
    conn.close()
