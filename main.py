# main.py

from scraping.selenium_scraper import Scraper
from database.db_operations import Database
from queue import Queue
import threading

from enums import MenuChoice

class App:
    def __init__(self):
        self.db = Database()
        self.db.create_database()
        self.queue = Queue()
        self.num_threads = 5  # Number of threads to use, adjust based on your system's capabilities

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
        threads = []
        for page_number in range(1, Scraper.TOTAL_PAGES + 1):
            self.queue.put(page_number)

        for _ in range(self.num_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            threads.append(thread)

        self.queue.join()

        for thread in threads:
            self.queue.put(None)  # Signal the threads to exit
        for thread in threads:
            thread.join()

    def worker(self):
        scraper = Scraper(debug=True)
        while True:
            page_number = self.queue.get()
            if page_number is None:
                scraper.close_driver()
                break
            try:
                scraper.scrape_page(page_number)
            except Exception as e:
                print(f"Error scraping page {page_number}: {e}")
            finally:
                self.queue.task_done()

    def scrape_token(self, token):
        scraper = Scraper(debug=True)
        scraper.scrape_token(token)
        scraper.close_driver()

    def display_data(self, token):
        self.db.display_price_trends(token)

if __name__ == '__main__':
    app = App()
    app.run()
