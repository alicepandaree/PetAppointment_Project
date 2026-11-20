"""
Read and write CSV files.
One CSVHandler looks after one file, so each Manager has its own CSVHandler.
"""

import csv
from pathlib import Path

# utf-8-sig adds a BOM (3 hidden bytes) at the start of the file, so Excel
# knows it is UTF-8. The program accepts English text only, but the BOM is
# kept because:
#   - existing CSV files may already start with a BOM, and reading with
#     utf-8-sig removes it (plain utf-8 would leave it stuck to the first
#     column name, so the header check would fail)
#   - reading with utf-8-sig works for files with or without a BOM
# Reading and writing share this value, so change it here only.

ENCODING = "utf-8-sig"


class CSVHandler:
    def __init__(self, file_path, fieldnames):
        self.file_path = Path(file_path)   # file location, e.g. data/owners.csv
        self.fieldnames = fieldnames       # header the file must have, e.g. Owner.FIELDNAMES

    def read_all(self):
        """Read every row in the file.

        Returns:
            list of dicts -- the file was read; an empty list means it has no records yet
            None          -- the file could not be read or created; the reason is printed

        Keeping these two cases apart matters: if a read error returned [],
        the program would think the file is empty, and the next save would
        overwrite the real records.
        """
        # First run: there is no file yet, so create one with only the header
        if not self.file_path.exists():
            if self.write_all([]):
                return []
            print(f"Cannot create {self.file_path.name}. Please check the data folder.")
            return None

        try:
            # newline='' lets the csv module handle line endings itself
            with open(self.file_path, mode='r', encoding=ENCODING, newline='') as file:
                reader = csv.DictReader(file)   # uses the first row as dict keys
                # The header must match in both names and order,
                # otherwise values would be read into the wrong columns
                if reader.fieldnames != self.fieldnames:
                    print(f"The header of {self.file_path.name} is incorrect.")
                    print("Expected:", ", ".join(self.fieldnames))
                    return None
                return list(reader)
        except PermissionError:
            # Windows locks the file while it is open in Excel
            print(f"Cannot open {self.file_path.name}. Please close it in Excel.")
            return None
        except UnicodeDecodeError:
            # The file was saved from Excel as plain CSV instead of CSV UTF-8
            print(f"Cannot read {self.file_path.name}. Please save it from Excel as CSV UTF-8.")
            return None
        except OSError as error:
            # Any other problem opening the file
            print(f"Cannot read {self.file_path.name}: {error}")
            return None

    def write_all(self, rows):
        """Write the header and every row, replacing the old file.

        rows : list of dicts from to_row()
        Returns True on success, or False if the file cannot be written
        (for example, it is open in Excel).
        """
        try:
            # Create the data folder if needed (exist_ok=True: no error if it exists)
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            # Mode 'w' overwrites the whole file
            with open(self.file_path, mode='w', encoding=ENCODING, newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()     # first row: the header
                writer.writerows(rows)   # following rows: all records
            return True
        except OSError:
            # PermissionError (file open in Excel) is a kind of OSError
            return False
