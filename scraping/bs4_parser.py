from bs4 import BeautifulSoup

def parse_html(html):
    """
    Parses the HTML content and extracts the relevant information.

    Args:
        html (str): The HTML content of the page.

    Returns:
        list: A list of dictionaries containing the title, price, and description of each listing.
    """
    soup = BeautifulSoup(html, 'html.parser')
    listings = soup.find_all(class_='listing')

    extracted_data = []

    for listing in listings:
        title_element = listing.find('h2', {'data-nagish': 'content-section-title'})
        price_element = listing.find(class_='price_price__xQt90')
        description_element = listing.find(class_='item-data-content_itemInfoLine__AeoPP')

        if title_element and price_element and description_element:
            title = title_element.get_text(strip=True)
            price = price_element.get_text(strip=True)
            description = description_element.get_text(strip=True)

            extracted_data.append({
                'title': title,
                'price': price,
                'description': description
            })

    return extracted_data
