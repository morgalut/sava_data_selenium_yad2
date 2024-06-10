from scraping.selenium_scraper import Scraper
from database.db_operations import Database

class App:
    def __init__(self):
        self.db = Database()
        self.scraper = Scraper()

    def run(self):
        # Create the database tables
        self.db.create_tables()

        # Scrape data from Yad2
        self.scraper.scrape_yad2()

        # Prompt the user to view price trends
        token = input("Enter token to view price trends (or type 'exit' to quit): ")
        while token.lower() != 'exit':
            self.db.view_price_trends(token)
            token = input("Enter another token to view price trends (or type 'exit' to quit): ")

if __name__ == "__main__":
    app = App()
    app.run()
