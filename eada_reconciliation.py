import csv
from pathlib import Path

# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

EADA_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Raw"
    / "All_Data_Combined_2024.csv"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_reconciliation_2024.csv"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# TARGET SCHOOLS
# --------------------------------------------------

TARGET_SCHOOLS = {
    "California State Polytechnic University-Humboldt": "CPH",
    "California State Polytechnic University-Pomona": "CPP",
    "California State University-Chico": "CHICO",
    "California State University-Dominguez Hills": "CSUDH",
    "California State University-East Bay": "CSUEB",
    "California State University-Los Angeles": "CSULA",
    "California State University-Monterey Bay": "CSUMB",
    "California State University-San Bernardino": "CSUSB",
    "California State University-San Marcos": "CSUSM",
    "California State University-Stanislaus": "STAN",
    "San Francisco State University": "SFSU",
    "Sonoma State University": "SSU",
    "Grand Valley State University": "GVSU",
}


# --------------------------------------------------
# NUMBER CLEANER
# --------------------------------------------------

def number(value):

    if value is None:
        return 0

    cleaned = (
        value.replace("$", "")
        .replace(",", "")
        .strip()
    )

    if cleaned == "":
        return 0

    try:
        return int(float(cleaned))
    except ValueError:
        return 0


# --------------------------------------------------
# PROCESS DATA
# --------------------------------------------------

results = []

with open(
    EADA_FILE,
    "r",
    encoding="utf-8-sig",
    errors="replace"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        institution = row["Institution Name"].strip()

        if institution not in TARGET_SCHOOLS:
            continue

        school_id = TARGET_SCHOOLS[institution]

        men_expenses = number(
            row["Total Men's Team Expenses"]
        )

        women_expenses = number(
            row["Total Women's Team Expenses"]
        )

        coed_expenses = number(
            row["Total Coed Team Expenses"]
        )

        not_allocated = number(
            row["Not Allocated by Sex/Sport Expenses"]
        )

        grand_total = number(
            row["Grand Total Expenses"]
        )

        calculated_total = (
            men_expenses
            + women_expenses
            + coed_expenses
            + not_allocated
        )

        difference = grand_total - calculated_total

        if grand_total > 0:
            unallocated_percent = round(
                (not_allocated / grand_total) * 100,
                2
            )
        else:
            unallocated_percent = 0

        status = (
            "MATCH"
            if difference == 0
            else "CHECK"
        )

        results.append({
            "school_id": school_id,
            "school_name": institution,
            "survey_year": row["Survey Year"],
            "men_team_expenses": men_expenses,
            "women_team_expenses": women_expenses,
            "coed_team_expenses": coed_expenses,
            "not_allocated_expenses": not_allocated,
            "grand_total_expenses": grand_total,
            "calculated_total": calculated_total,
            "difference": difference,
            "unallocated_percent":
                unallocated_percent,
            "reconciliation_status": status,
        })


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

fieldnames = [
    "school_id",
    "school_name",
    "survey_year",
    "men_team_expenses",
    "women_team_expenses",
    "coed_team_expenses",
    "not_allocated_expenses",
    "grand_total_expenses",
    "calculated_total",
    "difference",
    "unallocated_percent",
    "reconciliation_status",
]

with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print()
print("EADA EXPENSE RECONCILIATION")
print("===========================")

for school in results:

    print()
    print(
        f"{school['school_id']} | "
        f"{school['school_name']}"
    )

    print(
        f"  Men's Team Expenses: "
        f"${school['men_team_expenses']:,.0f}"
    )

    print(
        f"  Women's Team Expenses: "
        f"${school['women_team_expenses']:,.0f}"
    )

    print(
        f"  Coed Team Expenses: "
        f"${school['coed_team_expenses']:,.0f}"
    )

    print(
        f"  Not Allocated: "
        f"${school['not_allocated_expenses']:,.0f}"
    )

    print(
        f"  Grand Total: "
        f"${school['grand_total_expenses']:,.0f}"
    )

    print(
        f"  Calculated Total: "
        f"${school['calculated_total']:,.0f}"
    )

    print(
        f"  Difference: "
        f"${school['difference']:,.0f}"
    )

    print(
        f"  Unallocated %: "
        f"{school['unallocated_percent']:.2f}%"
    )

    print(
        f"  Status: "
        f"{school['reconciliation_status']}"
    )

print()
print("===========================")
print("RECONCILIATION DATA SAVED TO:")
print(OUTPUT_FILE)