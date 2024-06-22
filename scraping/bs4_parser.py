from datetime import datetime
from bs4 import BeautifulSoup
from enum import Enum
import re

import requests

class Selectors(Enum):
    LISTING = 'div.upper-item-description_upperDescriptionBox__zG69c'
    TITLE = 'h1.heading_heading__SB617'
    PRICE = 'span.price_price__xQt90'
    DESCRIPTION = 'h2.address_address__CNi30'
    TOKEN = 'a[data-testid="link"]'
    BUILDING_ITEM = 'div.building-item_itemValue__2jk14'
    DESCRIPTION_TEXT = 'div.description_description__l3oun'

class Parser:
    # Existing methods like parse_html, extract_text, and extract_token remain unchanged

    @staticmethod
    def scrape_apartment_page(url: str) -> dict:
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            title = Parser.extract_text(soup, Selectors.TITLE)
            price = Parser.extract_text(soup, Selectors.PRICE)
            description = Parser.extract_text(soup, Selectors.DESCRIPTION)
            token = Parser.extract_token(soup)
            building_item = Parser.extract_text(soup, Selectors.BUILDING_ITEM)
            description_text = Parser.extract_text(soup, Selectors.DESCRIPTION_TEXT)

            current_date = datetime.now().strftime('%Y-%m-%d')

            if title and price and description and token:
                apartment_data = {
                    'title': title,
                    'price': price,
                    'description': description,
                    'date': current_date,
                    'token': token,
                    'building_item': building_item,
                    'description_text': description_text,
                    'url': url  # Include the URL for reference
                }

                return apartment_data
            else:
                return None

        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    apartment_url = 'https://www.yad2.co.il/realestate/item/1234567'
    apartment_data = Parser.scrape_apartment_page(apartment_url)
    if apartment_data:
        print("Apartment Data:")
        print(apartment_data)
    else:
        print("Failed to scrape apartment data.")