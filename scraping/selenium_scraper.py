import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from database import db_operations
from enums import Paths, URLs
from utils.helpers import random_delay, get_random_user_agent
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

DEBUG = True
TOTAL_PAGES = 2785
VALIDATION_URL = "https://validate.perfdrive.com/ccb4768f5e2ea98586d13473d71efc83/"  # The URL to detect and pause on

def initialize_driver(additional_options=None):
    options = webdriver.ChromeOptions()
    options.headless = not DEBUG  # Set to False to debug visually; change to True for headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'user-agent={get_random_user_agent()}')  # Set a random user agent
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
    driver = webdriver.Chrome(service=service, options=options)
    
    # Bypass detection
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": get_random_user_agent()})
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def scroll_down(driver):
    SCROLL_PAUSE_TIME = random.uniform(2, 5) if not DEBUG else 1  # Use a random delay for scrolling
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def extract_data_from_page(driver):
    items = driver.find_elements(By.XPATH, "//*[@id='__next']/div/main/div[2]/div/div/div[4]/ul/li/div/div/a/div")
    data_list = []
    for item in items:
        try:
            title = item.find_element(By.CSS_SELECTOR, "h2[data-nagish='content-section-title']").text
        except:
            title = "N/A"

        try:
            price = item.find_element(By.CLASS_NAME, "price_price__xQt90").text
        except:
            price = "N/A"

        try:
            description = item.find_element(By.CLASS_NAME, "item-data-content_itemInfoLine__AeoPP").text
        except:
            description = "N/A"

        try:
            link = item.find_element(By.XPATH, "..").get_attribute("href")
            token = link.split("/item/")[1].split("?")[0]
        except:
            token = "N/A"

        # Skip items without a token or a price
        if token == "N/A" or price == "N/A":
            continue

        date = time.strftime('%Y-%m-%d')

        data_list.append({"title": title, "price": price, "description": description, "date": date, "token": token})
    return data_list

def save_data_to_csv(data):
    with open('C:/Users/Mor/Desktop/test/yad2_scraper/output.csv', 'a', newline='', encoding='utf-8') as file:  # Open file in append mode
        writer = csv.DictWriter(file, fieldnames=['title', 'price', 'description', 'date', 'token'])
        writer.writeheader()
        writer.writerows(data)
        if DEBUG:
            print("Data saved to CSV")

def save_data_to_db(data):
    for item in data:
        db_operations.save_data_to_db(item)
        if DEBUG:
            print("Data saved to DB: ", item)

def handle_captcha(driver):
    """
    Handles CAPTCHA by pausing the script and providing a link to solve it manually.
    
    Args:
        driver (WebDriver): The WebDriver instance.
    """
    if DEBUG:
        print("CAPTCHA detected. Please solve it manually.")
    driver.save_screenshot('captcha.png')  # Save a screenshot of the CAPTCHA
    captcha_url = driver.current_url
    print(f"Solve the CAPTCHA here: {captcha_url}")
    input("Press Enter after solving the CAPTCHA...")  # Wait for user input after CAPTCHA is solved

def wait_for_familiar_url(driver, familiar_url):
    """
    Waits until the URL changes to a familiar Yad2 URL.
    
    Args:
        driver (WebDriver): The WebDriver instance.
        familiar_url (str): The familiar URL to wait for.
    """
    if DEBUG:
        print("Waiting for URL to change from validation URL...")
    WebDriverWait(driver, 300).until(lambda d: familiar_url in d.current_url)

def scrape_yad2():
    driver = None
    try:
        driver = initialize_driver()
        
        for page_number in range(1, TOTAL_PAGES + 1):
            url = f"https://www.yad2.co.il/realestate/forsale?bBox=30.528827%2C32.047508%2C33.169434%2C36.550804&zoom=7&page={page_number}"
            driver.get(url)
            time.sleep(random_delay() if not DEBUG else 1)  # Wait for the page to load
            
            # Check for CAPTCHA and handle it
            if "captcha" in driver.current_url:
                handle_captcha(driver)

            # Check for validation URL and wait until it changes back
            if VALIDATION_URL in driver.current_url:
                wait_for_familiar_url(driver, URLs.YAD2_URL.value)

            scroll_down(driver)

            data = extract_data_from_page(driver)
            if DEBUG:
                print("Extracted data:", data)
            
            save_data_to_csv(data)
            save_data_to_db(data)
            time.sleep(random_delay() if not DEBUG else 1)  # Wait for some time to mimic human behavior
        
        time.sleep(random_delay() if not DEBUG else 1)  # Wait for some time to mimic human behavior

    finally:
        if driver:
            driver.quit()
        if DEBUG:
            print("Scraping completed")

if __name__ == "__main__":
    scrape_yad2()
