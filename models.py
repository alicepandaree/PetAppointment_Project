"""
class that selected all data about Person, Owner, Pet, Appointment
Person -- name, phone
Owner -- owner_id, to_row(), from_row(row)
Pet -- pet_id, species, name, owner_id, to_row(), from_row(row)
Appointment -- appointment_id, pet_id, date, time, reason
# Class ที่เก็บข้อมูล: Person, Owner, Pet, Appointment
"""

def clean_row(row, fieldnames, id_field):
    """ตรวจแถวจาก CSV และตัดช่องว่าง ถ้าแถวเสียจะ raise ValueError"""
    if None in row:
        raise ValueError("จำนวนคอลัมน์เกิน")

    values = {}
    for field in fieldnames:
        value = row.get(field)
        if value is None:
            raise ValueError(f"ไม่มีค่าในคอลัมน์ {field}")
        values[field] = value.strip()

    if not values[id_field]:
        raise ValueError(f"คอลัมน์ {id_field} ว่าง")
    return values


class Person:
    def __init__(self, name : str, phone: str):
        self.name = name
        self.phone = phone


class Owner(Person):
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
    def from_row(cls,row:dict):
        return cls(
            owner_id=row.get("owner_id"),
            name=row.get("name"),
            phone=row.get("phone")
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
        if None in row:
            raise ValueError("Row contains too many columns.")
        cleaned = {}  
        for column in cls.FIELDNAMES :
            value = row.get(column)
            if value is None:
                raise ValueError(f"Missing data in column: '{column}'")
            cleaned[column] = value.strip()
        if cleaned["pet_id"] == "":  
            raise ValueError("Pet ID (pet_id) cannot be empty.")
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