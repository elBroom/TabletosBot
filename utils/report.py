import csv

from transliterate import translit


def make_csv_file(filename, history):
    with open(filename, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'name', 'dosage'])
        for hst in history:
            writer.writerow(list(convert_data([hst.datetime, hst.name, hst.dosage.replace(',', '.')])))


def convert_data(data: list):
    for row in data:
        yield translit(row, 'ru', reversed=True)
