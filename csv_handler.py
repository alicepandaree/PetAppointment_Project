import csv
import os
from pathlib import Path

"""
# utf-8-sig adds a BOM (3 hidden bytes) at the start of the file, so Excel
# knows it is UTF-8. The program accepts English text only, but the BOM is
# kept because: the existing CSV files already start with a BOM, and reading with utf-8-sig removes it (plain utf-8 would leave it stuck to the 
# first column name, so the header check would fail)
# reading with utf-8-sig works for files with or without a BOM
# Reading and writing share this value, so change it here only.
"""

ENCODING = "utf-8-sig" 

class CSVHandler:
    def __init__(self, file_path, fieldnames):
        self.file_path = Path(file_path)
        self.fieldnames = fieldnames

    def read_all(self):
        if not self.file_path.exists():
            self.write_all([])
            return []
        try:
            with open(self.file_path, mode='r', encoding=ENCODING, newline='') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception:
            return []

    def write_all(self, rows):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, mode='w', encoding=ENCODING, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                return True
        except PermissionError:
            return False
