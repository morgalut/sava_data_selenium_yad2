import csv
import os
from logging import DEBUG
from enums import Paths

class CSVWriter:
    @staticmethod
    def save_data_to_csv(data):
        fieldnames = ['title', 'price', 'description', 'date', 'token']
        file_path = Paths.BASE_PATH.value + '/output.csv'
        write_header = not os.path.exists(file_path)
        with open(file_path, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(data)
            if DEBUG:
                print("Data saved to CSV")
