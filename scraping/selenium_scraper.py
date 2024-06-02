import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from database import db_operations
from enums import Paths
from utils.helpers import random_delay, get_random_user_agent
from selenium.webdriver.chrome.service import Service

def initialize_driver(additional_options=None):
    """
    Initializes the Chrome WebDriver with the specified options.

    Args:
        additional_options (list, optional): Additional options to add to the WebDriver.

    Returns:
        WebDriver: The initialized WebDriver instance.
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # Disable sandbox mode (Linux only)
    options.add_argument('--disable-dev-shm-usage')  # Disable sharing /dev/shm (Linux only)
    options.add_argument(f'user-agent={get_random_user_agent()}')  # Set a random user agent

    if additional_options:
        for option in additional_options:
            options.add_argument(option)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scroll_down(driver):
    """
    Scrolls down the page to load more content.

    Args:
        driver (WebDriver): The WebDriver instance.
    """
    SCROLL_PAUSE_TIME = random.uniform(2, 5)  # Use a random delay for scrolling
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_real_estate_section(driver):
    """
    Clicks the real estate section button to navigate to the listings.

    Args:
        driver (WebDriver): The WebDriver instance.
    """
    real_estate_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'נדלן')]")))
    real_estate_button.click()
    time.sleep(random_delay())  # Wait for the page to load

def get_next_page(driver):
    """
    Navigates to the next page of listings.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        bool: True if the next page was successfully loaded, False otherwise.
    """
    try:
        next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'הבא')]")
        if next_button.get_attribute('disabled'):
            return False
        next_button.click()
        time.sleep(random_delay())  # Wait for the page to load
        return True
    except:
        return False

def extract_data_from_page(driver):
    """
    Extracts data from the current page using the provided XPath.

    Args:
        driver (WebDriver): The WebDriver instance.

    Returns:
        list: A list of dictionaries containing the title, price, and description of each listing.
    """
    items = driver.find_elements(By.XPATH, "//*[@id='__next']/div/main/div[2]/div/div/div[4]/ul/li/div/div/a/div")
    data_list = []
    for item in items:
        title = item.find_element(By.CSS_SELECTOR, "h2[data-nagish='content-section-title']").text
        price = item.find_element(By.CLASS_NAME, "price_price__xQt90").text
        description = item.find_element(By.CLASS_NAME, "item-data-content_itemInfoLine__AeoPP").text
        data_list.append({"title": title, "price": price, "description": description})
    return data_list

def save_data_to_csv(data):
    """
    Saves the extracted data to a CSV file.

    Args:
        data (list): The list of extracted data.
    """
    with open('data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['title', 'price', 'description'])
        writer.writeheader()
        writer.writerows(data)

def save_data_to_db(data):
    """
    Saves the extracted data to the database.

    Args:
        data (list): The list of extracted data.
    """
    for item in data:
        db_operations.save_data_to_db(item)

def scrape_yad2():
    """
    Scrapes the Yad2 website for real estate listings.
    """
    driver = None
    try:
        driver = initialize_driver()
        driver.get(Paths.URLs.YAD2_URL.value)
        scroll_down(driver)
        click_real_estate_section(driver)
        data = extract_data_from_page(driver)
        save_data_to_csv(data)
        save_data_to_db(data)
        time.sleep(10)  # Wait for some time to mimic human behavior
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    scrape_yad2()
