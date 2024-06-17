import csv
import os
from datetime import datetime
import logging

class CSVWriter:
    BASE_PATH = "C:\\Users\\Mor\\Desktop\\test\\yad2_scraper\\database"

    @staticmethod
    def save_data_to_csv(data, filename):
        fieldnames = ['title', 'price', 'description', 'date', 'token', 'hour', 'link']
        file_path = os.path.join(CSVWriter.BASE_PATH, filename)
        write_header = not os.path.exists(file_path)
        
        try:
            with open(file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if write_header:
                    writer.writeheader()
                for item in data:
                    if isinstance(item, dict):
                        item['date'] = item.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        logging.warning(f"Expected dictionary, got {type(item)}: {item}")
                writer.writerows(data)
                logging.debug(f"Data saved to CSV: {file_path}")
        except Exception as e:
            logging.error(f"Error saving data to CSV: {e}")
