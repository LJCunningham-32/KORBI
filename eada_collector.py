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
    / "eada_financial_summary_2024.csv"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SCHOOLS WE WANT
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
# HELPER
# --------------------------------------------------

def number(value):
    """
    Convert EADA number fields into integers.
    Blank values become zero.
    """
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
# READ EADA DATA
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

        # Ignore community colleges, blanks,
        # and anything outside our target group.
        if institution not in TARGET_SCHOOLS:
            continue

        school_id = TARGET_SCHOOLS[institution]

        men_athletes = number(
            row["Unduplicated Count Men's Participation"]
        )

        women_athletes = number(
            row["Unduplicated Count Women's Participation"]
        )

        total_athletes = men_athletes + women_athletes

        revenue = number(
            row["Grand Total Revenue"]
        )

        expenses = number(
            row["Grand Total Expenses"]
        )

        operating_expenses = number(
            row["Grand Total Operating Expenses"]
        )

        athletic_aid = (
            number(row["Men's Team Athletic Student Aid"])
            + number(row["Women's Team Athletic Student Aid"])
            + number(row["Coed Team Athletic Student Aid"])
        )

        recruiting_expenses = (
            number(row["Men's Team Recruiting Expenses"])
            + number(row["Women's Team Recruiting Expenses"])
            + number(row["Coed Team Recruiting Expenses"])
        )

        net_result = revenue - expenses

        if total_athletes > 0:
            revenue_per_athlete = round(
                revenue / total_athletes,
                2
            )

            expense_per_athlete = round(
                expenses / total_athletes,
                2
            )
        else:
            revenue_per_athlete = 0
            expense_per_athlete = 0

        results.append({
            "school_id": school_id,
            "school_name": institution,
            "survey_year": row["Survey Year"],
            "classification": row["Classification Name"],
            "male_athletes": men_athletes,
            "female_athletes": women_athletes,
            "total_athletes": total_athletes,
            "athletics_revenue": revenue,
            "athletics_expenses": expenses,
            "net_reported_result": net_result,
            "operating_expenses": operating_expenses,
            "athletic_aid": athletic_aid,
            "recruiting_expenses": recruiting_expenses,
            "revenue_per_athlete": revenue_per_athlete,
            "expense_per_athlete": expense_per_athlete,
        })


# --------------------------------------------------
# SAVE PROCESSED DATA
# --------------------------------------------------

fieldnames = [
    "school_id",
    "school_name",
    "survey_year",
    "classification",
    "male_athletes",
    "female_athletes",
    "total_athletes",
    "athletics_revenue",
    "athletics_expenses",
    "net_reported_result",
    "operating_expenses",
    "athletic_aid",
    "recruiting_expenses",
    "revenue_per_athlete",
    "expense_per_athlete",
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
# SHOW RESULTS
# --------------------------------------------------

print()
print("EADA FINANCIAL PROCESSOR")
print("========================")
print(f"Schools processed: {len(results)}")
print()

for school in results:

    print(school["school_name"])

    print(
        f"  Athletes: "
        f"{school['total_athletes']:,}"
    )

    print(
        f"  Revenue: "
        f"${school['athletics_revenue']:,.0f}"
    )

    print(
        f"  Expenses: "
        f"${school['athletics_expenses']:,.0f}"
    )

    print(
        f"  Operating: "
        f"${school['operating_expenses']:,.0f}"
    )

    print(
        f"  Athletic Aid: "
        f"${school['athletic_aid']:,.0f}"
    )

    print(
        f"  Recruiting: "
        f"${school['recruiting_expenses']:,.0f}"
    )

    print(
        f"  Expense/Athlete: "
        f"${school['expense_per_athlete']:,.0f}"
    )

    print()

print("========================")
print("PROCESSED DATA SAVED TO:")
print(OUTPUT_FILE)