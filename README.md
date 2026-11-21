# PetAppointment_Project
CPE 102 Computer Programming// Final Projecy dued dte 23th Nov 2026

## How to run

```
python main.py              # start the program
python sample_data.py       # optional: fill empty data files with 20 owners, 24 pets, 25 appointments
```

The `data` folder and its CSV files are created on the first run.

## Project structure

```
main.py                 menus: main(), load_all(), manager_menu(), handle_*()
sample_data.py          sample owners, pets and appointments
sample_appointments.py  sample appointments only (needs pets PT001-PT024)
clinic/
    __init__.py
    models.py           Person, Owner, Pet, Appointment
    csv_handler.py      CSVHandler: reads and writes one CSV file
    managers.py         BaseManager, OwnerManager, PetManager, AppointmentManager
data/                   owners.csv, pets.csv, appointments.csv
```
