import csv
from pathlib import Path

# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

FINANCIAL_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_financial_summary_2024.csv"
)

RECONCILIATION_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_reconciliation_2024.csv"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_peer_comparison_2024.csv"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# NUMBER CLEANER
# --------------------------------------------------

def number(value):

    if value is None:
        return 0

    cleaned = (
        str(value)
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    if cleaned == "":
        return 0

    try:
        return float(cleaned)
    except ValueError:
        return 0


# --------------------------------------------------
# LOAD FINANCIAL SUMMARY
# --------------------------------------------------

financial_data = {}

with open(
    FINANCIAL_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        school_id = row["school_id"]

        financial_data[school_id] = row


# --------------------------------------------------
# LOAD RECONCILIATION DATA
# --------------------------------------------------

results = []

with open(
    RECONCILIATION_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        school_id = row["school_id"]

        if school_id not in financial_data:
            continue

        financial = financial_data[school_id]

        total_athletes = int(
            number(financial["total_athletes"])
        )

        total_expenses = number(
            row["grand_total_expenses"]
        )

        unallocated_expenses = number(
            row["not_allocated_expenses"]
        )

        team_expenses = (
            number(row["men_team_expenses"])
            + number(row["women_team_expenses"])
            + number(row["coed_team_expenses"])
        )

        unallocated_percent = number(
            row["unallocated_percent"]
        )

        # ------------------------------------------
        # CALCULATED METRICS
        # ------------------------------------------

        if total_athletes > 0:

            expense_per_athlete = round(
                total_expenses / total_athletes,
                2
            )

            unallocated_per_athlete = round(
                unallocated_expenses / total_athletes,
                2
            )

            team_expense_per_athlete = round(
                team_expenses / total_athletes,
                2
            )

        else:

            expense_per_athlete = 0
            unallocated_per_athlete = 0
            team_expense_per_athlete = 0

        team_percent = round(
            100 - unallocated_percent,
            2
        )

        results.append({

            "school_id":
                school_id,

            "school_name":
                row["school_name"],

            "survey_year":
                row["survey_year"],

            "total_athletes":
                total_athletes,

            "total_expenses":
                round(total_expenses),

            "team_expenses":
                round(team_expenses),

            "unallocated_expenses":
                round(unallocated_expenses),

            "team_percent":
                team_percent,

            "unallocated_percent":
                unallocated_percent,

            "expense_per_athlete":
                expense_per_athlete,

            "team_expense_per_athlete":
                team_expense_per_athlete,

            "unallocated_per_athlete":
                unallocated_per_athlete,

        })


# --------------------------------------------------
# SORT BY UNALLOCATED %
# HIGHEST FIRST
# --------------------------------------------------

results.sort(
    key=lambda school: school["unallocated_percent"],
    reverse=True
)


# --------------------------------------------------
# ADD RANK
# --------------------------------------------------

for rank, school in enumerate(
    results,
    start=1
):

    school["unallocated_rank"] = rank


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

fieldnames = [
    "unallocated_rank",
    "school_id",
    "school_name",
    "survey_year",
    "total_athletes",
    "total_expenses",
    "team_expenses",
    "unallocated_expenses",
    "team_percent",
    "unallocated_percent",
    "expense_per_athlete",
    "team_expense_per_athlete",
    "unallocated_per_athlete",
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
# DISPLAY FULL PEER COMPARISON
# --------------------------------------------------

print()
print("EADA PEER COST STRUCTURE")
print("========================")

for school in results:

    print()

    print(
        f"#{school['unallocated_rank']} "
        f"{school['school_id']} | "
        f"{school['school_name']}"
    )

    print(
        f"  Athletes: "
        f"{school['total_athletes']:,}"
    )

    print(
        f"  Total Expenses: "
        f"${school['total_expenses']:,.0f}"
    )

    print(
        f"  Team Expenses: "
        f"${school['team_expenses']:,.0f}"
    )

    print(
        f"  Unallocated Expenses: "
        f"${school['unallocated_expenses']:,.0f}"
    )

    print(
        f"  Team Share: "
        f"{school['team_percent']:.2f}%"
    )

    print(
        f"  Unallocated Share: "
        f"{school['unallocated_percent']:.2f}%"
    )

    print(
        f"  Expense/Athlete: "
        f"${school['expense_per_athlete']:,.0f}"
    )

    print(
        f"  Team Expense/Athlete: "
        f"${school['team_expense_per_athlete']:,.0f}"
    )

    print(
        f"  Unallocated/Athlete: "
        f"${school['unallocated_per_athlete']:,.0f}"
    )


# --------------------------------------------------
# CSU ALL-SCHOOL AVERAGE
# Includes Sonoma
# Excludes GVSU
# --------------------------------------------------

csu_all_schools = [
    school
    for school in results
    if school["school_id"] != "GVSU"
]

if csu_all_schools:

    all_avg_unallocated_percent = round(
        sum(
            school["unallocated_percent"]
            for school in csu_all_schools
        )
        / len(csu_all_schools),
        2
    )

    all_avg_expense_per_athlete = round(
        sum(
            school["expense_per_athlete"]
            for school in csu_all_schools
        )
        / len(csu_all_schools),
        2
    )

    all_avg_team_expense_per_athlete = round(
        sum(
            school["team_expense_per_athlete"]
            for school in csu_all_schools
        )
        / len(csu_all_schools),
        2
    )

    all_avg_unallocated_per_athlete = round(
        sum(
            school["unallocated_per_athlete"]
            for school in csu_all_schools
        )
        / len(csu_all_schools),
        2
    )

    print()
    print("========================")
    print("CSU D-II ALL-SCHOOL AVERAGE")
    print("INCLUDING SONOMA")
    print("========================")

    print(
        f"Schools: "
        f"{len(csu_all_schools)}"
    )

    print(
        f"Average Unallocated Share: "
        f"{all_avg_unallocated_percent:.2f}%"
    )

    print(
        f"Average Expense/Athlete: "
        f"${all_avg_expense_per_athlete:,.0f}"
    )

    print(
        f"Average Team Expense/Athlete: "
        f"${all_avg_team_expense_per_athlete:,.0f}"
    )

    print(
        f"Average Unallocated/Athlete: "
        f"${all_avg_unallocated_per_athlete:,.0f}"
    )


# --------------------------------------------------
# CSU PEER BENCHMARK
# Excludes Sonoma and GVSU
# --------------------------------------------------

csu_peer_schools = [
    school
    for school in results
    if school["school_id"] not in ["GVSU", "SSU"]
]

if csu_peer_schools:

    peer_avg_unallocated_percent = round(
        sum(
            school["unallocated_percent"]
            for school in csu_peer_schools
        )
        / len(csu_peer_schools),
        2
    )

    peer_avg_expense_per_athlete = round(
        sum(
            school["expense_per_athlete"]
            for school in csu_peer_schools
        )
        / len(csu_peer_schools),
        2
    )

    peer_avg_team_expense_per_athlete = round(
        sum(
            school["team_expense_per_athlete"]
            for school in csu_peer_schools
        )
        / len(csu_peer_schools),
        2
    )

    peer_avg_unallocated_per_athlete = round(
        sum(
            school["unallocated_per_athlete"]
            for school in csu_peer_schools
        )
        / len(csu_peer_schools),
        2
    )

    print()
    print("========================")
    print("CSU D-II PEER BENCHMARK")
    print("EXCLUDING SONOMA")
    print("========================")

    print(
        f"Peer Schools: "
        f"{len(csu_peer_schools)}"
    )

    print(
        f"Average Unallocated Share: "
        f"{peer_avg_unallocated_percent:.2f}%"
    )

    print(
        f"Average Expense/Athlete: "
        f"${peer_avg_expense_per_athlete:,.0f}"
    )

    print(
        f"Average Team Expense/Athlete: "
        f"${peer_avg_team_expense_per_athlete:,.0f}"
    )

    print(
        f"Average Unallocated/Athlete: "
        f"${peer_avg_unallocated_per_athlete:,.0f}"
    )


# --------------------------------------------------
# SONOMA VS CSU PEERS
# --------------------------------------------------

sonoma = next(
    (
        school
        for school in results
        if school["school_id"] == "SSU"
    ),
    None
)

if sonoma and csu_peer_schools:

    print()
    print("========================")
    print("SONOMA VS CSU PEERS")
    print("========================")

    print(
        f"Unallocated Share: "
        f"{sonoma['unallocated_percent']:.2f}% "
        f"vs {peer_avg_unallocated_percent:.2f}%"
    )

    print(
        f"Expense/Athlete: "
        f"${sonoma['expense_per_athlete']:,.0f} "
        f"vs ${peer_avg_expense_per_athlete:,.0f}"
    )

    print(
        f"Team Expense/Athlete: "
        f"${sonoma['team_expense_per_athlete']:,.0f} "
        f"vs ${peer_avg_team_expense_per_athlete:,.0f}"
    )

    print(
        f"Unallocated/Athlete: "
        f"${sonoma['unallocated_per_athlete']:,.0f} "
        f"vs ${peer_avg_unallocated_per_athlete:,.0f}"
    )

    print()
    print("DIFFERENCE FROM PEER BENCHMARK")
    print("------------------------------")

    print(
        f"Unallocated Share Difference: "
        f"{sonoma['unallocated_percent'] - peer_avg_unallocated_percent:+.2f} "
        f"percentage points"
    )

    print(
        f"Expense/Athlete Difference: "
        f"${sonoma['expense_per_athlete'] - peer_avg_expense_per_athlete:+,.0f}"
    )

    print(
        f"Team Expense/Athlete Difference: "
        f"${sonoma['team_expense_per_athlete'] - peer_avg_team_expense_per_athlete:+,.0f}"
    )

    print(
        f"Unallocated/Athlete Difference: "
        f"${sonoma['unallocated_per_athlete'] - peer_avg_unallocated_per_athlete:+,.0f}"
    )


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print()
print("========================")
print("PEER COMPARISON SAVED TO:")
print(OUTPUT_FILE)