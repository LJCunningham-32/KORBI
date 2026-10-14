import csv
from datetime import date
from pathlib import Path


# ==================================================
# KORBI
# Knowledge & Operations Resource
# for Business Intelligence
#
# FUTURE EXPENSE PLANNING
#
# TEST MODE
# ==================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"

CATEGORY_BUDGET_FILE = (
    PROCESSED_FOLDER / "korbi_category_budgets.csv"
)

FUTURE_EXPENSE_FILE = (
    PROCESSED_FOLDER / "korbi_future_expenses.csv"
)


FUTURE_EXPENSE_FIELDS = [
    "expense_id",
    "entry_date",
    "expected_date",
    "program_code",
    "program_name",
    "expense_category",
    "expense_type",
    "vendor",
    "description",
    "amount",
    "confidence",
    "status",
    "entered_by",
    "notes",
]


# ==================================================
# HELPERS
# ==================================================

def read_csv(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(csv.DictReader(file))


def format_money(value):

    return f"${value:,.0f}"


# ==================================================
# CREATE FUTURE EXPENSE REGISTER
# ==================================================

def ensure_future_expense_file():

    if FUTURE_EXPENSE_FILE.exists():
        return

    with open(
        FUTURE_EXPENSE_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FUTURE_EXPENSE_FIELDS
        )

        writer.writeheader()


# ==================================================
# LOAD PROGRAMS
# ==================================================

def load_programs():

    rows = read_csv(
        CATEGORY_BUDGET_FILE
    )

    programs = {}

    for row in rows:

        programs[row["program_code"]] = {
            "program_name":
                row["program_name"],

            "expense_category":
                row["expense_category"],

            "budget":
                float(row["category_budget"]),
        }

    return programs


# ==================================================
# SELECT PROGRAM
# ==================================================

def choose_program(programs):

    codes = sorted(
        programs.keys(),
        key=lambda code:
            programs[code]["program_name"]
    )

    print()
    print("SELECT PROGRAM")
    print("==============")

    for number, code in enumerate(
        codes,
        start=1
    ):

        print(
            f"{number}. "
            f"{programs[code]['program_name']} "
            f"({code})"
        )

    while True:

        selection = input(
            "\nEnter program number: "
        ).strip()

        try:

            number = int(selection)

            if 1 <= number <= len(codes):
                return codes[number - 1]

        except ValueError:
            pass

        print(
            "Invalid selection. "
            "Enter one of the numbers shown."
        )


# ==================================================
# EXPENSE TYPE
# ==================================================

def choose_expense_type():

    types = {
        "1": "TRAVEL",
        "2": "EQUIPMENT",
        "3": "GAME_OPERATIONS",
        "4": "OFFICIALS",
        "5": "SUBSCRIPTION",
        "6": "RECRUITING",
        "7": "FACILITY / RENTAL",
        "8": "OTHER",
    }

    print()
    print("FUTURE EXPENSE TYPE")
    print("===================")

    print("1. Travel")
    print("2. Equipment")
    print("3. Game Operations")
    print("4. Officials")
    print("5. Subscription")
    print("6. Recruiting")
    print("7. Facility / Rental")
    print("8. Other")

    while True:

        selection = input(
            "\nEnter expense type number: "
        ).strip()

        if selection in types:
            return types[selection]

        print(
            "Invalid selection. Enter 1-8."
        )


# ==================================================
# CONFIDENCE LEVEL
# ==================================================

def choose_confidence():

    print()
    print("FORECAST CONFIDENCE")
    print("===================")

    print()
    print("1. HIGH - SCHEDULED")
    print(
        "   We know this expense is expected "
        "and have a strong cost estimate."
    )

    print()
    print("2. MEDIUM - EXPECTED")
    print(
        "   We reasonably expect this expense "
        "but the final amount may change."
    )

    print()
    print("3. LOW - PLANNING ESTIMATE")
    print(
        "   We believe this expense may occur, "
        "but timing or cost is uncertain."
    )

    while True:

        selection = input(
            "\nEnter confidence number (1-3): "
        ).strip()

        if selection == "1":
            return "HIGH"

        if selection == "2":
            return "MEDIUM"

        if selection == "3":
            return "LOW"

        print(
            "Invalid selection. Enter 1, 2, or 3."
        )


# ==================================================
# DATE ENTRY
# ==================================================

def get_expected_date():

    while True:

        value = input(
            "\nExpected expense date "
            "(YYYY-MM-DD): "
        ).strip()

        try:

            parsed = date.fromisoformat(value)

            return parsed.isoformat()

        except ValueError:

            print(
                "Enter the date as YYYY-MM-DD."
            )


# ==================================================
# AMOUNT ENTRY
# ==================================================

def get_amount():

    while True:

        value = input(
            "Expected amount: $"
        ).replace(
            ",",
            ""
        ).strip()

        try:

            amount = float(value)

            if amount > 0:
                return int(round(amount))

        except ValueError:
            pass

        print(
            "Enter a valid amount greater than zero."
        )


# ==================================================
# GENERATE EXPENSE ID
# ==================================================

def generate_expense_id():

    ensure_future_expense_file()

    rows = read_csv(
        FUTURE_EXPENSE_FILE
    )

    highest = 0

    for row in rows:

        expense_id = row.get(
            "expense_id",
            ""
        )

        if not expense_id.startswith(
            "FUT-"
        ):
            continue

        try:

            number = int(
                expense_id.split("-")[1]
            )

            highest = max(
                highest,
                number
            )

        except (ValueError, IndexError):
            pass

    return f"FUT-{highest + 1:04d}"


# ==================================================
# GET FUTURE EXPENSE
# ==================================================

def get_future_expense(
    program_code,
    program_info
):

    print()
    print("NEW FUTURE EXPENSE")
    print("==================")

    expense_type = (
        choose_expense_type()
    )

    vendor = input(
        "\nVendor / Payee "
        "(if known): "
    ).strip()

    description = input(
        "Description: "
    ).strip()

    expected_date = (
        get_expected_date()
    )

    amount = get_amount()

    confidence = (
        choose_confidence()
    )

    entered_by = input(
        "\nEntered by: "
    ).strip()

    notes = input(
        "Notes: "
    ).strip()

    return {
        "expense_id":
            generate_expense_id(),

        "entry_date":
            date.today().isoformat(),

        "expected_date":
            expected_date,

        "program_code":
            program_code,

        "program_name":
            program_info["program_name"],

        "expense_category":
            program_info["expense_category"],

        "expense_type":
            expense_type,

        "vendor":
            vendor,

        "description":
            description,

        "amount":
            amount,

        "confidence":
            confidence,

        "status":
            "PLANNED",

        "entered_by":
            entered_by,

        "notes":
            notes,
    }


# ==================================================
# DISPLAY EXPENSE
# ==================================================

def display_expense(expense):

    print()
    print("FUTURE EXPENSE REVIEW")
    print("=====================")

    print(
        f"Expense ID:       "
        f"{expense['expense_id']}"
    )

    print(
        f"Program:          "
        f"{expense['program_name']}"
    )

    print(
        f"Expense Type:     "
        f"{expense['expense_type']}"
    )

    print(
        f"Vendor / Payee:   "
        f"{expense['vendor']}"
    )

    print(
        f"Description:      "
        f"{expense['description']}"
    )

    print(
        f"Expected Date:    "
        f"{expense['expected_date']}"
    )

    print(
        f"Expected Amount:  "
        f"{format_money(expense['amount'])}"
    )

    print(
        f"Confidence:       "
        f"{expense['confidence']}"
    )

    print(
        f"Entered By:       "
        f"{expense['entered_by']}"
    )

    print(
        f"Status:           "
        f"{expense['status']}"
    )

    print(
        f"Notes:            "
        f"{expense['notes']}"
    )


# ==================================================
# SAVE EXPENSE
# ==================================================

def save_expense(expense):

    ensure_future_expense_file()

    with open(
        FUTURE_EXPENSE_FILE,
        "a",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FUTURE_EXPENSE_FIELDS
        )

        writer.writerow(expense)


# ==================================================
# CONFIRM SAVE
# ==================================================

def confirm_save():

    while True:

        answer = input(
            "\nSave future expense? (Y/N): "
        ).strip().upper()

        if answer == "Y":
            return True

        if answer == "N":
            return False

        print(
            "Enter Y or N."
        )


# ==================================================
# MAIN
# ==================================================

def run():

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()

    print("FUTURE EXPENSE PLANNING")
    print("=======================")

    print()

    print(
        "TEST MODE - Entries are planning "
        "data, not actual Sonoma State expenses."
    )

    programs = load_programs()

    program_code = (
        choose_program(programs)
    )

    program_info = (
        programs[program_code]
    )

    expense = get_future_expense(
        program_code,
        program_info
    )

    display_expense(expense)

    if confirm_save():

        save_expense(expense)

        print()
        print("FUTURE EXPENSE SAVED")
        print("====================")

        print(
            f"Expense ID: "
            f"{expense['expense_id']}"
        )

        print(
            f"Program:    "
            f"{expense['program_name']}"
        )

        print(
            f"Amount:     "
            f"{format_money(expense['amount'])}"
        )

        print(
            f"Confidence: "
            f"{expense['confidence']}"
        )

    else:

        print()
        print("EXPENSE NOT SAVED")
        print("=================")

        print(
            "No files were changed."
        )


if __name__ == "__main__":

    try:
        run()

    except Exception as error:

        print()
        print("KORBI FUTURE EXPENSE ERROR")
        print("==========================")
        print(error)