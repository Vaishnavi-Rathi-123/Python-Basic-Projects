# ==========================================================
# PROJECT : STUDENT MANAGEMENT SYSTEM
# COURSE  : Python Programming
# ==========================================================
# A console-based CRUD app for managing student records.
# Records live in memory (a dict) while running, and are
# saved to / loaded from a CSV file for persistence.
# ==========================================================

import csv
import os

# Global dictionary that acts as our "database".
# Key   -> roll_no (int)
# Value -> dict containing name, marks, percentage, grade
students = {}

DATA_FILE = "students.csv"


# ----------------------------------------------------------
# ADD STUDENT
# ----------------------------------------------------------
def add_student():
    try:
        roll_no = int(input("Enter Roll Number: "))

        if roll_no in students:
            print("[ERROR] Roll Number already exists!")
            return

        name = input("Enter Student Name: ").strip()
        if not name:
            print("[ERROR] Name cannot be empty!")
            return

        marks = []
        total = 0

        for i in range(1, 6):
            mark = float(input(f"Enter Marks of Subject {i}: "))

            if not (0 <= mark <= 100):
                print("[ERROR] Marks must be between 0 and 100!")
                return

            marks.append(mark)
            total += mark

        percentage = total / 5
        grade = calculate_grade(percentage)

        students[roll_no] = {
            "name": name,
            "marks": marks,
            "percentage": percentage,
            "grade": grade,
        }

        print("\n[OK] Student Added Successfully!")
        print(f"Percentage : {percentage:.2f}")
        print(f"Grade      : {grade}")

    except ValueError:
        print("[ERROR] Invalid Input!")


# ----------------------------------------------------------
# VIEW ALL STUDENTS
# Shows every record in roll-number (insertion) order.
# ----------------------------------------------------------
def view_all():
    if not students:
        print("No Records Found.")
        return

    print("\n" + "=" * 75)
    print(f"{'Roll':<10}{'Name':<20}{'Percentage':<15}{'Grade':<10}")
    print("=" * 75)

    for roll, data in students.items():
        print(
            f"{roll:<10}"
            f"{data['name']:<20}"
            f"{data['percentage']:<15.2f}"
            f"{data['grade']:<10}"
        )

    print("=" * 75)


# ----------------------------------------------------------
# VIEW SORTED BY PERCENTAGE (Challenge 2 + 4)
# Shows all students ranked highest percentage first.
# Rank is computed on the fly from the sort order, so it
# always reflects the latest marks.
# ----------------------------------------------------------
def view_sorted_by_percentage():
    if not students:
        print("No Records Found.")
        return

    # sorted() with a lambda key, descending order (reverse=True)
    ranked = sorted(
        students.items(),
        key=lambda item: item[1]["percentage"],
        reverse=True,
    )

    print("\n" + "=" * 85)
    print(f"{'Rank':<6}{'Roll':<10}{'Name':<20}{'Percentage':<15}{'Grade':<10}")
    print("=" * 85)

    for position, (roll, data) in enumerate(ranked, start=1):
        print(
            f"{position:<6}"
            f"{roll:<10}"
            f"{data['name']:<20}"
            f"{data['percentage']:<15.2f}"
            f"{data['grade']:<10}"
        )

    print("=" * 85)


# ----------------------------------------------------------
# SEARCH STUDENT
# ----------------------------------------------------------
def search_student():
    try:
        roll_no = int(input("Enter Roll Number: "))
        student = students.get(roll_no)

        if student:
            print("\n===== STUDENT DETAILS =====")
            print("Roll No    :", roll_no)
            print("Name       :", student["name"])
            print("Marks      :", student["marks"])
            print("Percentage :", round(student["percentage"], 2))
            print("Grade      :", student["grade"])
        else:
            print("[ERROR] Student Not Found")

    except ValueError:
        print("[ERROR] Invalid Input")


# ----------------------------------------------------------
# UPDATE STUDENT
# ----------------------------------------------------------
def update_student():
    try:
        roll_no = int(input("Enter Roll Number: "))

        if roll_no not in students:
            print("[ERROR] Student Not Found")
            return

        print("\n1. Update Name")
        print("2. Update Marks")
        choice = int(input("Enter Choice: "))

        if choice == 1:
            new_name = input("Enter New Name: ").strip()
            if not new_name:
                print("[ERROR] Name cannot be empty!")
                return

            students[roll_no]["name"] = new_name
            print("[OK] Name Updated Successfully")

        elif choice == 2:
            marks = []
            total = 0

            for i in range(1, 6):
                mark = float(input(f"Enter Marks of Subject {i}: "))

                if not (0 <= mark <= 100):
                    print("[ERROR] Marks must be between 0 and 100!")
                    return

                marks.append(mark)
                total += mark

            percentage = total / 5
            grade = calculate_grade(percentage)

            students[roll_no].update({
                "marks": marks,
                "percentage": percentage,
                "grade": grade,
            })

            print("[OK] Marks Updated Successfully")

        else:
            print("[ERROR] Invalid Choice")

    except ValueError:
        print("[ERROR] Invalid Input")


# ----------------------------------------------------------
# DELETE STUDENT
# ----------------------------------------------------------
def delete_student():
    try:
        roll_no = int(input("Enter Roll Number: "))

        if roll_no not in students:
            print("[ERROR] Student Not Found")
            return

        confirm = input("Are you sure you want to delete? (yes/no): ").lower()

        if confirm == "yes":
            students.pop(roll_no)
            print("[OK] Student Deleted Successfully")
        else:
            print("Deletion Cancelled")

    except ValueError:
        print("[ERROR] Invalid Input")


# ----------------------------------------------------------
# GRADE HELPERS
# ----------------------------------------------------------
def calculate_grade(percentage):
    """Takes a percentage and returns the letter grade."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "F"


def show_grading_scale():
    """Prints the grading scale for reference."""
    print("\nGRADING SCALE")
    print("90 and above : A+")
    print("80 - 89      : A")
    print("70 - 79      : B+")
    print("60 - 69      : B")
    print("50 - 59      : C")
    print("40 - 49      : D")
    print("Below 40     : F")


# ----------------------------------------------------------
# CLASS REPORT (Challenge 3)
# Summarizes the whole class: topper, average percentage,
# and a pass/fail count. "Pass" is defined as percentage
# >= 40 (i.e. grade is not "F") — adjust PASS_MARK below
# if your institution uses a different cutoff.
# ----------------------------------------------------------
PASS_MARK = 40


def generate_class_report():
    if not students:
        print("No Records Found.")
        return

    # Find the topper: the student dict with the highest percentage
    topper_roll, topper_data = max(
        students.items(), key=lambda item: item[1]["percentage"]
    )

    total_percentage = sum(s["percentage"] for s in students.values())
    average_percentage = total_percentage / len(students)

    pass_count = sum(1 for s in students.values() if s["percentage"] >= PASS_MARK)
    fail_count = len(students) - pass_count

    print("\n" + "=" * 50)
    print("              CLASS REPORT")
    print("=" * 50)
    print(f"Total Students   : {len(students)}")
    print(f"Class Average %  : {average_percentage:.2f}")
    print(f"Topper           : {topper_data['name']} "
          f"(Roll {topper_roll}, {topper_data['percentage']:.2f}%, "
          f"Grade {topper_data['grade']})")
    print(f"Pass Count       : {pass_count}")
    print(f"Fail Count       : {fail_count}")
    print("=" * 50)


# ----------------------------------------------------------
# SAVE / LOAD TO CSV (Challenge 1)
# Persists the in-memory dictionary to disk so records
# survive between program runs.
# ----------------------------------------------------------
def save_to_file():
    """
    Writes every student record to DATA_FILE in CSV format.
    Marks (a list of 5 numbers) are joined with '|' into a
    single CSV cell, then split back apart when loading.
    """
    try:
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["roll_no", "name", "marks", "percentage", "grade"])

            for roll_no, data in students.items():
                marks_str = "|".join(str(m) for m in data["marks"])
                writer.writerow([
                    roll_no,
                    data["name"],
                    marks_str,
                    data["percentage"],
                    data["grade"],
                ])

        print(f"[OK] Saved {len(students)} record(s) to '{DATA_FILE}'")

    except OSError as e:
        print(f"[ERROR] Could not save file: {e}")


def load_from_file():
    """
    Reads DATA_FILE (if it exists) back into the students
    dict. Called automatically once at program startup so
    data persists across runs.
    """
    if not os.path.exists(DATA_FILE):
        return  # nothing to load yet, e.g. first ever run

    try:
        with open(DATA_FILE, newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                roll_no = int(row["roll_no"])
                marks = [float(m) for m in row["marks"].split("|")]

                students[roll_no] = {
                    "name": row["name"],
                    "marks": marks,
                    "percentage": float(row["percentage"]),
                    "grade": row["grade"],
                }

        if students:
            print(f"[INFO] Loaded {len(students)} record(s) from '{DATA_FILE}'")

    except (OSError, ValueError, KeyError) as e:
        print(f"[WARNING] Could not load existing data: {e}")


# ----------------------------------------------------------
# MENU
# Only PRINTS the menu — it does not read input itself.
# ----------------------------------------------------------
def show_menu():
    print("\n" + "=" * 50)
    print("       STUDENT MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Add Student")
    print("2. View All Students")
    print("3. Search by Roll Number")
    print("4. Update Student")
    print("5. Delete Student")
    print("6. Show Grading Scale")
    print("7. Show Menu")
    print("8. View Sorted by Percentage (with Rank)")
    print("9. Generate Class Report")
    print("10. Save Records to File")
    print("11. Exit")
    print("=" * 50)


# ----------------------------------------------------------
# MAIN LOOP
# Loads saved data on startup, then loops on the menu.
# Saves to file automatically on exit so nothing is lost.
# ----------------------------------------------------------
def main():
    load_from_file()  # restore previous session's data, if any

    while True:
        show_menu()
        try:
            choice = int(input("Enter Your Choice: "))

            if choice == 1:
                add_student()
            elif choice == 2:
                view_all()
            elif choice == 3:
                search_student()
            elif choice == 4:
                update_student()
            elif choice == 5:
                delete_student()
            elif choice == 6:
                show_grading_scale()
            elif choice == 7:
                continue
            elif choice == 8:
                view_sorted_by_percentage()
            elif choice == 9:
                generate_class_report()
            elif choice == 10:
                save_to_file()
            elif choice == 11:
                save_to_file()  # auto-save before quitting
                print("Thank You!")
                break
            else:
                print("[ERROR] Invalid Choice")

        except ValueError:
            print("[ERROR] Please Enter Numbers Only")


if __name__ == "__main__":
    main()
