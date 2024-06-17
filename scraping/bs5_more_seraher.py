import os
from bs4 import BeautifulSoup
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class WebpageAnalyzer:
    def __init__(self, url: str):
        self.url = url
        self.soup = None

    def fetch_content(self):
        try:
            logging.info(f"Fetching content from URL: {self.url}")
            response = requests.get(self.url)
            response.raise_for_status()  # Raise exception for HTTP errors
            self.soup = BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch the webpage: {e}")

    def extract_data(self):
        if not self.soup:
            self.fetch_content()

        data = {
            "title": self.soup.select_one("h1.heading_heading__SB617").get_text(strip=True) if self.soup.select_one("h1.heading_heading__SB617") else None,
            "address": self.soup.select_one("h2.address_address__CNi30").get_text(strip=True) if self.soup.select_one("h2.address_address__CNi30") else None,
            "details": {
                "rooms": self.soup.select_one("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']").get_text(strip=True) if self.soup.select_one("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']") else None,
                "floor": self.soup.select("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']")[1].get_text(strip=True) if len(self.soup.select("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']")) > 1 else None,
                "area": self.soup.select("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']")[2].get_text(strip=True) if len(self.soup.select("div.building-details_buildingDetailsBox__5cGqB span[data-testid='building-text']")) > 2 else None
            },
            "description": self.soup.select_one("p.description_description__l3oun").get_text(strip=True) if self.soup.select_one("p.description_description__l3oun") else None
        }
        return data

    def analyze(self):
        try:
            data = self.extract_data()
            return data
        except Exception as e:
            raise Exception(f"An error occurred during analysis: {e}")

# Example usage
if __name__ == "__main__":
    url = "URL_HERE"  # Replace with the actual URL
    analyzer = WebpageAnalyzer(url)
    
    try:
        analysis = analyzer.analyze()
        print(analysis)
    except Exception as e:
        logging.error(f"Error: {e}")
