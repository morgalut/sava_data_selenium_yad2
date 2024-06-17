from lib2to3.pgen2 import token
import sqlite3
import sys
import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Ensure the parent directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db_operations import Database
from database.csv_writer import CSVWriter
from utils.helpers import random_delay, get_random_user_agent
from enums import URLs
from scraping.bs4_parser import Parser
from scraping.bs5_more_seraher import WebpageAnalyzer

class Scraper:
    DEBUG = True
    TOTAL_PAGES = 1
    VALIDATION_URL = "https://validate.perfdrive.com/ccb4768f5e2ea98586d13473d71efc83/"

    def __init__(self, debug=False):
        self.DEBUG = debug
        self.VALIDATION_URL = f"https://www.yad2.co.il/realestate/item/{token}"  # Adjust according to your token handling
        self.db = Database()
        self.driver = None

    def initialize_driver(self, additional_options=None):
        options = Options()
        options.headless = not self.DEBUG
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={get_random_user_agent()}')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if additional_options:
            for option in additional_options:
                options.add_argument(option)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": get_random_user_agent()})
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

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

    def extract_data_from_page(self):
        items = self.driver.find_elements(
            By.XPATH,
            "//*[@id='__next']/div/main/div[2]/div/div/div[4]/ul/li/div/div/a/div"
        )
        data_list = []
        for item in items:
            try:
                title = item.find_element(
                    By.CSS_SELECTOR, "h2[data-nagish='content-section-title']"
                ).text
            except (AttributeError, Exception):
                title = "N/A"

            try:
                price = item.find_element(By.CLASS_NAME, "price_price__xQt90").text
            except (AttributeError, Exception):
                price = "N/A"

            try:
                description = item.find_element(
                    By.CLASS_NAME, "item-data-content_itemInfoLine__AeoPP"
                ).text
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

    def save_data_to_db(self, data):
        conn = sqlite3.connect(self.db.db_path)
        c = conn.cursor()

        # Log the type of `data` and its first element if available
        logging.debug(f"Data type: {type(data)}")
        if data:
            logging.debug(f"First element type: {type(data[0])}, value: {data[0]}")

        for row in data:
            # Check the type of `row` before accessing its elements
            if not isinstance(row, dict):
                logging.error(f"Expected row to be a dict, but got {type(row)}: {row}")
                continue

            title = row['title']
            price = row['price']
            description = row['description']
            date = row['date']
            hour = row['hour']
            token = row['token']
            link = row['link']

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
                logging.error(f"Error inserting data into DB: {e}")
                conn.rollback()
            else:
                conn.commit()

        conn.close()

    def save_data_to_csv(self, data, filename):
        try:
            csv_writer = CSVWriter()
            csv_writer.save_data_to_csv(data, filename)
        except Exception as e:
            logging.error(f"Error saving data to CSV: {e}")

    def handle_captcha(self):
        if self.DEBUG:
            print("CAPTCHA detected. Please solve it manually.")
        self.driver.save_screenshot('captcha.png')
        captcha_url = self.driver.current_url
        print(f"Solve the CAPTCHA here: {captcha_url}")
        input("Press Enter after solving the CAPTCHA...")

    def wait_for_familiar_url(self, familiar_url):
        if self.DEBUG:
            print("Waiting for URL to change from validation URL...")
        WebDriverWait(self.driver, 300).until(lambda d: familiar_url in d.current_url)

    def scrape_token(self, token):
        try:
            self.initialize_driver()
            with sqlite3.connect(self.db.db_path) as conn:
                c = conn.cursor()

                # Query to fetch the link for the token from the database
                c.execute('SELECT link FROM apartments WHERE token = ?', (token,))
                result = c.fetchone()

                if result:
                    url = result[0]
                    self.driver.get(url)
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                    if "captcha" in self.driver.current_url:
                        self.handle_captcha()

                    if self.VALIDATION_URL in self.driver.current_url:
                        self.wait_for_familiar_url(URLs.YAD2_URL.value)

                    data = self.extract_data_from_page()
                    if not data:  # If no data fetched by Selenium, use WebpageAnalyzer
                        data = self.use_webpage_analyzer(url)

                    if self.DEBUG:
                        print("Extracted data:", data)

                    self.save_data_to_csv(data, f'yad2_{token}.csv')
                    self.save_data_to_db(data)
                    time.sleep(random_delay() if not self.DEBUG else 1)

                else:
                    print(f"Token '{token}' not found in the database.")

        finally:
            if self.driver:
                self.driver.quit()
            if self.DEBUG:
                print(f"Scraping of token {token} completed")

    def scrape_yad2(self):
        try:
            self.initialize_driver()
            for page_number in range(1, self.TOTAL_PAGES + 1):
                url = f"https://www.yad2.co.il/realestate/forsale?bBox=30.528827%2C32.047508%2C33.169434%2C36.550804&zoom=7&page={page_number}"
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                if "captcha" in self.driver.current_url:
                    self.handle_captcha()

                if self.VALIDATION_URL in self.driver.current_url:
                    self.wait_for_familiar_url(URLs.YAD2_URL.value)

                self.scroll_down()

                data = self.extract_data_from_page()

                # If no data fetched by Selenium, use WebpageAnalyzer
                if not data:
                    data = self.use_webpage_analyzer(url)

                if self.DEBUG:
                    print("Extracted data:", data)

                self.save_data_to_csv(data, 'yad2_data.csv')
                self.save_data_to_db(data)
                time.sleep(random_delay() if not self.DEBUG else 1)

            time.sleep(random_delay() if not self.DEBUG else 1)

        finally:
            if self.driver:
                self.driver.quit()
            if self.DEBUG:
                print("Scraping completed")

    def use_webpage_analyzer(self, url):
        try:
            print("Selenium failed to fetch data. Attempting to analyze with WebpageAnalyzer...")
            analyzer = WebpageAnalyzer(url)
            analysis = analyzer.analyze()
            return analysis
        except Exception as e:
            logging.error(f"Error using WebpageAnalyzer: {e}")
            return []

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    scraper = Scraper()
    scraper.scrape_yad2()
