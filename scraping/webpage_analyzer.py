import logging
from datetime import datetime
from enum import Enum
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Status(Enum):
    SUCCESS = 1
    FAILURE = 2

class Selectors(Enum):
    TITLE = 'h1.heading_heading__SB617'
    PRICE = 'span.price_price__xQt90'
    DESCRIPTION = 'h2.address_address__CNi30'
    BUILDING_DETAILS = 'div.building-details_buildingDetailsBox__5cGqB'
    DESCRIPTION_TEXT = 'p.description_description__l3oun'
    BUILDING_ITEM = 'div.building-item_itemValue__2jk14'
    ITEM_CONTENT = 'div.item-data-content_itemDataContentBox__gvAC2'

class WebpageAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.current_date = datetime.now().strftime('%Y-%m-%d')
    
    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Uncomment to run headlessly
        service = Service('/path/to/chromedriver')  # Specify path to chromedriver executable
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def fetch_content(self):
        try:
            logging.info(f"Fetching content from URL: {self.url}")
            self.driver.get(self.url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            return Status.SUCCESS
        except Exception as e:
            logging.error(f"Failed to fetch the webpage: {e}")
            return Status.FAILURE

    def extract_data(self):
        if not self.driver:
            self.setup_driver()

        status = self.fetch_content()
        if status == Status.FAILURE:
            return {}

        data = {}
        for selector in Selectors:
            element = self.driver.find_element(By.CSS_SELECTOR, selector.value)
            data[selector.name.lower()] = element.text.strip() if element else 'N/A'

        return data

    def analyze(self):
        try:
            data = self.extract_data()
            return data
        except Exception as e:
            logging.error(f"An error occurred during analysis: {e}")
            return {}

# Usage example
if __name__ == "__main__":
    url = input("Enter the URL to analyze: ")
    analyzer = WebpageAnalyzer(url)
    analysis = analyzer.analyze()
    print(analysis)
