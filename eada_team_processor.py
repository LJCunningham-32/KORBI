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
    / "eada_team_summary_2024.csv"
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
# SPORTS
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
# PROCESS EADA DATA
# --------------------------------------------------

team_results = []

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

        for sport in SPORTS:

            # --------------------------------------
            # MEN
            # --------------------------------------

            men_participants = number(
                row.get(
                    f"{sport} Men's Team Participation"
                )
            )

            men_revenue = number(
                row.get(
                    f"{sport} Men's Team Revenue"
                )
            )

            men_operating = number(
                row.get(
                    f"{sport} Men's Team Operating Expenses"
                )
            )

            men_expenses = number(
                row.get(
                    f"{sport} Men's Team Expenses"
                )
            )

            if men_participants > 0 or men_expenses > 0:

                expense_per_athlete = 0

                if men_participants > 0:
                    expense_per_athlete = round(
                        men_expenses / men_participants,
                        2
                    )

                team_results.append({
                    "school_id": school_id,
                    "school_name": institution,
                    "survey_year": row["Survey Year"],
                    "sport": sport,
                    "team": "Men",
                    "participants": men_participants,
                    "revenue": men_revenue,
                    "operating_expenses": men_operating,
                    "total_expenses": men_expenses,
                    "expense_per_athlete":
                        expense_per_athlete,
                })

            # --------------------------------------
            # WOMEN
            # --------------------------------------

            women_participants = number(
                row.get(
                    f"{sport} Women's Team Participation"
                )
            )

            women_revenue = number(
                row.get(
                    f"{sport} Women's Team Revenue"
                )
            )

            women_operating = number(
                row.get(
                    f"{sport} Women's Team Operating Expenses"
                )
            )

            women_expenses = number(
                row.get(
                    f"{sport} Women's Team Expenses"
                )
            )

            if women_participants > 0 or women_expenses > 0:

                expense_per_athlete = 0

                if women_participants > 0:
                    expense_per_athlete = round(
                        women_expenses / women_participants,
                        2
                    )

                team_results.append({
                    "school_id": school_id,
                    "school_name": institution,
                    "survey_year": row["Survey Year"],
                    "sport": sport,
                    "team": "Women",
                    "participants": women_participants,
                    "revenue": women_revenue,
                    "operating_expenses": women_operating,
                    "total_expenses": women_expenses,
                    "expense_per_athlete":
                        expense_per_athlete,
                })


# --------------------------------------------------
# SAVE TEAM DATA
# --------------------------------------------------

fieldnames = [
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
    writer.writerows(team_results)


# --------------------------------------------------
# SHOW SONOMA
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
print("============================")
print(f"Total team records: {len(team_results)}")
print()
print("TEAM DATA SAVED TO:")
print(OUTPUT_FILE)