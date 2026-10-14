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
    / "eada_sport_summary_2024.csv"
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
# SPORTS IN EADA
# --------------------------------------------------

SPORTS = [
    "Archery",
    "Badminton",
    "Baseball",
    "Basketball",
    "Beach Volleyball",
    "Bowling",
    "All Track Combined",
    "Diving",
    "Equestrian",
    "Fencing",
    "Field Hockey",
    "Football",
    "Golf",
    "Gymnastics",
    "Ice Hockey",
    "Lacrosse",
    "Rifle",
    "Rodeo",
    "Rowing",
    "Sailing",
    "Skiing",
    "Soccer",
    "Softball",
    "Squash",
    "Swimming and Diving",
    "Swimming",
    "Synchronized Swimming",
    "Table Tennis",
    "Team Handball",
    "Tennis",
    "Track and Field Indoor",
    "Track and Field Outdoor",
    "Track and Field X Country",
    "Volleyball",
    "Water Polo",
    "Weight Lifting",
    "Wrestling",
    "Other Sports",
]


# --------------------------------------------------
# HELPER FUNCTION
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
# READ EADA
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

        school_total_expenses = number(
            row["Grand Total Expenses"]
        )

        # ------------------------------------------
        # PROCESS EACH SPORT
        # ------------------------------------------

        for sport in SPORTS:

            men_participation = number(
                row.get(
                    f"{sport} Men's Team Participation"
                )
            )

            women_participation = number(
                row.get(
                    f"{sport} Women's Team Participation"
                )
            )

            coed_men = number(
                row.get(
                    f"{sport} Coed Team Men Participation"
                )
            )

            coed_women = number(
                row.get(
                    f"{sport} Coed Team Women Participation"
                )
            )

            total_participation = number(
                row.get(
                    f"{sport} Total Participation"
                )
            )

            # If EADA total is blank, calculate it.
            if total_participation == 0:
                total_participation = (
                    men_participation
                    + women_participation
                    + coed_men
                    + coed_women
                )

            # --------------------------------------
            # FINANCIAL DATA
            # --------------------------------------

            men_revenue = number(
                row.get(
                    f"{sport} Men's Team Revenue"
                )
            )

            women_revenue = number(
                row.get(
                    f"{sport} Women's Team Revenue"
                )
            )

            coed_revenue = number(
                row.get(
                    f"{sport} Coed Team Revenue"
                )
            )

            total_revenue = number(
                row.get(
                    f"{sport} Total Revenue"
                )
            )

            men_operating = number(
                row.get(
                    f"{sport} Men's Team Operating Expenses"
                )
            )

            women_operating = number(
                row.get(
                    f"{sport} Women's Team Operating Expenses"
                )
            )

            coed_operating = number(
                row.get(
                    f"{sport} Coed Team Operating Expenses"
                )
            )

            total_operating = number(
                row.get(
                    f"{sport} Total Operating Expenses"
                )
            )

            men_expenses = number(
                row.get(
                    f"{sport} Men's Team Expenses"
                )
            )

            women_expenses = number(
                row.get(
                    f"{sport} Women's Team Expenses"
                )
            )

            coed_expenses = number(
                row.get(
                    f"{sport} Coed Team Expenses"
                )
            )

            total_expenses = number(
                row.get(
                    f"{sport} Total Expenses"
                )
            )

            # Skip sports the school doesn't sponsor.
            if (
                total_participation == 0
                and total_revenue == 0
                and total_expenses == 0
            ):
                continue

            # --------------------------------------
            # CALCULATED METRICS
            # --------------------------------------

            if total_participation > 0:

                expense_per_athlete = round(
                    total_expenses
                    / total_participation,
                    2
                )

                operating_per_athlete = round(
                    total_operating
                    / total_participation,
                    2
                )

            else:
                expense_per_athlete = 0
                operating_per_athlete = 0

            if school_total_expenses > 0:

                percent_school_expenses = round(
                    (
                        total_expenses
                        / school_total_expenses
                    ) * 100,
                    2
                )

            else:
                percent_school_expenses = 0

            # --------------------------------------
            # SAVE SPORT RECORD
            # --------------------------------------

            results.append({

                "school_id": school_id,
                "school_name": institution,
                "survey_year": row["Survey Year"],
                "sport": sport,

                "men_participation":
                    men_participation,

                "women_participation":
                    women_participation,

                "coed_men_participation":
                    coed_men,

                "coed_women_participation":
                    coed_women,

                "total_participation":
                    total_participation,

                "men_revenue":
                    men_revenue,

                "women_revenue":
                    women_revenue,

                "coed_revenue":
                    coed_revenue,

                "total_revenue":
                    total_revenue,

                "men_operating_expenses":
                    men_operating,

                "women_operating_expenses":
                    women_operating,

                "coed_operating_expenses":
                    coed_operating,

                "total_operating_expenses":
                    total_operating,

                "men_total_expenses":
                    men_expenses,

                "women_total_expenses":
                    women_expenses,

                "coed_total_expenses":
                    coed_expenses,

                "total_expenses":
                    total_expenses,

                "expense_per_athlete":
                    expense_per_athlete,

                "operating_per_athlete":
                    operating_per_athlete,

                "percent_school_expenses":
                    percent_school_expenses,
            })


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

fieldnames = [
    "school_id",
    "school_name",
    "survey_year",
    "sport",
    "men_participation",
    "women_participation",
    "coed_men_participation",
    "coed_women_participation",
    "total_participation",
    "men_revenue",
    "women_revenue",
    "coed_revenue",
    "total_revenue",
    "men_operating_expenses",
    "women_operating_expenses",
    "coed_operating_expenses",
    "total_operating_expenses",
    "men_total_expenses",
    "women_total_expenses",
    "coed_total_expenses",
    "total_expenses",
    "expense_per_athlete",
    "operating_per_athlete",
    "percent_school_expenses",
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
# CREATE TEAM-LEVEL DATA
# --------------------------------------------------

TEAM_OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_team_summary_2024.csv"
)

team_results = []

for record in results:

    # Men's team
    if (
        record["men_participation"] > 0
        or record["men_total_expenses"] > 0
    ):

        men_expense_per_athlete = 0

        if record["men_participation"] > 0:
            men_expense_per_athlete = round(
                record["men_total_expenses"]
                / record["men_participation"],
                2
            )

        team_results.append({
            "school_id": record["school_id"],
            "school_name": record["school_name"],
            "survey_year": record["survey_year"],
            "sport": record["sport"],
            "team": "Men",
            "participants": record["men_participation"],
            "revenue": record["men_revenue"],
            "operating_expenses":
                record["men_operating_expenses"],
            "total_expenses":
                record["men_total_expenses"],
            "expense_per_athlete":
                men_expense_per_athlete,
        })

    # Women's team
    if (
        record["women_participation"] > 0
        or record["women_total_expenses"] > 0
    ):

        women_expense_per_athlete = 0

        if record["women_participation"] > 0:
            women_expense_per_athlete = round(
                record["women_total_expenses"]
                / record["women_participation"],
                2
            )

        team_results.append({
            "school_id": record["school_id"],
            "school_name": record["school_name"],
            "survey_year": record["survey_year"],
            "sport": record["sport"],
            "team": "Women",
            "participants": record["women_participation"],
            "revenue": record["women_revenue"],
            "operating_expenses":
                record["women_operating_expenses"],
            "total_expenses":
                record["women_total_expenses"],
            "expense_per_athlete":
                women_expense_per_athlete,
        })

    # Coed team
    coed_participants = (
        record["coed_men_participation"]
        + record["coed_women_participation"]
    )

    if (
        coed_participants > 0
        or record["coed_total_expenses"] > 0
    ):

        coed_expense_per_athlete = 0

        if coed_participants > 0:
            coed_expense_per_athlete = round(
                record["coed_total_expenses"]
                / coed_participants,
                2
            )

        team_results.append({
            "school_id": record["school_id"],
            "school_name": record["school_name"],
            "survey_year": record["survey_year"],
            "sport": record["sport"],
            "team": "Coed",
            "participants": coed_participants,
            "revenue": record["coed_revenue"],
            "operating_expenses":
                record["coed_operating_expenses"],
            "total_expenses":
                record["coed_total_expenses"],
            "expense_per_athlete":
                coed_expense_per_athlete,
        })


# --------------------------------------------------
# SAVE TEAM-LEVEL CSV
# --------------------------------------------------

team_fieldnames = [
    "school_id",
    "school_name",
    "survey_year",
    "sport",
    "team",
    "participants",
    "revenue",
    "operating_expenses",
    "total_expenses",
    "expense_per_athlete",
]

with open(
    TEAM_OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=team_fieldnames
    )

    writer.writeheader()
    writer.writerows(team_results)


# --------------------------------------------------
# DISPLAY SONOMA TEAM DATA
# --------------------------------------------------

print()
print("SONOMA STATE TEAM-LEVEL DATA")
print("============================")

for team in team_results:

    if team["school_id"] == "SSU":

        print(
            f"{team['team']} | "
            f"{team['sport']} | "
            f"Athletes: {team['participants']} | "
            f"Expenses: ${team['total_expenses']:,.0f} | "
            f"Operating: ${team['operating_expenses']:,.0f}"
        )

print()
print(f"Team records created: {len(team_results)}")
print()
print("TEAM DATA SAVED TO:")
print(TEAM_OUTPUT_FILE)
# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print()
print("EADA SPORT-LEVEL PROCESSOR")
print("==========================")
print(f"Sport records created: {len(results)}")
print()

for record in results:

    print(
        f"{record['school_id']} | "
        f"{record['sport']} | "
        f"Athletes: {record['total_participation']} | "
        f"Expenses: ${record['total_expenses']:,.0f}"
    )

print()
print("==========================")
print("SPORT DATA SAVED TO:")
print(OUTPUT_FILE)