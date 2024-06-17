"""Module to run the Yad2 scraping application."""

from scraping.selenium_scraper import Scraper
from database.db_operations import Database

class App:
    """Class to manage the application."""

    def __init__(self):
        """Initialize the App class."""
        self.db = Database()
        self.scraper = Scraper()

    def run(self):
        """Run the application."""
        # Create the database tables
        self.db.create_tables()

        # Prompt the user for scraping options
        scrape_choice = input("Enter 'all' to scrape all data or enter a specific token "
                              "to scrape data for that token: ")

        if scrape_choice.lower() == 'all':
            # Scrape data from Yad2
            self.scraper.scrape_yad2()
        else:
            # Scrape data for a specific token
            self.scraper.scrape_token(scrape_choice)

        # Prompt the user to view price trends
        token = input("Enter token to view price trends (or type 'exit' to quit): ")
        while token.lower() != 'exit':
            self.db.view_price_trends(token)
            token = input("Enter another token to view price trends (or type 'exit' to quit): ")

if __name__ == "__main__":
    app = App()
    app.run()
