"""Fill the CSV files with sample data: 20 owners, 24 pets and 25 appointments.

How to run: python sample_data.py

Every record goes through the program's own validate() and add(),
so the sample data follows the same rules as data typed in by a user.
The script only runs when all three files are empty, so it never
duplicates or overwrites real records.
"""

from main import DATA_DIRECTORY, SAVE_FAILED, load_all
from clinic.managers import AppointmentManager, OwnerManager, PetManager

# One entry per owner: (name, phone, pets)
# Each pet: (pet name, species, [(date, time, reason), ...])
SAMPLE_DATA = [
    ("Somchai Jaidee", "0812345678", [
        ("Mochi", "Cat", [("2026-12-01", "09:00", "Annual vaccination"),
                          ("2026-12-15", "09:00", "Booster shot")]),
        ("Lucky", "Dog", [("2026-12-01", "10:30", "Skin rash check")]),
    ]),
    ("Malee Srisuk", "0898765432", [
        ("Pudding", "Rabbit", [("2026-12-02", "13:00", "Dental cleaning")]),
    ]),
    ("Anan Wongdee", "021234567", [
        ("Max", "Dog", [("2026-12-03", "15:30", "Follow-up after surgery")]),
    ]),
    ("Pranee Chaiyo", "0861112233", [
        ("Snow", "Cat", [("2026-12-04", "09:30", "Vaccination")]),
    ]),
    ("Kittipong Saelim", "0823344556", [
        ("Bobby", "Dog", [("2026-12-04", "11:00", "Ear infection")]),
        ("Coco", "Dog", [("2026-12-04", "11:30", "Nail trimming")]),
    ]),
    ("Siriporn Thongdee", "0835566778", [
        ("Nemo", "Fish", [("2026-12-05", "10:00", "Fin rot check")]),
    ]),
    ("Wichai Rattanakul", "0847788990", [
        ("Tiger", "Cat", [("2026-12-05", "14:00", "Neutering")]),
    ]),
    ("Nattaya Boonmee", "0859900112", [
        ("Kiwi", "Bird", [("2026-12-07", "09:00", "Beak check")]),
    ]),
    ("Prasert Kaewmanee", "0611223344", [
        ("Rocky", "Dog", [("2026-12-07", "13:30", "Limping")]),
        ("Bella", "Dog", [("2026-12-08", "10:30", "Vaccination")]),
    ]),
    ("Kanokwan Sukjai", "0622334455", [
        ("Milo", "Cat", [("2026-12-08", "15:00", "Weight check")]),
    ]),
    ("Thanawat Phromma", "0633445566", [
        ("Shell", "Turtle", [("2026-12-09", "09:00", "Shell care")]),
    ]),
    ("Duangjai Inthara", "0644556677", [
        ("Luna", "Cat", [("2026-12-09", "11:30", "Dental cleaning")]),
    ]),
    ("Somsak Pansri", "0655667788", [
        ("Buddy", "Dog", [("2026-12-10", "10:00", "Skin allergy")]),
    ]),
    ("Arunee Wattana", "0666778899", [
        ("Hammy", "Hamster", [("2026-12-10", "16:00", "General check-up")]),
    ]),
    ("Chaiwat Somboon", "0677889900", [
        ("Simba", "Cat", [("2026-12-11", "09:30", "Deworming")]),
        ("Nala", "Cat", [("2026-12-11", "10:00", "Deworming")]),
    ]),
    ("Pimchanok Rungroj", "0688990011", [
        ("Oreo", "Rabbit", [("2026-12-14", "14:30", "Teeth trimming")]),
    ]),
    ("Narong Khamphan", "0699001122", [
        ("Duke", "Dog", [("2026-12-14", "16:00", "Vaccination")]),
    ]),
    ("Supaporn Meesuk", "0911223344", [
        ("Ginger", "Cat", [("2026-12-16", "10:30", "Eye infection")]),
    ]),
    ("Jirawat Thongchai", "0922334455", [
        ("Charlie", "Dog", [("2026-12-16", "13:00", "Annual check-up")]),
    ]),
    ("Waraporn Saengdao", "0933445566", [
        ("Peanut", "Guinea pig", [("2026-12-17", "11:00", "Weight loss")]),
    ]),
]


def add_record(manager, data):
    """Validate data, create a new ID, then add and save the record.

    Returns the new object, or None if the data is invalid or could not be saved.
    """
    errors = manager.validate(data)
    if errors:
        print(f"Skipped {data}: {', '.join(errors)}")
        return None

    item = manager.item_from_data(manager.next_id(), data)
    if not manager.add(item):
        print(SAVE_FAILED)
        return None
    return item


def create_sample_data():
    # Create and link the Managers the same way main() does
    owner_manager = OwnerManager(DATA_DIRECTORY / "owners.csv")
    pet_manager = PetManager(DATA_DIRECTORY / "pets.csv", owner_manager)
    appointment_manager = AppointmentManager(DATA_DIRECTORY / "appointments.csv", pet_manager)
    owner_manager.pet_manager = pet_manager
    pet_manager.appointment_manager = appointment_manager

    managers = [owner_manager, pet_manager, appointment_manager]
    # Same loading and checking as main(): stop if any file is broken
    if not load_all(managers):
        return

    # Never mix sample data with records that are already there
    if any(manager.items for manager in managers):
        print("The data files already contain records. Empty them first to load sample data.")
        return

    for owner_name, phone, pets in SAMPLE_DATA:
        owner = add_record(owner_manager, {"name": owner_name, "phone": phone})
        if owner is None:
            return

        for pet_name, species, appointments in pets:
            # The owner ID comes from the owner just created, e.g. OW001
            pet = add_record(pet_manager, {
                "name": pet_name,
                "species": species,
                "owner_id": owner.owner_id,
            })
            if pet is None:
                return

            for date, time, reason in appointments:
                appointment = add_record(appointment_manager, {
                    "pet_id": pet.pet_id,
                    "date": date,
                    "time": time,
                    "reason": reason,
                })
                if appointment is None:
                    return

    print(f"Added {len(owner_manager.items)} owners, {len(pet_manager.items)} pets "
          f"and {len(appointment_manager.items)} appointments.")


if __name__ == "__main__":
    create_sample_data()
