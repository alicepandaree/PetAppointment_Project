"""
# Alice -- BaseManager, AppointmentManager
# Pakbung -- OwnerManager
# Ruangkhaow -- PetManager

Manager classes: BaseManager and one Manager for each kind of record.

BaseManager holds the methods every kind of record shares: load, save, add, update, delete and search. 
OwnerManager, PetManager and AppointmentManager inherit them and write only what differs:
prompt_data, validate, item_from_data and can_delete.
"""

from datetime import datetime

from .csv_handler import CSVHandler
from .models import Appointment, Owner, Pet


def ask(label, current_value = None):
    """Ask the user for one value.

    When adding, current_value is None, so the question is asked as usual.
    When editing, the old value is shown in [ ]; pressing Enter keeps it.
    """
    if current_value is None:
        return input(f"{label}: ").strip()
    value = input(f"{label} [{current_value}]: ").strip()
    return value if value else current_value


def is_valid_datetime(value, fmt):
    """Check that value matches fmt and is a real date or time.

    strptime turns the text into a datetime and raises ValueError if the
    format is wrong or the date does not exist. strftime turns it back into
    text, which is compared with the original to require leading zeros:
    "2026-1-5" becomes "2026-01-05", which does not match, so it fails.
    """
    try:
        return datetime.strptime(value, fmt).strftime(fmt) == value
    except ValueError:
        return False


class BaseManager:
    # Child classes must set these values
    title = ""          # name shown in the menu, e.g. "Owners"
    item_class = None   # data class, e.g. Owner
    id_field = ""       # ID column, e.g. "owner_id"
    prefix = ""         # ID prefix, e.g. "OW"

    def __init__(self, file_path):
        self.items = []   # every record, kept in memory
        self.csv_handler = CSVHandler(file_path, self.item_class.FIELDNAMES)

    def get_id(self, item):
        """Return the ID of item. Works for every class because it reads to_row()."""
        return item.to_row()[self.id_field]

    def find_index(self, item_id):
        """Return the position of a record in self.items, or None if not found."""
        for index, item in enumerate(self.items):
            if self.get_id(item) == item_id:
                return index
        return None

    def load(self):
        """Load records from the file into self.items. Returns True on success."""
        rows = self.csv_handler.read_all()
        if rows is None:
            return False

        self.items = []
        # Row 1 of the file is the header, so data starts at row 2
        for row_number, row in enumerate(rows, start=2):
            try:
                self.items.append(self.item_class.from_row(row))
            except ValueError as error:
                # Stop here: skipping the row would delete it on the next save
                print(f"{self.csv_handler.file_path.name} row {row_number} is invalid: {error}")
                return False
        return True

    def save(self):
        """Write every record in self.items to the file. Returns True on success."""
        rows = [item.to_row() for item in self.items]
        return self.csv_handler.write_all(rows)

    def next_id(self):
        """Create a new ID: the highest existing number plus one (OW002 -> OW003)."""
        max_number = 0
        for item in self.items:
            suffix = self.get_id(item)[len(self.prefix):]   # remove the prefix, keep the number
            if suffix.isdigit() and int(suffix) > max_number:
                max_number = int(suffix)
        # :03d pads with zeros to 3 digits, e.g. 3 becomes 003
        return f"{self.prefix}{max_number + 1:03d}"

    def find_by_id(self, item_id):
        """Find a record by ID. Returns the object, or None if not found."""
        result = None
        for item in self.items:
            if self.get_id(item) == item_id:
                result = item
                break   # found it, no need to keep looking
        return result

    def add(self, item):
        """Add a record and save. If saving fails, remove the record again."""
        self.items.append(item)
        saved = self.save()
        if not saved:
            # Roll back so the records in memory match the file
            self.items.remove(item)
        return saved

    def update(self, item_id, data):
        """Replace a record with new data. If saving fails, put the old record back."""
        saved = False
        index = self.find_index(item_id)
        if index is not None:
            old_item = self.items[index]   # kept in case we need to roll back
            self.items[index] = self.item_from_data(item_id, data)
            saved = self.save()
            if not saved:
                self.items[index] = old_item
        return saved

    def delete(self, item_id):
        """Delete a record and save. If saving fails, put the record back in place."""
        saved = False
        index = self.find_index(item_id)
        if index is not None:
            old_item = self.items.pop(index)   # removed and kept in case we need to roll back
            saved = self.save()
            if not saved:
                self.items.insert(index, old_item)
        return saved

    def search(self, keyword):
        """Search every column, ignoring upper and lower case."""
        results = []
        keyword = keyword.lower()
        for item in self.items:
            # Join all values into one text, so ID, name, phone etc. are all searched
            text = " ".join(item.to_row().values()).lower()
            if keyword in text:
                results.append(item)
        return results

    def can_delete(self, item_id):
        """Check whether a record may be deleted. Returns (allowed, reason).

        By default every record may be deleted. Child classes with rules override this.
        """
        return True, ""

    # Child classes must write the methods below.
    # If one is missing, NotImplementedError is raised as soon as it is called.
    def prompt_data(self, current=None):
        """Ask the user for the record's values. Returns a dict."""
        raise NotImplementedError

    def validate(self, data, exclude_id=None):
        """Check the data. Returns a list of error messages; an empty list means valid."""
        raise NotImplementedError

    def item_from_data(self, item_id, data):
        """Create an object from an ID and the dict from prompt_data()."""
        raise NotImplementedError


class OwnerManager(BaseManager):
    title = "Owners"
    item_class = Owner
    id_field = "owner_id"
    prefix = "OW"

    def __init__(self, file_path):
        super().__init__(file_path)
        # Set later by main(), because PetManager is created after OwnerManager
        self.pet_manager = None

    def prompt_data(self, current=None):
        # current is None when adding, and the existing Owner when editing
        return {
            "name": ask("Owner name", current.name if current else None),
            "phone": ask("Phone number", current.phone if current else None),
        }

    def validate(self, data, exclude_id=None):
        errors = []
        if not data["name"]:
            errors.append("Please enter a name.")
        phone = data["phone"]
        # isascii() rejects Thai digits such as ๐๘๑, which isdigit() accepts
        if not (phone.isascii() and phone.isdigit() and 9 <= len(phone) <= 10):
            errors.append("Invalid phone number.")
        return errors

    def item_from_data(self, item_id, data):
        return Owner(item_id, data["name"], data["phone"])

    def can_delete(self, item_id):
        # An owner who still has pets cannot be deleted,
        # otherwise those pets would refer to an owner that no longer exists
        for pet in self.pet_manager.items:
            if pet.owner_id == item_id:
                return False, "This owner still has pets."
        return True, ""

# ruangkhaow
class PetManager(BaseManager):
    title = "Pets"
    item_class = Pet
    id_field = "pet_id"
    prefix = "PT"

    def __init__(self, file_path, owner_manager):
        super().__init__(file_path)
        self.owner_manager = owner_manager   # used to check that the owner ID exists
        # Set later by main(), because AppointmentManager is created after PetManager
        self.appointment_manager = None

    def prompt_data(self, current=None):
        return {
            "name": ask("Pet name", current.name if current else None),
            "species": ask("Species", current.species if current else None),
            "owner_id": ask("Owner ID", current.owner_id if current else None),
        }

    def validate(self, data, exclude_id=None):
        errors = []
        if not data["name"]:
            errors.append("Please enter the pet's name.")
        if not data["species"]:
            errors.append("Please enter the species.")
        # Every pet must belong to an owner in the system
        if self.owner_manager.find_by_id(data["owner_id"]) is None:
            errors.append("Owner ID not found.")
        return errors

    def item_from_data(self, item_id, data):
        return Pet(item_id, data["name"], data["species"], data["owner_id"])

    def can_delete(self, item_id):
        # A pet that still has appointments cannot be deleted
        for appointment in self.appointment_manager.items:
            if appointment.pet_id == item_id:
                return False, "This pet still has appointments."
        return True, ""


class AppointmentManager(BaseManager):
    title = "Appointments"
    item_class = Appointment
    id_field = "appointment_id"
    prefix = "AP"

    def __init__(self, file_path, pet_manager):
        super().__init__(file_path)
        self.pet_manager = pet_manager   # used to check that the pet ID exists

    def prompt_data(self, current=None):
        return {
            "pet_id": ask("Pet ID", current.pet_id if current else None),
            "date": ask("Date (YYYY-MM-DD)", current.date if current else None),
            "time": ask("Time (HH:MM)", current.time if current else None),
            "reason": ask("Reason", current.reason if current else None),
        }

    def validate(self, data, exclude_id=None):
        """exclude_id is used when editing, so an appointment does not clash with itself."""
        errors = []
        if self.pet_manager.find_by_id(data["pet_id"]) is None:
            errors.append("Pet ID not found.")

        date_confirmed = is_valid_datetime(data["date"], "%Y-%m-%d")
        time_confirmed = is_valid_datetime(data["time"], "%H:%M")
        if not date_confirmed:
            errors.append("Invalid date.")
        if not time_confirmed:
            errors.append("Invalid time.")

        # Check for a clash only when both date and time are valid
        if date_confirmed and time_confirmed:
            for appointment in self.items:
                same_slot = appointment.date == data["date"] and appointment.time == data["time"]
                if same_slot and appointment.appointment_id != exclude_id:
                    errors.append("This date and time is already booked.")
                    break   # one clash is enough
        return errors

    def item_from_data(self, item_id, data):
        return Appointment(item_id, data["pet_id"], data["date"], data["time"], data["reason"])
