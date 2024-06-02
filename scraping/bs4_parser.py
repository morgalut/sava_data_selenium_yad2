from bs4 import BeautifulSoup

def parse_html(html, selectors):
    """
    Parses the HTML content and extracts the relevant information.

    Args:
        html (str): The HTML content of the page.
        selectors (dict): A dictionary containing the CSS selectors for the elements to be extracted.

    Returns:
        list: A list of dictionaries containing the title, price, and description of each listing.
    """
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.select(selectors['listing'])

    extracted_data = []

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
                'description': description
            })

    return extracted_data
