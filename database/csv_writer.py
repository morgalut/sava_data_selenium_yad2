import csv
import os
import logging

class CSVWriter:
    CSV_DIR = "csv_data"

    def __init__(self):
        os.makedirs(self.CSV_DIR, exist_ok=True)

    def save_data_to_csv(self, data, filename):
        csv_file_path = os.path.join(self.CSV_DIR, filename)
        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
        except Exception as e:
            logging.error(f"Error saving data to CSV: {e}")
            raise
