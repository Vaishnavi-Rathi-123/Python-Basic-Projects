# ==========================================================
# PROJECT : LIBRARY MANAGEMENT SYSTEM
# COURSE  : Python Programming
# FILE    : library_management.py
# ==========================================================
# Tracks books, handles issue/return, borrower tracking,
# overdue fines, a waiting list for issued books, and
# catalog export — all using a nested dictionary as the
# in-memory "database".
# ==========================================================

from datetime import datetime, timedelta

# ----------------------------------------------------------
# DATA STORE
# Master dictionary: ISBN (str) -> book record (dict)
#   {
#     "title": str,
#     "author": str,
#     "available": bool,
#     "borrower_name": str or None,
#     "borrower_id": str or None,
#     "issue_date": datetime or None,
#     "waiting_list": list of (borrower_id, borrower_name)
#   }
# ----------------------------------------------------------
library = {}

ISSUE_PERIOD_DAYS = 7
FINE_PER_DAY = 2  # Rs. 2/day after due date
DATE_FORMAT = "%d-%B-%Y"  # e.g. 28-June-2026
INPUT_DATE_FORMAT = "%d-%m-%Y"  # e.g. 28-06-2026, used for typed-in dates


def get_date_input(prompt):
    """
    Asks the user to type a date as DD-MM-YYYY.
    - Empty input -> returns today's date/time (datetime.now()).
    - Invalid format -> prints an error and returns None so the
      calling function can abort cleanly.
    """
    date_str = input(prompt).strip()

    if not date_str:
        return datetime.now()

    try:
        return datetime.strptime(date_str, INPUT_DATE_FORMAT)
    except ValueError:
        print("~~~> Invalid date format! Please use DD-MM-YYYY (e.g. 21-06-2026).")
        return None


# ----------------------------------------------------------
# ADD BOOK
# Registers a new book with a unique ISBN.
# ----------------------------------------------------------
def add_book():
    isbn = input("Enter ISBN: ").strip()

    if not isbn:
        print("~~~> ISBN cannot be empty!")
        return

    if isbn in library:
        print("~~~> A book with this ISBN already exists!")
        return

    title = input("Enter Title: ").strip()
    author = input("Enter Author: ").strip()

    if not title or not author:
        print("~~~> Title and Author cannot be empty!")
        return

    library[isbn] = {
        "title": title,
        "author": author,
        "available": True,
        "borrower_name": None,
        "borrower_id": None,
        "issue_date": None,
        "waiting_list": [],  # list of (borrower_id, borrower_name) tuples
    }

    print(f"\n===> Book '{title}' added successfully!")


# ----------------------------------------------------------
# ISSUE BOOK
# Issues a book to a student if available. If it's already
# issued, offers to add the student to a waiting list
# (Additional Challenge: waiting list).
# ----------------------------------------------------------
def issue_book():
    isbn = input("Enter ISBN: ").strip()

    try:
        book = library[isbn]  # raises KeyError if ISBN not found
    except KeyError:
        print("~~~> No book found with this ISBN!")
        return

    borrower_id = input("Enter Borrower ID: ").strip()
    borrower_name = input("Enter Your Name: ").strip()

    if not borrower_id or not borrower_name:
        print("~~~> Borrower ID and Name are required!")
        return

    if book["available"]:
        # --- Ask for the issue date (manual entry, defaults to today) ---
        issue_date = get_date_input(
            "Enter Issue Date (DD-MM-YYYY) [Press Enter for today]: "
        )
        if issue_date is None:
            return  # invalid date was entered; get_date_input already printed the error

        # --- Normal issue: book is free to lend ---
        book["available"] = False
        book["borrower_id"] = borrower_id
        book["borrower_name"] = borrower_name
        book["issue_date"] = issue_date

        due_date = book["issue_date"] + timedelta(days=ISSUE_PERIOD_DAYS)

        print("\n===> Book Issued Successfully!")
        print(f"Title    : {book['title']}")
        print(f"Due Date : {due_date.strftime(DATE_FORMAT)}")

    else:
        # --- Book already issued: offer the waiting list ---
        print(f"~~~> '{book['title']}' is currently issued to {book['borrower_name']}.")
        choice = input("Add yourself to the waiting list? (yes/no): ").strip().lower()

        if choice == "yes":
            book["waiting_list"].append((borrower_id, borrower_name))
            position = len(book["waiting_list"])
            print(f"===> Added to waiting list. Your position: {position}")
        else:
            print("Okay, not added to waiting list.")


# ----------------------------------------------------------
# RETURN BOOK
# Marks a book as returned, calculates an overdue fine if
# applicable (Additional Challenge), and automatically
# issues it to the next person on the waiting list if any.
# ----------------------------------------------------------
def return_book():
    isbn = input("Enter ISBN: ").strip()

    try:
        book = library[isbn]
    except KeyError:
        print("~~~> No book found with this ISBN!")
        return

    if book["available"]:
        print("~~~> This book was not issued, so it can't be returned.")
        return

    # --- Ask how the return date should be determined ---
    print("\nHow do you want to specify the return date?")
    print("1. Enter number of days after issue date")
    print("2. Enter the actual return date")
    print("3. Use today's date")
    date_choice = input("Choice: ").strip()

    if date_choice == "1":
        try:
            days_after = int(input("Enter number of days after issue: "))
        except ValueError:
            print("~~~> Please enter a whole number of days.")
            return
        return_date = book["issue_date"] + timedelta(days=days_after)

    elif date_choice == "2":
        return_date = get_date_input("Enter Return Date (DD-MM-YYYY): ")
        if return_date is None:
            return

    else:
        return_date = datetime.now()

    fine = calculate_fine(book["issue_date"], return_date)

    print(f"\n===> '{book['title']}' returned by {book['borrower_name']}.")
    print(f"Return Date : {return_date.strftime(DATE_FORMAT)}")
    if fine > 0:
        days_overdue = (return_date - book["issue_date"]).days - ISSUE_PERIOD_DAYS
        print(f"///> Overdue by {days_overdue} day(s). Fine: Rs. {fine}")
    else:
        print("On time — no fine.")

    # Clear current borrower info
    book["borrower_name"] = None
    book["borrower_id"] = None
    book["issue_date"] = None
    book["available"] = True

    # If someone is waiting, hand the book straight to them
    if book["waiting_list"]:
        next_borrower_id, next_borrower_name = book["waiting_list"].pop(0)

        book["available"] = False
        book["borrower_id"] = next_borrower_id
        book["borrower_name"] = next_borrower_name
        book["issue_date"] = datetime.now()

        due_date = book["issue_date"] + timedelta(days=ISSUE_PERIOD_DAYS)

        print(f"\n```> Book auto-issued to next person on waiting list: "
              f"{next_borrower_name} ({next_borrower_id})")
        print(f"Due Date : {due_date.strftime(DATE_FORMAT)}")


def calculate_fine(issue_date, return_date=None):
    """
    Additional Challenge: overdue fine calculation.
    Returns the fine in Rupees for a book issued on issue_date
    and returned on return_date (defaults to right now if not
    given). Rs. 2/day for every day past the 7-day issue period.
    """
    if issue_date is None:
        return 0

    if return_date is None:
        return_date = datetime.now()

    days_held = (return_date - issue_date).days
    days_overdue = days_held - ISSUE_PERIOD_DAYS

    if days_overdue > 0:
        return days_overdue * FINE_PER_DAY
    return 0


def check_due_date(issue_date):
    """Returns the due date (issue_date + 7 days)."""
    if issue_date is None:
        return None
    return issue_date + timedelta(days=ISSUE_PERIOD_DAYS)


# ----------------------------------------------------------
# SEARCH BOOK
# Multi-field search: matches the keyword against title,
# author, or ISBN (case-insensitive, partial match).
# ----------------------------------------------------------
def search_book():
    keyword = input("Enter Title, Author, or ISBN to search: ").strip().lower()

    if not keyword:
        print("~~~> Search keyword cannot be empty!")
        return

    results = []

    for isbn, book in library.items():
        if (
            keyword in book["title"].lower()
            or keyword in book["author"].lower()
            or keyword in isbn.lower()
        ):
            results.append((isbn, book))

    if not results:
        print("~~~> No matching books found.")
        return

    print(f"\n```> Found {len(results)} matching book(s):\n")
    for isbn, book in results:
        print_book_details(isbn, book)


def print_book_details(isbn, book):
    status = "Available ===>" if book["available"] else "Issued ~~~>"
    print("-" * 50)
    print(f"ISBN     : {isbn}")
    print(f"Title    : {book['title']}")
    print(f"Author   : {book['author']}")
    print(f"Status   : {status}")

    if not book["available"]:
        due_date = check_due_date(book["issue_date"])
        print(f"Borrower : {book['borrower_name']} ({book['borrower_id']})")
        print(f"Due Date : {due_date.strftime(DATE_FORMAT)}")

    if book["waiting_list"]:
        print(f"Waiting  : {len(book['waiting_list'])} student(s) in queue")

    print("-" * 50)


# ----------------------------------------------------------
# VIEW CATALOG
# Prints every book in a formatted table.
# ----------------------------------------------------------
def view_catalog():
    if not library:
        print("~~~> No books in the catalog yet.")
        return

    print("\n" + "=" * 90)
    print(f"{'ISBN':<22}{'Title':<25}{'Author':<20}{'Status':<15}{'Waiting':<8}")
    print("=" * 90)

    for isbn, book in library.items():
        status = "Available" if book["available"] else "Issued"
        waiting = len(book["waiting_list"])
        print(
            f"{isbn:<22}"
            f"{book['title']:<25}"
            f"{book['author']:<20}"
            f"{status:<15}"
            f"{waiting:<8}"
        )

    print("=" * 90)


# ----------------------------------------------------------
# LIBRARY REPORT (Additional Challenge)
# Counts of issued vs. available books.
# ----------------------------------------------------------
def library_report():
    if not library:
        print("~~~> No books in the catalog yet.")
        return

    total = len(library)
    issued = sum(1 for b in library.values() if not b["available"])
    available = total - issued

    print("\n" + "=" * 40)
    print("        ===> LIBRARY REPORT")
    print("=" * 40)
    print(f"Total Books     : {total}")
    print(f"Issued          : {issued}")
    print(f"Available       : {available}")
    print("=" * 40)


# ----------------------------------------------------------
# EXPORT CATALOG TO FILE (Additional Challenge)
# ----------------------------------------------------------
def export_catalog():
    if not library:
        print("~~~> No books to export.")
        return

    filename = "library_catalog.txt"

    try:
        with open(filename, "w") as f:
            f.write("LIBRARY CATALOG\n")
            f.write("=" * 90 + "\n")
            f.write(f"{'ISBN':<22}{'Title':<25}{'Author':<20}{'Status':<15}\n")
            f.write("=" * 90 + "\n")

            for isbn, book in library.items():
                status = "Available" if book["available"] else "Issued"
                f.write(
                    f"{isbn:<22}{book['title']:<25}"
                    f"{book['author']:<20}{status:<15}\n"
                )

                if not book["available"]:
                    due_date = check_due_date(book["issue_date"])
                    f.write(
                        f"    Borrower: {book['borrower_name']} "
                        f"({book['borrower_id']}), Due: "
                        f"{due_date.strftime(DATE_FORMAT)}\n"
                    )

            f.write("=" * 90 + "\n")

        print(f"===> Catalog exported to '{filename}'")

    except OSError as e:
        print(f"~~~> Could not export file: {e}")


# ----------------------------------------------------------
# MENU
# ----------------------------------------------------------
def show_menu():
    print("\n" + "=" * 42)
    print("====== LIBRARY MANAGEMENT SYSTEM ======")
    print("=" * 42)
    print("1. Add Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. Search Book")
    print("5. View All")
    print("6. Library Report (Issued vs Available)")
    print("7. Export Catalog to File")
    print("8. Exit")
    print("=" * 42)


# ----------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------
def main():
    while True:
        show_menu()
        choice_input = input("Enter choice: ").strip()

        try:
            choice = int(choice_input)
        except ValueError:
            print("~~~> Please enter a number.")
            continue

        if choice == 1:
            add_book()
        elif choice == 2:
            issue_book()
        elif choice == 3:
            return_book()
        elif choice == 4:
            search_book()
        elif choice == 5:
            view_catalog()
        elif choice == 6:
            library_report()
        elif choice == 7:
            export_catalog()
        elif choice == 8:
            print("Thank you for using the Library Management System!")
            break
        else:
            print("~~~> Invalid choice. Please select 1-8.")


if __name__ == "__main__":
    main()

"""
================ SAMPLE TEST OUTPUT ================

========== ADD BOOK ==========

Book 1
ISBN   : 101
Title  : Python Programming
Author : Chetan Bhagat

Book 2
ISBN   : 102
Title  : Data Structures Using Python
Author : R. Nageswara Rao

Book 3
ISBN   : 103
Title  : Artificial Intelligence Basics
Author : Priya Sharma

Book 4
ISBN   : 104
Title  : Machine Learning Essentials
Author : Rajesh Kumar

Book 5
ISBN   : 105
Title  : Computer Networks
Author : Ankit Verma

=== 5 BOOKS ADDED SUCCESSFULLY ===


========== ISSUE BOOK TEST 1 ==========

Enter ISBN : 101
Borrower ID   : AIML001
Borrower Name : Vaishnavi Rathi

Book Issued Successfully!

Title    : Python Programming
Due Date : 28-June-2026


========== RETURN BOOK TEST 1 ==========

Enter ISBN : 101

Book Returned Successfully!

Title : Python Programming


========== ISSUE BOOK TEST 2 ==========

Enter ISBN : 103
Borrower ID   : AIML002
Borrower Name : Ananya Gupta

Book Issued Successfully!

Title    : Artificial Intelligence Basics
Due Date : 28-June-2026


========== RETURN BOOK TEST 2 ==========

Enter ISBN : 103

Book Returned Successfully!

Title : Artificial Intelligence Basics


========== VIEW CATALOG ==========

==========================================================================================
ISBN          Title                           Author                Status
==========================================================================================
101           Python Programming              Chetan Bhagat         Available
102           Data Structures Using Python    R. Nageswara Rao      Available
103           Artificial Intelligence Basics  Rajesh Kumar          Available
104           Machine Learning Essentials     Priya Sharma          Available
105           Computer Networks               Ankit Verma           Available
==========================================================================================


========== LIBRARY REPORT ==========

Total Books     : 5
Issued Books    : 0
Available Books : 5

====================================================
END OF SAMPLE TEST OUTPUT
====================================================
"""
