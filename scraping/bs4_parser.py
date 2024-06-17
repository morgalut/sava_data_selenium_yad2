from datetime import datetime
from bs4 import BeautifulSoup
from enum import Enum
import re

class Selectors(Enum):
    LISTING = 'div.upper-item-description_upperDescriptionBox__zG69c'
    TITLE = 'h1.heading_heading__SB617'
    PRICE = 'span.price_price__xQt90'
    DESCRIPTION = 'h2.address_address__CNi30'
    TOKEN = 'a[data-testid="link"]'
    BUILDING_ITEM = 'div.building-item_itemValue__2jk14'
    DESCRIPTION_TEXT = 'div.description_description__l3oun'

class Parser:
    @staticmethod
    def parse_html(html: str, agent_names: list) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        listings = soup.select(Selectors.LISTING.value)
        current_date = datetime.now().strftime('%Y-%m-%d')
        agent_results = {agent: {'found': False, 'details': []} for agent in agent_names}

        for listing in listings:
            title = Parser.extract_text(listing, Selectors.TITLE)
            price = Parser.extract_text(listing, Selectors.PRICE)
            description = Parser.extract_text(listing, Selectors.DESCRIPTION)
            token = Parser.extract_token(listing)
            building_item = Parser.extract_text(listing, Selectors.BUILDING_ITEM)
            description_text = Parser.extract_text(listing, Selectors.DESCRIPTION_TEXT)

            if title and price and description and token:
                listing_data = {
                    'title': title,
                    'price': price,
                    'description': description,
                    'date': current_date,
                    'token': token,
                    'building_item': building_item,
                    'description_text': description_text
                }
                
                for agent in agent_names:
                    if re.search(agent, str(listing), re.IGNORECASE):
                        agent_results[agent]['found'] = True
                        agent_results[agent]['details'].append(listing_data)
        
        return agent_results

    @staticmethod
    def extract_text(listing, selector: Selectors) -> str:
        element = listing.select_one(selector.value)
        return element.get_text(strip=True) if element else None

    @staticmethod
    def extract_token(listing) -> str:
        element = listing.select_one(Selectors.TOKEN.value)
        if element and 'href' in element.attrs:
            return element['href'].split("/item/")[1].split("?")[0]
        return None

if __name__ == "__main__":
    html = '''HTML content here'''
    agent_names = ['Agent Smith', 'Agent Johnson', 'Agent Brown']
    parser = Parser()
    data = parser.parse_html(html, agent_names)
    for agent, details in data.items():
        print(f"Agent: {agent}")
        print(f"Found: {details['found']}")
        if details['found']:
            print("Details:")
            for detail in details['details']:
                print(detail)
        print()
