# C:\Users\Mor\Desktop\test\yad2_scraper\database\db_operations.py

import sqlite3
import logging
import matplotlib.pyplot as plt
from datetime import datetime
import os
from enum import Enum

class TableName(Enum):
    APARTMENTS = 'apartments'
    APARTMENT_HISTORY = 'apartment_history'
    TOKEN_HISTORY = 'token_history'

class Database:
    DB_DIR = 'database'

    def __init__(self, db_path='database/yad2.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def create_database(self):
        os.makedirs(self.DB_DIR, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(f'''
                CREATE TABLE IF NOT EXISTS {TableName.APARTMENTS.value} (
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
            c.execute(f'''
                CREATE TABLE IF NOT EXISTS {TableName.APARTMENT_HISTORY.value} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    apartment_id INTEGER,
                    title TEXT,
                    price TEXT,
                    description TEXT,
                    date TEXT,
                    hour TEXT,
                    token TEXT,
                    link TEXT,
                    FOREIGN KEY (apartment_id) REFERENCES apartments(id)
                )
            ''')
            c.execute(f'''
                CREATE TABLE IF NOT EXISTS {TableName.TOKEN_HISTORY.value} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT,
                    date TEXT,
                    time TEXT,
                    price TEXT
                )
            ''')
            conn.commit()

    def save_token_history(self, token, price):
        date = datetime.now().strftime('%Y-%m-%d')
        time = datetime.now().strftime('%H:%M:%S')
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute(f'INSERT INTO {TableName.TOKEN_HISTORY.value} (token, date, time, price) VALUES (?, ?, ?, ?)', (token, date, time, price))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"SQLite error occurred: {e}")
            conn.rollback()

    def display_price_trends(self, token):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''
                SELECT date, price
                FROM apartment_history
                WHERE token = ?
                ORDER BY date
            ''', (token,))
            rows = c.fetchall()

            if not rows:
                print(f"No price trends found for token: {token}")
                return

            dates = [row[0] for row in rows]
            prices = [row[1] for row in rows]

            # Plotting the price trends
            plt.figure(figsize=(10, 5))
            plt.plot(dates, prices, marker='o', linestyle='-', color='b')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(f'Price Trends for Token: {token}')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            plt.show()

        except sqlite3.Error as e:
            self.logger.error(f"SQLite error occurred: {e}")
        finally:
            if conn:
                conn.close()

    # Other methods (e.g., save_token_history, etc.) would be here
