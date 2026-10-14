import csv
import statistics
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
    / "eada_cost_drivers_2024.csv"
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


CSU_PEER_IDS = {
    "CPH",
    "CPP",
    "CHICO",
    "CSUDH",
    "CSUEB",
    "CSULA",
    "CSUMB",
    "CSUSB",
    "CSUSM",
    "STAN",
    "SFSU",
}


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
# NORMALIZE HEADER NAMES
# --------------------------------------------------
#
# EADA contains some headers with leading spaces.
# We remove leading/trailing spaces before processing.
# --------------------------------------------------

def clean_row(row):

    cleaned = {}

    for key, value in row.items():

        if key is None:
            continue

        clean_key = key.strip()

        cleaned[clean_key] = value

    return cleaned


# --------------------------------------------------
# SAFE FIELD READER
# --------------------------------------------------

def get_value(row, field_name):

    return number(
        row.get(field_name, 0)
    )


# --------------------------------------------------
# LOAD EADA
# --------------------------------------------------

results = []

with open(
    EADA_FILE,
    "r",
    encoding="utf-8-sig",
    errors="replace"
) as file:

    reader = csv.DictReader(file)

    for raw_row in reader:

        row = clean_row(raw_row)

        institution = (
            row.get("Institution Name", "")
            .strip()
        )

        if institution not in TARGET_SCHOOLS:
            continue

        school_id = TARGET_SCHOOLS[institution]

        # ------------------------------------------
        # ATHLETES
        # ------------------------------------------

        male_athletes = get_value(
            row,
            "Unduplicated Count Men's Participation"
        )

        female_athletes = get_value(
            row,
            "Unduplicated Count Women's Participation"
        )

        total_athletes = (
            male_athletes
            + female_athletes
        )

        # ------------------------------------------
        # TOTAL REVENUE / EXPENSES
        # ------------------------------------------

        total_revenue = get_value(
            row,
            "Grand Total Revenue"
        )

        total_expenses = get_value(
            row,
            "Grand Total Expenses"
        )

        # ------------------------------------------
        # TEAM EXPENSES
        # ------------------------------------------

        men_team_expenses = get_value(
            row,
            "Total Men's Team Expenses"
        )

        women_team_expenses = get_value(
            row,
            "Total Women's Team Expenses"
        )

        coed_team_expenses = get_value(
            row,
            "Total Coed Team Expenses"
        )

        team_expenses = (
            men_team_expenses
            + women_team_expenses
            + coed_team_expenses
        )

        # ------------------------------------------
        # UNALLOCATED EXPENSES
        # ------------------------------------------

        unallocated_expenses = get_value(
            row,
            "Not Allocated by Sex/Sport Expenses"
        )

        # ------------------------------------------
        # OPERATING EXPENSES
        # ------------------------------------------

        operating_expenses = get_value(
            row,
            "Grand Total Operating Expenses"
        )

        # ------------------------------------------
        # ATHLETIC AID
        # ------------------------------------------

        men_aid = get_value(
            row,
            "Men's Team Athletic Student Aid"
        )

        women_aid = get_value(
            row,
            "Women's Team Athletic Student Aid"
        )

        coed_aid = get_value(
            row,
            "Coed Team Athletic Student Aid"
        )

        athletic_aid = (
            men_aid
            + women_aid
            + coed_aid
        )

        # ------------------------------------------
        # RECRUITING
        # ------------------------------------------

        men_recruiting = get_value(
            row,
            "Men's Team Recruiting Expenses"
        )

        women_recruiting = get_value(
            row,
            "Women's Team Recruiting Expenses"
        )

        coed_recruiting = get_value(
            row,
            "Coed Team Recruiting Expenses"
        )

        recruiting_expenses = (
            men_recruiting
            + women_recruiting
            + coed_recruiting
        )

        # ==========================================
        # HEAD COACH COMPENSATION
        # ==========================================
        #
        # We now use:
        #
        # Average salary PER HEAD COACH
        # x
        # Number of head coaches included
        #
        # These fields are unique and avoid the
        # duplicate "per FTE" header problem.
        # ==========================================

        men_head_avg_salary = get_value(
            row,
            "Men's Team Average Annual Institutional Salary per Head Coach"
        )

        men_head_count = get_value(
            row,
            "Men's Team Number of Head Coaches Included in Average"
        )

        women_head_avg_salary = get_value(
            row,
            "Women's Team Average Annual Institutional Salary per Head Coach"
        )

        women_head_count = get_value(
            row,
            "Women's Team Number of Head Coaches Included in Average"
        )

        coed_head_avg_salary = get_value(
            row,
            "Coed Team Average Annual Institutional Salary per Head Coach"
        )

        coed_head_count = get_value(
            row,
            "Coed Team Number of Head Coaches Included in Average"
        )

        men_head_comp = (
            men_head_avg_salary
            * men_head_count
        )

        women_head_comp = (
            women_head_avg_salary
            * women_head_count
        )

        coed_head_comp = (
            coed_head_avg_salary
            * coed_head_count
        )

        estimated_head_coach_comp = (
            men_head_comp
            + women_head_comp
            + coed_head_comp
        )

        total_head_coaches = (
            men_head_count
            + women_head_count
            + coed_head_count
        )

        # ==========================================
        # ASSISTANT COACH COMPENSATION
        # ==========================================

        men_assistant_avg_salary = get_value(
            row,
            "Men's Team Average Annual Institutional Salary per Assistant Coach"
        )

        men_assistant_count = get_value(
            row,
            "Men's Team Number of Assistant Coaches Included in Average"
        )

        women_assistant_avg_salary = get_value(
            row,
            "Women's Team Average Annual Institutional Salary per Assistant Coach"
        )

        women_assistant_count = get_value(
            row,
            "Women's Team Number of Assistant Coaches Included in Average"
        )

        coed_assistant_avg_salary = get_value(
            row,
            "Coed Team Average Annual Institutional Salary per Assistant Coach"
        )

        coed_assistant_count = get_value(
            row,
            "Coed Team Number of Assistant Coaches Included in Average"
        )

        men_assistant_comp = (
            men_assistant_avg_salary
            * men_assistant_count
        )

        women_assistant_comp = (
            women_assistant_avg_salary
            * women_assistant_count
        )

        coed_assistant_comp = (
            coed_assistant_avg_salary
            * coed_assistant_count
        )

        estimated_assistant_coach_comp = (
            men_assistant_comp
            + women_assistant_comp
            + coed_assistant_comp
        )

        total_assistant_coaches = (
            men_assistant_count
            + women_assistant_count
            + coed_assistant_count
        )

        # ------------------------------------------
        # TOTAL COACHING COMPENSATION
        # ------------------------------------------

        estimated_total_coaching_comp = (
            estimated_head_coach_comp
            + estimated_assistant_coach_comp
        )

        # ------------------------------------------
        # PERCENTAGES OF TOTAL EXPENSES
        # ------------------------------------------

        if total_expenses > 0:

            team_expense_pct = (
                team_expenses
                / total_expenses
                * 100
            )

            unallocated_pct = (
                unallocated_expenses
                / total_expenses
                * 100
            )

            operating_pct = (
                operating_expenses
                / total_expenses
                * 100
            )

            athletic_aid_pct = (
                athletic_aid
                / total_expenses
                * 100
            )

            recruiting_pct = (
                recruiting_expenses
                / total_expenses
                * 100
            )

            head_coach_comp_pct = (
                estimated_head_coach_comp
                / total_expenses
                * 100
            )

            assistant_coach_comp_pct = (
                estimated_assistant_coach_comp
                / total_expenses
                * 100
            )

            total_coaching_comp_pct = (
                estimated_total_coaching_comp
                / total_expenses
                * 100
            )

        else:

            team_expense_pct = 0
            unallocated_pct = 0
            operating_pct = 0
            athletic_aid_pct = 0
            recruiting_pct = 0
            head_coach_comp_pct = 0
            assistant_coach_comp_pct = 0
            total_coaching_comp_pct = 0

        # ------------------------------------------
        # PER ATHLETE METRICS
        # ------------------------------------------

        if total_athletes > 0:

            total_expense_per_athlete = (
                total_expenses
                / total_athletes
            )

            operating_per_athlete = (
                operating_expenses
                / total_athletes
            )

            aid_per_athlete = (
                athletic_aid
                / total_athletes
            )

            recruiting_per_athlete = (
                recruiting_expenses
                / total_athletes
            )

            coaching_comp_per_athlete = (
                estimated_total_coaching_comp
                / total_athletes
            )

        else:

            total_expense_per_athlete = 0
            operating_per_athlete = 0
            aid_per_athlete = 0
            recruiting_per_athlete = 0
            coaching_comp_per_athlete = 0

        # ------------------------------------------
        # STORE RESULT
        # ------------------------------------------

        results.append({

            "school_id":
                school_id,

            "school_name":
                institution,

            "survey_year":
                row.get("Survey Year", ""),

            "total_athletes":
                round(total_athletes),

            "total_revenue":
                round(total_revenue),

            "total_expenses":
                round(total_expenses),

            "team_expenses":
                round(team_expenses),

            "team_expense_pct":
                round(team_expense_pct, 2),

            "unallocated_expenses":
                round(unallocated_expenses),

            "unallocated_pct":
                round(unallocated_pct, 2),

            "operating_expenses":
                round(operating_expenses),

            "operating_pct":
                round(operating_pct, 2),

            "athletic_aid":
                round(athletic_aid),

            "athletic_aid_pct":
                round(athletic_aid_pct, 2),

            "recruiting_expenses":
                round(recruiting_expenses),

            "recruiting_pct":
                round(recruiting_pct, 2),

            "head_coach_count":
                round(total_head_coaches, 2),

            "estimated_head_coach_comp":
                round(estimated_head_coach_comp),

            "head_coach_comp_pct":
                round(head_coach_comp_pct, 2),

            "assistant_coach_count":
                round(total_assistant_coaches, 2),

            "estimated_assistant_coach_comp":
                round(estimated_assistant_coach_comp),

            "assistant_coach_comp_pct":
                round(
                    assistant_coach_comp_pct,
                    2
                ),

            "estimated_total_coaching_comp":
                round(estimated_total_coaching_comp),

            "total_coaching_comp_pct":
                round(total_coaching_comp_pct, 2),

            "total_expense_per_athlete":
                round(total_expense_per_athlete, 2),

            "operating_per_athlete":
                round(operating_per_athlete, 2),

            "aid_per_athlete":
                round(aid_per_athlete, 2),

            "recruiting_per_athlete":
                round(recruiting_per_athlete, 2),

            "coaching_comp_per_athlete":
                round(coaching_comp_per_athlete, 2),
        })


# --------------------------------------------------
# SORT
# --------------------------------------------------

results.sort(
    key=lambda row: row["school_id"]
)


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

fieldnames = list(results[0].keys())

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
# FIND SONOMA
# --------------------------------------------------

sonoma = next(
    row
    for row in results
    if row["school_id"] == "SSU"
)


# --------------------------------------------------
# CSU PEER BENCHMARK
# --------------------------------------------------

peers = [
    row
    for row in results
    if row["school_id"] in CSU_PEER_IDS
]


def peer_median(field):

    values = [
        row[field]
        for row in peers
        if row[field] > 0
    ]

    if not values:
        return 0

    return statistics.median(values)


peer_operating_pct = peer_median(
    "operating_pct"
)

peer_aid_pct = peer_median(
    "athletic_aid_pct"
)

peer_recruiting_pct = peer_median(
    "recruiting_pct"
)

peer_coaching_pct = peer_median(
    "total_coaching_comp_pct"
)

peer_unallocated_pct = peer_median(
    "unallocated_pct"
)

peer_coaching_per_athlete = peer_median(
    "coaching_comp_per_athlete"
)


# --------------------------------------------------
# DISPLAY SONOMA
# --------------------------------------------------

print()
print("SONOMA STATE COST DRIVERS")
print("=========================")

print(
    f"Total Athletes: "
    f"{sonoma['total_athletes']:,}"
)

print(
    f"Total Expenses: "
    f"${sonoma['total_expenses']:,.0f}"
)


print()
print("TEAM / SHARED STRUCTURE")
print("-----------------------")

print(
    f"Team Expenses: "
    f"${sonoma['team_expenses']:,.0f} "
    f"({sonoma['team_expense_pct']:.2f}%)"
)

print(
    f"Unallocated Expenses: "
    f"${sonoma['unallocated_expenses']:,.0f} "
    f"({sonoma['unallocated_pct']:.2f}%)"
)


print()
print("IDENTIFIABLE COST DRIVERS")
print("-------------------------")

print(
    f"Operating Expenses: "
    f"${sonoma['operating_expenses']:,.0f} "
    f"({sonoma['operating_pct']:.2f}%)"
)

print(
    f"Athletic Aid: "
    f"${sonoma['athletic_aid']:,.0f} "
    f"({sonoma['athletic_aid_pct']:.2f}%)"
)

print(
    f"Recruiting: "
    f"${sonoma['recruiting_expenses']:,.0f} "
    f"({sonoma['recruiting_pct']:.2f}%)"
)


print()
print("COACHING COMPENSATION")
print("---------------------")

print(
    f"Head Coaches Reported: "
    f"{sonoma['head_coach_count']:.0f}"
)

print(
    f"Estimated Head Coach Compensation: "
    f"${sonoma['estimated_head_coach_comp']:,.0f}"
)

print(
    f"Assistant Coaches Reported: "
    f"{sonoma['assistant_coach_count']:.0f}"
)

print(
    f"Estimated Assistant Coach Compensation: "
    f"${sonoma['estimated_assistant_coach_comp']:,.0f}"
)

print(
    f"Estimated Total Coaching Compensation: "
    f"${sonoma['estimated_total_coaching_comp']:,.0f} "
    f"({sonoma['total_coaching_comp_pct']:.2f}% "
    f"of total expenses)"
)


print()
print("PER ATHLETE")
print("-----------")

print(
    f"Total Expense/Athlete: "
    f"${sonoma['total_expense_per_athlete']:,.0f}"
)

print(
    f"Operating/Athlete: "
    f"${sonoma['operating_per_athlete']:,.0f}"
)

print(
    f"Aid/Athlete: "
    f"${sonoma['aid_per_athlete']:,.0f}"
)

print(
    f"Recruiting/Athlete: "
    f"${sonoma['recruiting_per_athlete']:,.0f}"
)

print(
    f"Coaching Compensation/Athlete: "
    f"${sonoma['coaching_comp_per_athlete']:,.0f}"
)


# --------------------------------------------------
# SONOMA VS CSU PEER MEDIAN
# --------------------------------------------------

print()
print("=========================")
print("SONOMA VS CSU PEER MEDIAN")
print("=========================")

print(
    f"Operating Share: "
    f"{sonoma['operating_pct']:.2f}% "
    f"vs {peer_operating_pct:.2f}%"
)

print(
    f"Athletic Aid Share: "
    f"{sonoma['athletic_aid_pct']:.2f}% "
    f"vs {peer_aid_pct:.2f}%"
)

print(
    f"Recruiting Share: "
    f"{sonoma['recruiting_pct']:.2f}% "
    f"vs {peer_recruiting_pct:.2f}%"
)

print(
    f"Coaching Compensation Share: "
    f"{sonoma['total_coaching_comp_pct']:.2f}% "
    f"vs {peer_coaching_pct:.2f}%"
)

print(
    f"Unallocated Share: "
    f"{sonoma['unallocated_pct']:.2f}% "
    f"vs {peer_unallocated_pct:.2f}%"
)

print(
    f"Coaching Compensation/Athlete: "
    f"${sonoma['coaching_comp_per_athlete']:,.0f} "
    f"vs ${peer_coaching_per_athlete:,.0f}"
)


# --------------------------------------------------
# IMPORTANT ACCOUNTING WARNING
# --------------------------------------------------

print()
print("=========================")
print("ACCOUNTING NOTE")
print("=========================")

print(
    "Operating, athletic aid, recruiting, coaching "
    "compensation, team expenses, and unallocated "
    "expenses are NOT all mutually exclusive buckets."
)

print(
    "Do not add them together to calculate a remainder."
)

print(
    "They are being preserved separately so the future "
    "budget model does not double-count EADA expenses."
)


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print()
print("=========================")
print("COST DRIVER DATA SAVED TO:")
print(OUTPUT_FILE)