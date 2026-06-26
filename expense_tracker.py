# ==========================================================
# PROJECT : PERSONAL EXPENSE TRACKER
# COURSE  : Python Programming
# FILE    : expense_tracker.py
# ==========================================================
# Tracks daily expenses by category, compares spending
# against a monthly budget, and reports overspending.
# Expenses are stored as a list of dictionaries.
# ==========================================================

# ----------------------------------------------------------
# DATA STORE
# expenses is a list of dicts, one per entry:
#   { "description": str, "category": str,
#     "amount": float, "date": str (DD-MM-YYYY) }
# ----------------------------------------------------------
expenses = []
monthly_budget = 0.0

VALID_CATEGORIES = ["Food", "Travel", "Bills", "Entertainment", "Other"]


# ----------------------------------------------------------
# VALIDATE AMOUNT
# Ensures the entered amount is a positive number.
# Returns the float amount, or None if invalid.
# ----------------------------------------------------------
def validate_amount(prompt):
    try:
        amount = float(input(prompt))
    except ValueError:
        print("~~~> Invalid amount! Please enter a number.")
        return None

    if amount <= 0:
        print("~~~> Amount must be greater than 0.")
        return None

    return amount


# ----------------------------------------------------------
# ADD EXPENSE
# Collects description, category, amount, date; validates
# amount > 0; appends a dict to the expenses list.
# ----------------------------------------------------------
def add_expense():
    description = input("Enter Description: ").strip()
    if not description:
        print("~~~> Description cannot be empty!")
        return

    print(f"Categories: {', '.join(VALID_CATEGORIES)}")
    category = input("Enter Category: ").strip().title()
    if category not in VALID_CATEGORIES:
        print("~~~> Invalid category! Choose from the list shown above.")
        return

    amount = validate_amount("Enter Amount: Rs. ")
    if amount is None:
        return  # validate_amount already printed the error

    date = input("Enter Date (DD-MM-YYYY): ").strip()
    if not date:
        print("~~~> Date cannot be empty!")
        return

    expenses.append({
        "description": description,
        "category": category,
        "amount": amount,
        "date": date,
    })

    running_total = sum(e["amount"] for e in expenses)

    print("\n===> Expense Added Successfully!")
    print(f"Running Total So Far : Rs. {running_total:.2f}")


# ----------------------------------------------------------
# VIEW ALL EXPENSES
# Prints every entry with a serial number, in table format.
# ----------------------------------------------------------
def view_expenses():
    if not expenses:
        print("No expenses recorded yet.")
        return

    print("\n" + "=" * 80)
    print(f"{'No.':<5}{'Description':<20}{'Category':<15}{'Amount':<12}{'Date':<12}")
    print("=" * 80)

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index:<5}"
            f"{expense['description']:<20}"
            f"{expense['category']:<15}"
            f"Rs. {expense['amount']:<8.2f}"
            f"{expense['date']:<12}"
        )

    print("=" * 80)


# ----------------------------------------------------------
# CATEGORY SUMMARY
# Groups and totals expenses by category using a dictionary
# for accumulation.
# ----------------------------------------------------------
def category_summary():
    if not expenses:
        print("No expenses recorded yet.")
        return

    totals = {}
    for expense in expenses:
        category = expense["category"]
        totals[category] = totals.get(category, 0) + expense["amount"]

    print("\n" + "=" * 40)
    print("       CATEGORY SUMMARY")
    print("=" * 40)
    for category, total in totals.items():
        print(f"{category:<15}: Rs. {total:.2f}")
    print("=" * 40)


# ----------------------------------------------------------
# GET TOP CATEGORY
# Returns (category, total) for the highest-spending
# category, or (None, 0) if there are no expenses.
# ----------------------------------------------------------
def get_top_category():
    if not expenses:
        return None, 0

    totals = {}
    for expense in expenses:
        category = expense["category"]
        totals[category] = totals.get(category, 0) + expense["amount"]

    top_category = max(totals, key=totals.get)
    return top_category, totals[top_category]


# ----------------------------------------------------------
# BUDGET REPORT
# Sums all expenses, compares against the monthly budget,
# shows percentage used, and warns at 80% / 100% usage.
# ----------------------------------------------------------
def budget_report():
    total_spent = sum(e["amount"] for e in expenses)
    remaining = monthly_budget - total_spent

    used_percent = (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0

    print("\n" + "=" * 40)
    print("       BUDGET REPORT")
    print("=" * 40)
    print(f"Total Spent  : Rs. {total_spent:.2f}")
    print(f"Budget Limit : Rs. {monthly_budget:.2f}")
    print(f"Remaining    : Rs. {remaining:.2f}")
    print(f"Used         : {used_percent:.2f}%")

    if used_percent >= 100:
        print(f"~~~> WARNING: You have EXCEEDED your budget! ({used_percent:.2f}% used)")
    elif used_percent >= 80:
        print(f"///> WARNING: You have used {used_percent:.2f}% of your budget!")

    top_category, top_total = get_top_category()
    if top_category:
        print(f"Top Category : {top_category} (Rs. {top_total:.2f})")

    print("=" * 40)


# ----------------------------------------------------------
# FILTER BY CATEGORY (Additional Challenge)
# Displays only the expenses matching a chosen category.
# ----------------------------------------------------------
def filter_by_category():
    if not expenses:
        print("No expenses recorded yet.")
        return

    print(f"Categories: {', '.join(VALID_CATEGORIES)}")
    category = input("Enter Category to Filter: ").strip().title()

    matches = [e for e in expenses if e["category"] == category]

    if not matches:
        print(f"No expenses found in category '{category}'.")
        return

    print("\n" + "=" * 80)
    print(f"{'No.':<5}{'Description':<20}{'Amount':<12}{'Date':<12}")
    print("=" * 80)

    for index, expense in enumerate(matches, start=1):
        print(
            f"{index:<5}"
            f"{expense['description']:<20}"
            f"Rs. {expense['amount']:<8.2f}"
            f"{expense['date']:<12}"
        )

    print("=" * 80)
    print(f"Total in {category}: Rs. {sum(e['amount'] for e in matches):.2f}")


# ----------------------------------------------------------
# MOST EXPENSIVE EXPENSE (Additional Challenge)
# ----------------------------------------------------------
def most_expensive_expense():
    if not expenses:
        print("No expenses recorded yet.")
        return

    top_expense = max(expenses, key=lambda e: e["amount"])

    print("\n===> Most Expensive Entry:")
    print(f"Description : {top_expense['description']}")
    print(f"Category    : {top_expense['category']}")
    print(f"Amount      : Rs. {top_expense['amount']:.2f}")
    print(f"Date        : {top_expense['date']}")


# ----------------------------------------------------------
# AVERAGE DAILY SPENDING (Additional Challenge)
# Divides total spending by the number of UNIQUE dates
# recorded, so multiple expenses on the same day count
# as one day, not several.
# ----------------------------------------------------------
def average_daily_spending():
    if not expenses:
        print("No expenses recorded yet.")
        return

    unique_dates = {e["date"] for e in expenses}  # set comprehension
    total_spent = sum(e["amount"] for e in expenses)
    average = total_spent / len(unique_dates)

    print("\n===> Average Daily Spending:")
    print(f"Total Spent   : Rs. {total_spent:.2f}")
    print(f"Days Tracked  : {len(unique_dates)}")
    print(f"Daily Average : Rs. {average:.2f}")


# ----------------------------------------------------------
# SAVE TO FILE (Additional Challenge)
# Writes the full expense log + budget report to a text
# file when the program exits.
# ----------------------------------------------------------
def save_to_file():
    filename = "expenses.txt"

    try:
        with open(filename, "w") as f:
            f.write("PERSONAL EXPENSE TRACKER - SESSION LOG\n")
            f.write("=" * 80 + "\n")
            f.write(f"Monthly Budget: Rs. {monthly_budget:.2f}\n\n")

            f.write(f"{'No.':<5}{'Description':<20}{'Category':<15}"
                    f"{'Amount':<12}{'Date':<12}\n")
            f.write("-" * 80 + "\n")

            for index, expense in enumerate(expenses, start=1):
                f.write(
                    f"{index:<5}"
                    f"{expense['description']:<20}"
                    f"{expense['category']:<15}"
                    f"Rs. {expense['amount']:<8.2f}"
                    f"{expense['date']:<12}\n"
                )

            total_spent = sum(e["amount"] for e in expenses)
            used_percent = (
                (total_spent / monthly_budget * 100) if monthly_budget > 0 else 0
            )

            f.write("-" * 80 + "\n")
            f.write(f"Total Spent : Rs. {total_spent:.2f}\n")
            f.write(f"Used        : {used_percent:.2f}%\n")

        print(f"===> Expense log saved to '{filename}'")

    except OSError as e:
        print(f"~~~> Could not save file: {e}")


# ----------------------------------------------------------
# MENU
# Only PRINTS the menu — it does not read input itself.
# ----------------------------------------------------------
def show_menu():
    print("\n" + "=" * 50)
    print("     === PERSONAL EXPENSE TRACKER ===")
    print("=" * 50)
    print(f"Monthly Budget: Rs. {monthly_budget:.2f}")
    print("-" * 50)
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Category Summary")
    print("4. Budget Report")
    print("5. Filter by Category")
    print("6. Most Expensive Expense")
    print("7. Average Daily Spending")
    print("8. Exit")
    print("=" * 50)


# ----------------------------------------------------------
# MAIN LOOP
# Asks for the monthly budget once at startup, then loops
# on the menu. Saves the log to file automatically on exit.
# ----------------------------------------------------------
def main():
    global monthly_budget

    print("===== PERSONAL EXPENSE TRACKER =====")
    while True:
        budget_amount = validate_amount("Set Your Monthly Budget: Rs. ")
        if budget_amount is not None:
            monthly_budget = budget_amount
            break

    while True:
        show_menu()
        try:
            choice = int(input("Choice: "))
        except ValueError:
            print("~~~> Please enter a number.")
            continue

        if choice == 1:
            add_expense()
        elif choice == 2:
            view_expenses()
        elif choice == 3:
            category_summary()
        elif choice == 4:
            budget_report()
        elif choice == 5:
            filter_by_category()
        elif choice == 6:
            most_expensive_expense()
        elif choice == 7:
            average_daily_spending()
        elif choice == 8:
            save_to_file()
            print("Thank You! Goodbye.")
            break
        else:
            print("~~~> Invalid Choice. Please select 1-8.")


if __name__ == "__main__":
    main()

'''
================ SAMPLE TEST OUTPUT ================

Monthly Budget: Rs. 10000

========== 10 EXPENSE ENTRIES ==========

1. Lunch                  Food            Rs. 250      01-07-2026
2. Bus Pass               Travel          Rs. 500      02-07-2026
3. Electricity Bill       Bills           Rs. 1800     03-07-2026
4. Movie Ticket           Entertainment   Rs. 400      04-07-2026
5. Mobile Recharge        Bills           Rs. 299      05-07-2026
6. Dinner                 Food            Rs. 450      06-07-2026
7. Shopping               Other           Rs. 2500     07-07-2026
8. Auto Fare              Travel          Rs. 200      08-07-2026
9. Pizza                  Food            Rs. 700      09-07-2026
10. Headphones            Other           Rs. 3500     10-07-2026

====================================================

========== CATEGORY SUMMARY ==========

Food            : Rs. 1400.00
Travel          : Rs. 700.00
Bills           : Rs. 2099.00
Entertainment   : Rs. 400.00
Other           : Rs. 6000.00

====================================================

========== BUDGET REPORT ==========

Total Spent  : Rs. 10599.00
Budget Limit : Rs. 10000.00
Remaining    : Rs. -599.00
Used         : 105.99%

WARNING: You have EXCEEDED your budget!
(105.99% used)

Top Category : Other (Rs. 6000.00)

====================================================

========== MOST EXPENSIVE EXPENSE ==========

Description : Headphones
Category    : Other
Amount      : Rs. 3500.00
Date        : 10-07-2026

====================================================

========== AVERAGE DAILY SPENDING ==========

Total Spent   : Rs. 10599.00
Days Tracked  : 10
Daily Average : Rs. 1059.90

====================================================
END OF SAMPLE TEST OUTPUT
=========================
'''
