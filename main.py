from scraping.selenium_scraper import scrape_yad2
from database.db_operations import create_tables

def main():
    # Create database tables if they don't exist
    create_tables()
    
    # Start the scraping process
    scrape_yad2()

if __name__ == "__main__":
    main()
