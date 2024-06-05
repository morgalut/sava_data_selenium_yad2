from bs4 import BeautifulSoup
from datetime import datetime

def parse_html(html, selectors):
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.select(selectors['listing'])

    extracted_data = []
    current_date = datetime.now().strftime('%Y-%m-%d')

    for listing in listings:
        title_element = listing.select_one(selectors['title'])
        price_element = listing.select_one(selectors['price'])
        description_element = listing.select(selectors['description'])

        if title_element and price_element and description_element:
            title = title_element.get_text(strip=True)
            price = price_element.get_text(strip=True)
            description = ' • '.join([desc.get_text(strip=True) for desc in description_element])

            extracted_data.append({
                'title': title,
                'price': price,
                'description': description,
                'date': current_date
            })

    return extracted_data
