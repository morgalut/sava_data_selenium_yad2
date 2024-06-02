from scraping.selenium_scraper import initialize_driver, get_next_page, scrape_yad2
from scraping.bs4_parser import parse_html
from database.db_operations import save_data_to_db, create_tables
from scraping.csv_writer import write_to_csv

def main():
    url = "https://www.yad2.co.il/realestate/forsale"

    # Create database tables if they don't exist
    create_tables()

    all_items = []

    selectors = {
        'listing': 'div.item-data-content_itemDataContentBox__gvAC2',
        'title': 'h2[data-nagish="content-section-title"] span.item-data-content_heading__tphH4',
        'price': 'span.price_price__xQt90',
        'description': 'span.item-data-content_itemInfoLine__AeoPP'
    }

    try:
        with initialize_driver() as driver:
            print("Driver initialized successfully.")
            driver.get(url)
            print("Navigated to real estate section.")
            page_source = driver.page_source
            
            while page_source:
                items = parse_html(page_source, selectors)
                all_items.extend(items)
                
                if not get_next_page(driver):  # Update get_next_page to return False if no next page
                    break
                page_source = driver.page_source

        # Write all scraped items to a CSV file
        write_to_csv(all_items)
        print("Data written to CSV successfully.")
        
        # Save all scraped items to the database
        for item in all_items:
            save_data_to_db(item)
        print("Data saved to database successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == "__main__":
    main()
