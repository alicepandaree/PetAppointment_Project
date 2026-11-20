"""
class that selected all data about Person, Owner, Pet, Appointment
Person -- name, phone
Owner -- owner_id, to_row(), from_row(row)
Pet -- pet_id, species, name, owner_id, to_row(), from_row(row)
Appointment -- appointment_id, pet_id, date, time, reason
# Class ที่เก็บข้อมูล: Person, Owner, Pet, Appointment

Every model uses clean_row() in from_row(), so every CSV file is checked the same way.
"""

def clean_row(row, fieldnames, id_field):
    """Check one row from a CSV file and strip spaces from every value.

    Raises ValueError if the row is broken, so load() can report the row number.
    """
    # csv.DictReader puts extra values under the key None
    if None in row:
        raise ValueError("too many columns")

    values = {}
    for field in fieldnames:
        value = row.get(field)
        # The value is None when the row is shorter than the header
        if value is None:
            raise ValueError(f"missing value in column {field}")
        values[field] = value.strip()

    # A record without an ID cannot be found, edited or deleted
    if not values[id_field]:
        raise ValueError(f"column {id_field} is empty")
    return values


class Person:
    def __init__(self, name : str, phone: str):
        self.name = name
        self.phone = phone


class Owner(Person):
    # Columns of owners.csv, in order. BaseManager passes this to CSVHandler.
    FIELDNAMES = ["owner_id", "name", "phone"]

    def __init__(self, owner_id: str, name: str, phone: str):
        super().__init__(name, phone)    
        self.owner_id = owner_id          

    def to_row(self) -> dict:
        return {
            "owner_id": self.owner_id,
            "name": self.name,
            "phone": self.phone
        }

    @classmethod
    def from_row(cls, row: dict):
        # clean_row checks for missing columns, extra columns and an empty ID
        values = clean_row(row, cls.FIELDNAMES, "owner_id")
        return cls(
            owner_id=values["owner_id"],
            name=values["name"],
            phone=values["phone"]
        ) 

    def __str__ (self):
        return f"ID: {self.owner_id} Name:{self.name} Phone:{self.phone}"

class Pet:
    FIELDNAMES = ["pet_id", "name", "species", "owner_id"]
    def __init__(self, pet_id, name, species, owner_id):#สร้างออบเจ็กต์สัตว์เลี้ยงตัวใหม่
        self.pet_id = pet_id
        self.name = name
        self.species = species
        self.owner_id = owner_id

    def to_row(self):#แปลงออบเจ็กต ให้เป็นdict เพื่อเซฟไฟล์ CSV
        row_data = {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "owner_id": self.owner_id
        }
        return row_data

    @classmethod
    def from_row(cls, row) :#ปลงข้อมูลdict1 แถวที่อ่านจากไฟล์ CSV กลับมาสร้างเป็นออบเจ็กต์
        # Same checks as Owner and Appointment: missing/extra columns and an empty ID
        cleaned = clean_row(row, cls.FIELDNAMES, "pet_id")
        return cls(
            pet_id=cleaned["pet_id"],
            name=cleaned["name"],
            species=cleaned["species"],
            owner_id=cleaned["owner_id"]
        )
    def __str__(self):#กำหนดรูปแบบข้อความที่่รันออกมาทางหน้าจอ
        return f"{self.pet_id} | Name: {self.name} | Species: {self.species} | Owner: {self.owner_id}"


class Appointment:
    FIELDNAMES = ["appointment_id", "pet_id", "date", "time", "reason"]

    def __init__(self, appointment_id, pet_id, date, time, reason):
        self.appointment_id = appointment_id
        self.pet_id = pet_id
        self.date = date
        self.time = time
        self.reason = reason

    def to_row(self):
        return {
            "appointment_id": self.appointment_id,
            "pet_id": self.pet_id,
            "date": self.date,
            "time": self.time,
            "reason": self.reason,
        }

    @classmethod
    def from_row(cls, row):
        values = clean_row(row, cls.FIELDNAMES, "appointment_id")
        return cls(
            values["appointment_id"],
            values["pet_id"],
            values["date"],
            values["time"],
            values["reason"],
        )

    def __str__(self):
        return (
            f"{self.appointment_id} | Pet ID: {self.pet_id} | date: {self.date} "
            f"| time: {self.time} | reason: {self.reason}"
        )
