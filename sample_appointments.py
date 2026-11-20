"""Fill appointments.csv with 25 sample appointments.

How to run: python sample_appointments.py

Needs pets PT001 to PT024 in pets.csv, because every appointment must
belong to a pet that exists. Each appointment goes through the program's
own validate() and add(), so it follows the same rules as user input.
The script only runs when appointments.csv is empty, so it never
duplicates or overwrites real appointments.
"""

from main import DATA_DIRECTORY, SAVE_FAILED, load_all
from clinic.managers import AppointmentManager, OwnerManager, PetManager

# (pet_id, date, time, reason) - IDs AP001 to AP025 are created in this order
SAMPLE_APPOINTMENTS = [
    ("PT001", "2026-12-01", "09:00", "Annual vaccination"),
    ("PT001", "2026-12-15", "09:00", "Booster shot"),
    ("PT002", "2026-12-01", "10:30", "Skin rash check"),
    ("PT003", "2026-12-02", "13:00", "Dental cleaning"),
    ("PT004", "2026-12-03", "15:30", "Follow-up after surgery"),
    ("PT005", "2026-12-04", "09:30", "Vaccination"),
    ("PT006", "2026-12-04", "11:00", "Ear infection"),
    ("PT007", "2026-12-04", "11:30", "Nail trimming"),
    ("PT008", "2026-12-05", "10:00", "Fin rot check"),
    ("PT009", "2026-12-05", "14:00", "Neutering"),
    ("PT010", "2026-12-07", "09:00", "Beak check"),
    ("PT011", "2026-12-07", "13:30", "Limping"),
    ("PT012", "2026-12-08", "10:30", "Vaccination"),
    ("PT013", "2026-12-08", "15:00", "Weight check"),
    ("PT014", "2026-12-09", "09:00", "Shell care"),
    ("PT015", "2026-12-09", "11:30", "Dental cleaning"),
    ("PT016", "2026-12-10", "10:00", "Skin allergy"),
    ("PT017", "2026-12-10", "16:00", "General check-up"),
    ("PT018", "2026-12-11", "09:30", "Deworming"),
    ("PT019", "2026-12-11", "10:00", "Deworming"),
    ("PT020", "2026-12-14", "14:30", "Teeth trimming"),
    ("PT021", "2026-12-14", "16:00", "Vaccination"),
    ("PT022", "2026-12-16", "10:30", "Eye infection"),
    ("PT023", "2026-12-16", "13:00", "Annual check-up"),
    ("PT024", "2026-12-17", "11:00", "Weight loss"),
]


def create_sample_appointments():
    # AppointmentManager needs PetManager to check pet IDs,
    # and PetManager needs OwnerManager, so create all three like main() does
    owner_manager = OwnerManager(DATA_DIRECTORY / "owners.csv")
    pet_manager = PetManager(DATA_DIRECTORY / "pets.csv", owner_manager)
    appointment_manager = AppointmentManager(DATA_DIRECTORY / "appointments.csv", pet_manager)

    managers = [owner_manager, pet_manager, appointment_manager]
    # Same loading and checking as main(): stop if any file is broken
    if not load_all(managers):
        return

    # Never mix sample data with appointments that are already there
    if appointment_manager.items:
        print("appointments.csv already contains records. Empty it first to load sample data.")
        return

    for pet_id, date, time, reason in SAMPLE_APPOINTMENTS:
        data = {"pet_id": pet_id, "date": date, "time": time, "reason": reason}

        # Same steps as handle_add(): validate, create an ID, build the object, save
        errors = appointment_manager.validate(data)
        if errors:
            print(f"Stopped at {pet_id} {date} {time}: {', '.join(errors)}")
            return

        item_id = appointment_manager.next_id()
        appointment = appointment_manager.item_from_data(item_id, data)
        if not appointment_manager.add(appointment):
            print(SAVE_FAILED)
            return

    print(f"Added {len(appointment_manager.items)} appointments.")


if __name__ == "__main__":
    create_sample_appointments()
