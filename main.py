"""
Programme started point: main menu divided menu ad get the command form the user.
run: python main.py
"""

from pathlib import Path
from clinic.managers import AppointmentManager, OwnerManager, PetManager

DATA_DIRECTORY = Path(__file__).resolve().parent / "data"
SAVE_FAILED = "บันทึกไม่สำเร็จ กรุณาปิดไฟล์ใน Excel แล้วลองใหม่"


def show_errors(errors): #แสดงรายการข้อผิดพลาดทั้งหมดจากการตรวจสอบข้อมูล
    print("!! Errors found. Please check your input !! :")
    for error in errors:
        print(f" * {error}")


def show_items(items):
    if not items:
        print("No records yet.")
        return
    for item in items:
        print(item)


def handle_add(manager): #การเพิ่มข้อมูลใหม้
    print(f"\n[Add New {manager.title}]")
    data = manager.prompt_data()
    errors = manager.validate(data)
    if errors:
        show_errors(errors)
        return
    item_id = manager.next_id()
    item = manager.item_from_data(item_id, data)
    if manager.add(item):
        print(f"Record added successfully! (ID: {item_id})")
    else:
        print("!! Save failed. (Please close the CSV file in Excel and try again)")


def handle_update(manager):#แก้ไขIDใหม่้
    print(f"\n[Update {manager.title} Information]")
    target_id = input("Enter the ID to update: ").strip()
    old_item = manager.find_by_id(target_id)
    if old_item is None:
        print("ID not found in the system.")
        return
    print("Current information:", old_item)
    print("(Press Enter to skip any field you do not want to change)")
    updated_data = manager.prompt_data(old_item)
    errors = manager.validate(updated_data, exclude_id=target_id)
    if errors:
        show_errors(errors)
        return
    if manager.update(target_id, updated_data):
        print("Information updated successfully.")
    else:
        print("!! Save failed. (Please close the CSV file in Excel and try again)")


def handle_delete(manager): #การลบข้อมูล
    print(f"\n[Delete {manager.title} Information]")
    target_id = input("Enter the ID to delete: ").strip()
    target_item = manager.find_by_id(target_id)
    if target_item is None:
        print("ID not found in the system.")
        return
    can_remove, reason = manager.can_delete(target_id)
    if not can_remove:
        print(f"!! Cannot delete this record: {reason}")
        return
    print("Record to be deleted:", target_item)
    confirm = input("Are you sure you want to delete this record? (Yes/No): ").strip().lower()
    if confirm != "yes":
        print("Deletion canceled.")
        return
    if manager.delete(target_id):
        print("Record deleted from the system.")
    else:
        print("!! Save failed. (Please close the CSV file in Excel and try again)")


def handle_search(manager): #การค้นหาข้อมูล
    print(f"\n[Search {manager.title} Information]")
    keyword = input("Enter search keyword (Name or ID): ").strip()
    if keyword == "":
        print("Please enter a search keyword.")
        return
    matched_items = manager.search(keyword)
    if len(matched_items) == 0:
        print("No matching records found.")
    else:
        print(f"Found {len(matched_items)} matching record(s):")
        show_items(matched_items)


def manager_screen(manager): # หน้าจอย่อยที่มีข้อมูเพิ่ม แก้ไข ลบ ค้นหา แสดงทั้งหมด
    while True:
        print(f"\n=== Screen: {manager.title} ===")
        print("[1] Add New Record")
        print("[2] Update Record")
        print("[3] Delete Record")
        print("[4] Search Record")
        print("[5] Show All Records")
        print("[0] Back to Main Screen")
        screen_choice = input("Select an option (0-5): ").strip()

        if screen_choice == "1":
            handle_add(manager)
        elif screen_choice == "2":
            handle_update(manager)
        elif screen_choice == "3":
            handle_delete(manager)
        elif screen_choice == "4":
            handle_search(manager)
        elif screen_choice == "5":
            show_items(manager.items)
        elif screen_choice == "0":
            break
        else:
            print("Please enter a number between 0 and 5 only.")

def main():#ฟังก์ชันหลักมีการสร้างManager เชื่อมความสัมพันธ์ โหลดไฟล์ CSV และวนลูปหน้าจอหลัก
    owner_manager = OwnerManager(DATA_DIRECTORY /"owners.csv")
    pet_manager = PetManager(DATA_DIRECTORY /"pets.csv", owner_manager)
    appointment_manager = AppointmentManager(DATA_DIRECTORY /"appointments.csv", pet_manager)

    owner_manager.pet_manager = pet_manager
    pet_manager.appointment_manager = appointment_manager
    all_managers = [owner_manager, pet_manager, appointment_manager]
    error_files = []

    for manager in all_managers:
        if not manager.load():
            error_files.append(manager.csv_handler.file_path.name)
    if len(error_files) > 0:
        print("!! Error loading files:", ", ".join(error_files))
        print("Please check the files before starting the program.")
        return
    while True:
        print("\n==========================================")
        print("      Pet Clinic Management System        ")
        print("==========================================")
        print("1. Manage Pet Owners")
        print("2. Manage Pets")
        print("3. Manage Appointments")
        print("0. Exit Program")

        main_choice = input("Please select a main menu option (0-3): ").strip()

        if main_choice == "1":
            manager_screen(owner_manager)
        elif main_choice == "2":
            manager_screen(pet_manager)
        elif main_choice == "3":
            manager_screen(appointment_manager)
        elif main_choice == "0":
            print("Thank you for using the Pet Clinic Management System. Goodbye!")
            break
        else:
            print("Invalid option. Please enter a number between 0 and 3.")


if __name__ == "__main__":
    main()