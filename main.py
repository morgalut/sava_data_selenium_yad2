from scraping.selenium_scraper import Scraper
from database.db_operations import Database
from enums import MenuChoice

class App:
    def __init__(self):
        self.scraper = Scraper(debug=True)
        self.db = Database()
        self.db.create_database()

    def run(self):
        while True:
            print("Menu:")
            print("1. Scrape all")
            print("2. Scrape token")
            print("3. Display data")
            print("4. Exit")
            choice = input("Enter your choice: ")
            if choice == MenuChoice.ALL.value:
                self.scrape_all()
            elif choice == MenuChoice.TOKEN.value:
                token = input("Enter the token to scrape: ")
                self.scrape_token(token)
            elif choice == MenuChoice.DISPLAY.value:
                token = input("Enter the token to display: ")
                self.display_data(token)
            elif choice == MenuChoice.EXIT.value:
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please select a valid option.")

    def scrape_all(self):
        for page_number in range(1, self.scraper.TOTAL_PAGES + 1):
            self.scraper.scrape_page(page_number)

    def scrape_token(self, token):
        self.scraper.scrape_token(token)

    def display_data(self, token):
        self.db.display_price_trends(token)

if __name__ == '__main__':
    app = App()
    app.run()
