import os
import sqlite3
import sys
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from utils.decorators import log_execution_time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_operations import Database
from database.csv_writer import CSVWriter
from utils.helpers import random_delay, get_random_user_agent
from enums import URLs
from scraping.bs4_parser import Parser
from scraping.bs5_more_seraher import WebpageAnalyzer


class Scraper:
    DEBUG = True
    TOTAL_PAGES = 2822
    YAD2_ITEM_URL = 'https://www.yad2.co.il/realestate/item/{token}'
    
    def __init__(self, debug=False):
        self.DEBUG = debug
        self.db_path = 'C:\\Users\\Mor\\Desktop\\test\\yad2_scraper\\database\\yad2.db'
        self.db = Database()
        self.driver = None
        self.csv_writer = CSVWriter()  # Initialize the CSVWriter instance

    def initialize_driver(self, additional_options=None):
        options = webdriver.ChromeOptions()
        options.headless = not self.DEBUG
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent={get_random_user_agent()}')
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=options)
        
        if additional_options:
            for option in additional_options:
                options.add_argument(option)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": get_random_user_agent()})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
                
    def extract_data_from_page_items(self):
        items = self.driver.find_elements(By.XPATH, "//*[@id='__next']/div/main/div[2]/div/div/div[4]/ul/li/div/div/a/div")
        data_list = []
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "h2[data-nagish='content-section-title']").text
            except (AttributeError, Exception):
                title = "N/A"

            try:
                price = item.find_element(By.CLASS_NAME, "price_price__xQt90").text
            except (AttributeError, Exception):
                price = "N/A"

            try:
                description = item.find_element(By.CLASS_NAME, "item-data-content_itemInfoLine__AeoPP").text
            except (AttributeError, Exception):
                description = "N/A"

            try:
                link = item.find_element(By.XPATH, "..").get_attribute("href")
                token = link.split("/item/")[1].split("?")[0]
            except (AttributeError, Exception):
                token = "N/A"

            if token == "N/A" or price == "N/A":
                continue

            date = time.strftime('%Y-%m-%d')
            hour = time.strftime('%H:%M:%S')

            row = {
                'date': date,
                'hour': hour,
                'link': link,
                'token': token,
                'price': price,
                'title': title,
                'description': description
            }
            data_list.append(row)

        return data_list

    def extract_data_from_page(self, token):
        data_list = []
        url = self.YAD2_ITEM_URL.format(token=token)
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        try:
            title_element = self.driver.find_element(By.CSS_SELECTOR, "h1.heading_heading__SB617")
            price_element = self.driver.find_element(By.CSS_SELECTOR, "span.price_price__xQt90")
            description_element = self.driver.find_element(By.CSS_SELECTOR, "p.description_description__l3oun")

            data_list.append({
                'title': title_element.text if title_element else 'N/A',
                'price': price_element.text if price_element else 'N/A',
                'description': description_element.text if description_element else 'N/A',
                'token': token,
                'link': url,
                'date': time.strftime('%Y-%m-%d'),
                'hour': time.strftime('%H:%M:%S')
            })
        except Exception as e:
            logging.error(f"Error extracting data from page for token {token}: {e}")

        return data_list

    def save_data_to_db(self, data):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            for row in data:
                title = row.get('title', 'N/A')
                price = row.get('price', 'N/A')
                description = row.get('description', 'N/A')
                token = row.get('token', 'N/A')
                date = row.get('date', time.strftime('%Y-%m-%d'))
                hour = row.get('hour', time.strftime('%H:%M:%S'))
                link = row.get('link', 'N/A')

                print(f"Processing token: {token}, title: {title}, price: {price}")

                c.execute('SELECT id, price FROM apartments WHERE token = ?', (token,))
                apartment_row = c.fetchone()

                if apartment_row:
                    apartment_id = apartment_row[0]
                    old_price = apartment_row[1]
                    if old_price != price:
                        c.execute('UPDATE apartments SET price = ?, date = ?, hour = ? WHERE id = ?', (price, date, hour, apartment_id))
                        c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                  (apartment_id, title, price, description, date, hour, token, link))
                    else:
                        c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                  (apartment_id, title, price, description, date, hour, token, link))
                else:
                    c.execute('INSERT INTO apartments (title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                              (title, price, description, date, hour, token, link))
                    apartment_id = c.lastrowid
                    c.execute('INSERT INTO apartment_history (apartment_id, title, price, description, date, hour, token, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                              (apartment_id, title, price, description, date, hour, token, link))

                c.execute('INSERT INTO token_history (token, date, time, price) VALUES (?, ?, ?, ?)', (token, date, hour, price))
                conn.commit()

        except Exception as e:
            logging.error(f"Error saving data to database: {e}")
            conn.rollback()

        finally:
            if conn:
                conn.close()

    def save_data_to_csv(self, data, filename):
        import csv
        keys = data[0].keys() if data else []
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

    def handle_captcha(self):
        if self.DEBUG:
            print("CAPTCHA detected. Please solve it manually.")
        self.driver.save_screenshot('captcha.png')
        captcha_url = self.driver.current_url
        print(f"Solve the CAPTCHA here: {captcha_url}")
        input("Press Enter after solving the CAPTCHA...")
        
        
    @log_execution_time
    def scrape_token(self, token):
        try:
            self.initialize_driver()
            url = self.YAD2_ITEM_URL.format(token=token)
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            if "captcha" in self.driver.current_url:
                self.handle_captcha()

            data = self.extract_data_from_page(token)
            if not data:
                logging.warning("No data extracted from page")

            if self.DEBUG:
                print("Extracted data:", data)

            csv_filename = f'yad2_{token}.csv'
            self.save_data_to_csv(data, csv_filename)

            if data:
                self.save_data_to_db(data)

            time.sleep(2)

        except Exception as e:
            logging.error(f"Error scraping token {token}: {e}")

        finally:
            if self.driver:
                self.driver.quit()
            if self.DEBUG:
                print(f"Scraping of token {token} completed")

    @log_execution_time
    def scrape_page(self, page_number):
        try:
            if self.driver is None:
                self.initialize_driver()
            url = f"https://www.yad2.co.il/realestate/forsale?bBox=30.528827%2C32.047508%2C34.087585%2C34.920591&status=0&owner=0&page={page_number}"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

            if "captcha" in self.driver.current_url:
                self.handle_captcha()

            self.scroll_down()
            data_list = self.extract_data_from_page_items()

            csv_filename = f'yad2_page_{page_number}.csv'
            self.csv_writer.save_data_to_csv(data_list, csv_filename)  # Use CSVWriter to save data

            if data_list:
                self.save_data_to_db(data_list)

            time.sleep(random.uniform(2, 5) if not self.DEBUG else 1)

        except Exception as e:
            logging.error(f"Error scraping page {page_number}: {e}")

        finally:
            if self.DEBUG:
                print(f"Scraping of page {page_number} completed")

    def extract_token_from_url(self, url):
        # Assuming the token is the last part of the URL after '/'
        return url.split('/')[-1].strip()
                
    def scroll_down(self):
        scroll_pause_time = random.uniform(2, 5) if not self.DEBUG else 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
