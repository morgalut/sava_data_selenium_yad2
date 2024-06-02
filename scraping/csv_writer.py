# scraping/csv_writer.py

import csv
from enums import Paths

def write_to_csv(data, filename='output.csv'):
    fieldnames = ['title', 'description', 'price', 'image_url']
    with open(Paths.BASE_PATH.value + '/' + filename, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
