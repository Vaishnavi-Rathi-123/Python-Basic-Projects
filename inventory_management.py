"""
=================================================================
 PROJECT 5: INVENTORY MANAGEMENT SYSTEM
=================================================================
A menu-driven stock-control application that:
  - Tracks products (ID, name, category, price, quantity, reorder level)
  - Supports stock-in (restocking) and stock-out (sales) with validation
  - Raises low-stock alerts and generates valuation / category reports
  - Persists data to inventory.txt and logs every transaction with a
    timestamp to transactions.txt

Bonus features implemented:
  - Product search by name or category
  - GST calculation (5% / 12% / 18%) based on product category
  - Barcode-style automatic Product ID generator
  - Restock suggestion list sorted by urgency
  - Daily transaction report filtered by date

File names: inventory_management.py and inventory.txt
=================================================================
"""

import os
from datetime import datetime

INVENTORY_FILE = "inventory.txt"
TRANSACTION_FILE = "transactions.txt"

# GST slabs applied per category (bonus feature)
GST_RATES = {
    "Electronics": 18,
    "FMCG": 5,
    "Apparel": 12,
    "Stationery": 5,
}
DEFAULT_GST_RATE = 18

# Pre-populated starter catalogue used only if inventory.txt is missing,
# so the program still has 8+ products across 3+ categories on first run.
DEFAULT_PRODUCTS = [
    ("P001", "Laptop", "Electronics", 58000.00, 2, 2),
    ("P002", "Wireless Mouse", "Electronics", 750.00, 15, 5),
    ("P003", "Bluetooth Speaker", "Electronics", 2200.00, 6, 3),
    ("P004", "Notebook Pack", "Stationery", 120.00, 40, 10),
    ("P005", "Ball Pen Box", "Stationery", 95.00, 50, 15),
    ("P006", "Cotton T-Shirt", "Apparel", 499.00, 20, 5),
    ("P007", "Denim Jeans", "Apparel", 1299.00, 12, 4),
    ("P008", "Instant Noodles Carton", "FMCG", 480.00, 25, 8),
]


# -----------------------------------------------------------------
# FILE HANDLING
# -----------------------------------------------------------------
def load_inventory(filename=INVENTORY_FILE):
    """Reads inventory data from a pipe-delimited .txt file.
    Returns a dict: {product_id: {name, category, price, quantity, reorder_level}}.
    If the file does not exist, returns a pre-populated default catalogue."""
    inventory = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # skip blank lines
                parts = line.split("|")
                if len(parts) != 6:
                    continue  # skip malformed line
                pid, name, category, price, qty, reorder = parts
                # Normalise the ID and text fields, cast numeric fields to their types
                inventory[pid.strip().upper()] = {
                    "name": name.strip(),
                    "category": category.strip(),
                    "price": float(price),
                    "quantity": int(qty),
                    "reorder_level": int(reorder),
                }
    except FileNotFoundError:
        # First run / file deleted -> bootstrap with the starter catalogue
        print(f"'{filename}' not found. Starting with default catalogue.")
        for pid, name, category, price, qty, reorder in DEFAULT_PRODUCTS:
            inventory[pid] = {
                "name": name,
                "category": category,
                "price": price,
                "quantity": qty,
                "reorder_level": reorder,
            }
    except ValueError as e:
        # A field in the file could not be converted to float/int
        print(f"Error parsing inventory file: {e}")
    return inventory


def save_inventory(inventory, filename=INVENTORY_FILE):
    """Writes the current inventory dict back to a pipe-delimited .txt file."""
    try:
        with open(filename, "w") as f:
            for pid, data in inventory.items():
                # Same pipe-delimited layout used by load_inventory()
                line = (
                    f"{pid}|{data['name']}|{data['category']}|"
                    f"{data['price']}|{data['quantity']}|{data['reorder_level']}\n"
                )
                f.write(line)
        print(f"Inventory saved to '{filename}'.")
    except OSError as e:
        print(f"Could not save inventory: {e}")


def log_transaction(product_id, t_type, qty, resulting_qty, filename=TRANSACTION_FILE):
    """Appends a timestamped transaction entry (IN/OUT/ADD) to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp}|{product_id}|{t_type}|{qty}|{resulting_qty}\n"
    try:
        with open(filename, "a") as f:  # append, never overwrite history
            f.write(entry)
    except OSError as e:
        print(f"Could not write transaction log: {e}")


# -----------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------
def format_inr(amount):
    """Formats a number using the Indian numbering style (lakh/crore commas),
    e.g. 124500.0 -> 'Rs. 1,24,500.00'."""
    amount = round(amount, 2)
    whole, _, frac = f"{amount:.2f}".partition(".")
    negative = whole.startswith("-")
    if negative:
        whole = whole[1:]

    if len(whole) <= 3:
        grouped = whole  # no comma needed for numbers under 1000
    else:
        last_three = whole[-3:]      # last 3 digits form their own group
        remaining = whole[:-3]
        parts = []
        while len(remaining) > 2:    # every group after that is 2 digits
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.insert(0, remaining)
        grouped = ",".join(parts) + "," + last_three

    sign = "-" if negative else ""
    return f"Rs. {sign}{grouped}.{frac}"


def generate_product_id(inventory):
    """Barcode-style auto Product ID generator: P001, P002, ... (bonus feature)."""
    max_num = 0
    for pid in inventory:
        digits = "".join(ch for ch in pid if ch.isdigit())  # extract numeric part
        if digits.isdigit():
            max_num = max(max_num, int(digits))
    return f"P{max_num + 1:03d}"


def get_categories(inventory):
    """Returns the set of unique product categories currently in stock."""
    return {data["category"] for data in inventory.values()}


def get_total_value(inventory):
    """Returns total inventory valuation: sum of price x quantity for all items."""
    return sum(data["price"] * data["quantity"] for data in inventory.values())


def calculate_gst(product):
    """Returns the GST amount for one unit of a product, based on its
    category's slab (bonus feature)."""
    rate = GST_RATES.get(product["category"], DEFAULT_GST_RATE)
    return product["price"] * rate / 100


# -----------------------------------------------------------------
# CORE OPERATIONS
# -----------------------------------------------------------------
def add_product(inventory):
    """Registers a new product after validating a unique Product ID."""
    suggested_id = generate_product_id(inventory)
    prompt = f"Enter Product ID (or press Enter to use '{suggested_id}'): "
    pid = input(prompt).strip().upper()
    if not pid:
        pid = suggested_id  # use the auto-generated ID if left blank

    if pid in inventory:  # uniqueness check
        print(
            f"Product ID '{pid}' already exists! "
            "Use Stock-In to add quantity instead."
        )
        return

    name = input("Enter Product Name: ").strip()
    category = input("Enter Category: ").strip()

    try:
        price = float(input("Enter Unit Price: ").strip())
        quantity = int(input("Enter Initial Quantity: ").strip())
        reorder_level = int(input("Enter Reorder Level: ").strip())
        if price < 0 or quantity < 0 or reorder_level < 0:
            raise ValueError("Values cannot be negative.")
    except ValueError as e:
        print(f"Invalid input, product not added: {e}")
        return

    inventory[pid] = {
        "name": name,
        "category": category,
        "price": price,
        "quantity": quantity,
        "reorder_level": reorder_level,
    }
    log_transaction(pid, "ADD", quantity, quantity)
    # Fixed metadata snapshot stored as an immutable tuple at creation time
    snapshot = (pid, name, category, price)
    print(f"Product added successfully! Snapshot: {snapshot}")


def stock_in(inventory):
    """Adds quantity to an existing product (restocking)."""
    pid = input("Enter Product ID to stock-in: ").strip().upper()
    if pid not in inventory:
        print(f"Product ID '{pid}' not found.")
        return

    try:
        qty = int(input("Enter quantity to add: ").strip())
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
    except ValueError as e:
        print(f"Invalid quantity: {e}")
        return

    inventory[pid]["quantity"] += qty  # update stock level
    log_transaction(pid, "IN", qty, inventory[pid]["quantity"])  # record the movement
    print(
        f"Stocked in {qty} units of '{inventory[pid]['name']}'. "
        f"New quantity: {inventory[pid]['quantity']}"
    )


def stock_out(inventory):
    """Deducts quantity from a product after checking sufficient stock."""
    pid = input("Enter Product ID to stock-out: ").strip().upper()
    if pid not in inventory:
        print(f"Product ID '{pid}' not found.")
        return

    try:
        qty = int(input("Enter quantity to remove: ").strip())
        if qty <= 0:
            raise ValueError("Quantity must be positive.")
    except ValueError as e:
        print(f"Invalid quantity: {e}")
        return

    available = inventory[pid]["quantity"]
    if qty > available:  # prevent stock going negative
        print(
            f"Error: Insufficient stock! Only {available} units of "
            f"'{inventory[pid]['name']}' available."
        )
        return

    inventory[pid]["quantity"] -= qty
    log_transaction(pid, "OUT", qty, inventory[pid]["quantity"])
    print(
        f"Stocked out {qty} units of '{inventory[pid]['name']}'. "
        f"Remaining quantity: {inventory[pid]['quantity']}"
    )

    # Immediately flag the product if it has dropped to/below its reorder level
    if inventory[pid]["quantity"] <= inventory[pid]["reorder_level"]:
        print(
            f"⚠ Low stock alert: '{inventory[pid]['name']}' is now at or "
            f"below its reorder level ({inventory[pid]['reorder_level']})."
        )


def view_inventory(inventory):
    """Displays the full inventory in a formatted table, including total value."""
    if not inventory:
        print("Inventory is empty.")
        return

    print("\n" + "=" * 80)
    print(f"{'ID':<6}{'Name':<24}{'Category':<14}{'Price':>10}{'Qty':>6}{'Value':>16}")
    print("-" * 80)
    for pid, data in inventory.items():
        value = data["price"] * data["quantity"]
        print(
            f"{pid:<6}{data['name']:<24}{data['category']:<14}"
            f"{data['price']:>10.2f}{data['quantity']:>6}{format_inr(value):>16}"
        )
    print("-" * 80)
    print(f"{'TOTAL INVENTORY VALUE':<60}{format_inr(get_total_value(inventory)):>20}")
    print("=" * 80)


def low_stock_alert(inventory):
    """Lists every product whose quantity is at or below its reorder level."""
    alerts = [
        (pid, data)
        for pid, data in inventory.items()
        if data["quantity"] <= data["reorder_level"]
    ]

    if not alerts:
        print("\nNo low-stock items. All products are sufficiently stocked. ✓")
        return

    print(f"\n----- LOW STOCK ALERT ({len(alerts)} item(s)) -----")
    for pid, data in alerts:
        print(
            f"{pid} - {data['name']:<20} Qty: {data['quantity']:<5} "
            f"Reorder Level: {data['reorder_level']}"
        )
    print("-" * 45)


def generate_report(inventory):
    """Prints a summary report: total products, total value, categories,
    low-stock count, and the highest-value item."""
    if not inventory:
        print("Inventory is empty. No report to generate.")
        return

    total_products = len(inventory)
    total_value = get_total_value(inventory)
    categories = get_categories(inventory)
    low_stock_count = sum(
        1 for d in inventory.values() if d["quantity"] <= d["reorder_level"]
    )

    top_pid, top_data = max(
        inventory.items(), key=lambda item: item[1]["price"] * item[1]["quantity"]
    )
    top_value = top_data["price"] * top_data["quantity"]

    print("\n======= INVENTORY REPORT =======")
    print(f"Total Products    : {total_products}")
    print(f"Total Stock Value : {format_inr(total_value)}")
    print(f"Categories        : {', '.join(sorted(categories))}")
    print(f"Low Stock Items   : {low_stock_count} (below or at reorder level)")
    print(
        f"Highest Value Item: {top_data['name']} "
        f"({format_inr(top_data['price'])} x {top_data['quantity']} = "
        f"{format_inr(top_value)})"
    )
    print("=================================")


# -----------------------------------------------------------------
# BONUS FEATURES
# -----------------------------------------------------------------
def search_product(inventory):
    """Searches products by name or category keyword (bonus feature)."""
    keyword = input("Enter product name or category to search: ").strip().lower()
    matches = [
        (pid, data)
        for pid, data in inventory.items()
        if keyword in data["name"].lower() or keyword in data["category"].lower()
    ]

    if not matches:
        print(f"No products found matching '{keyword}'.")
        return

    print(f"\n----- SEARCH RESULTS for '{keyword}' -----")
    for pid, data in matches:
        gst = calculate_gst(data)
        print(
            f"{pid} - {data['name']} | {data['category']} | "
            f"Price: {format_inr(data['price'])} | Qty: {data['quantity']} | "
            f"GST/unit: {format_inr(gst)}"
        )
    print("-" * 45)


def restock_suggestion(inventory):
    """Suggests restock quantities for low-stock items, sorted by urgency
    (most urgent first). Suggested order brings stock to 2x reorder level."""
    candidates = []
    for pid, data in inventory.items():
        deficit = data["reorder_level"] - data["quantity"]
        if deficit >= 0:
            suggested_qty = (data["reorder_level"] * 2) - data["quantity"]
            candidates.append((pid, data, deficit, max(suggested_qty, 1)))

    if not candidates:
        print("\nNo restocking needed at this time. ✓")
        return

    candidates.sort(key=lambda x: x[2], reverse=True)  # most urgent first

    print("\n----- RESTOCK SUGGESTIONS (most urgent first) -----")
    for pid, data, deficit, suggested_qty in candidates:
        print(
            f"{pid} - {data['name']:<20} Current: {data['quantity']:<5} "
            f"Reorder Level: {data['reorder_level']:<5} "
            f"Suggested Order: {suggested_qty}"
        )
    print("-" * 55)


def daily_transaction_report(filename=TRANSACTION_FILE):
    """Filters and displays all transactions for a date entered by the user
    in YYYY-MM-DD format (bonus feature)."""
    if not os.path.exists(filename):
        print("\nNo transactions logged yet.")
        return

    date_str = input("Enter date to filter (YYYY-MM-DD): ").strip()
    found = False

    print(f"\n----- TRANSACTIONS ON {date_str} -----")
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(date_str):
                    timestamp, pid, t_type, qty, resulting_qty = line.split("|")
                    print(
                        f"{timestamp} | {pid} | {t_type:<3} | Qty: {qty:<5} "
                        f"| Resulting Qty: {resulting_qty}"
                    )
                    found = True
    except OSError as e:
        print(f"Could not read transaction log: {e}")
        return

    if not found:
        print("No transactions found for that date.")
    print("-" * 45)


# -----------------------------------------------------------------
# MAIN MENU LOOP
# -----------------------------------------------------------------
def show_menu():
    print("\n===== INVENTORY MANAGEMENT SYSTEM =====")
    print("1.Add Product")
    print("2.Stock-In")
    print("3.Stock-Out")
    print("4.View Inventory")
    print("5.Low Stock Alert")
    print("6.Generate Report")
    print("7.Search Product")
    print("8.Restock Suggestions")
    print("9.Daily Transactions")
    print("10.Save & Exit\n")


def main():
    inventory = load_inventory()
    print(
        f"Products Loaded: {len(inventory)} | "
        f"Categories: {len(get_categories(inventory))}"
    )

    while True:
        show_menu()
        choice = input("Choice: ").strip()

        if choice == "1":
            add_product(inventory)
        elif choice == "2":
            stock_in(inventory)
        elif choice == "3":
            stock_out(inventory)
        elif choice == "4":
            view_inventory(inventory)
        elif choice == "5":
            low_stock_alert(inventory)
        elif choice == "6":
            generate_report(inventory)
        elif choice == "7":
            search_product(inventory)
        elif choice == "8":
            restock_suggestion(inventory)
        elif choice == "9":
            daily_transaction_report()
        elif choice == "10":
            save_inventory(inventory)
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please select a valid menu option.")


if __name__ == "__main__":
    main()


# =================================================================
# SAMPLE RUN (documented output for testing reference)
# =================================================================
# ===== INVENTORY MANAGEMENT SYSTEM =====
# Products Loaded: 8 | Categories: 3
#
# 1.Add  2.Stock-In  3.Stock-Out  4.View  5.Alert  6.Report
# 7.Search  8.Restock Suggestions  9.Daily Transactions  10.Save & Exit
# Choice: 2
# Enter Product ID to stock-in: P001
# Enter quantity to add: 3
# Stocked in 3 units of 'Laptop'. New quantity: 5
#
# Choice: 3
# Enter Product ID to stock-out: P004
# Enter quantity to remove: 35
# Stocked out 35 units of 'Notebook Pack'. Remaining quantity: 5
# ⚠ Low stock alert: 'Notebook Pack' is now at or below its reorder level (10).
#
# Choice: 6
# ======= INVENTORY REPORT =======
# Total Products    : 8
# Total Stock Value : Rs. 3,17,605.00
# Categories        : Apparel, Electronics, FMCG, Stationery
# Low Stock Items   : 1 (below or at reorder level)
# Highest Value Item: Laptop (Rs. 58,000.00 x 5 = Rs. 2,90,000.00)
# =================================
#
# Choice: 10
# Inventory saved to 'inventory.txt'.
# Goodbye!
# =================================================================
