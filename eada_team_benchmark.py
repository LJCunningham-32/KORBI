import csv
import statistics
from pathlib import Path


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

TEAM_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_team_summary_2024.csv"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "eada_team_benchmark_2024.csv"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SCHOOL GROUPS
# --------------------------------------------------

SONOMA_ID = "SSU"

# CSU Division II peers.
# Sonoma is excluded because Sonoma is the school
# we are benchmarking.
# GVSU is excluded because it is a national benchmark,
# not a CSU peer.
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
# LOAD TEAM DATA
# --------------------------------------------------

team_data = []

with open(
    TEAM_FILE,
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        participants = int(
            number(row["participants"])
        )

        total_expenses = number(
            row["total_expenses"]
        )

        operating_expenses = number(
            row["operating_expenses"]
        )

        # Calculate these ourselves so every school
        # is treated the same way.

        if participants > 0:

            expense_per_athlete = (
                total_expenses / participants
            )

            operating_per_athlete = (
                operating_expenses / participants
            )

        else:

            expense_per_athlete = 0
            operating_per_athlete = 0

        team_data.append({

            "school_id":
                row["school_id"],

            "school_name":
                row["school_name"],

            "survey_year":
                row["survey_year"],

            "sport":
                row["sport"],

            "team":
                row["team"],

            "participants":
                participants,

            "revenue":
                number(row["revenue"]),

            "operating_expenses":
                operating_expenses,

            "total_expenses":
                total_expenses,

            "expense_per_athlete":
                expense_per_athlete,

            "operating_per_athlete":
                operating_per_athlete,
        })


# --------------------------------------------------
# FIND SONOMA TEAMS
# --------------------------------------------------

sonoma_teams = [
    row
    for row in team_data
    if row["school_id"] == SONOMA_ID
]


# --------------------------------------------------
# BENCHMARK EACH SONOMA TEAM
# --------------------------------------------------

results = []

for sonoma in sonoma_teams:

    sport = sonoma["sport"]
    team = sonoma["team"]

    # Find CSU schools sponsoring the exact same
    # sport and men's/women's team.

    peers = [
        row
        for row in team_data
        if (
            row["school_id"] in CSU_PEER_IDS
            and row["sport"] == sport
            and row["team"] == team
            and row["participants"] > 0
        )
    ]

    peer_count = len(peers)

    # ----------------------------------------------
    # PEER VALUES
    # ----------------------------------------------

    peer_total_expenses = [
        peer["total_expenses"]
        for peer in peers
    ]

    peer_expense_per_athlete = [
        peer["expense_per_athlete"]
        for peer in peers
    ]

    peer_operating_expenses = [
        peer["operating_expenses"]
        for peer in peers
    ]

    peer_operating_per_athlete = [
        peer["operating_per_athlete"]
        for peer in peers
    ]

    peer_participants = [
        peer["participants"]
        for peer in peers
    ]

    # ----------------------------------------------
    # MEDIANS
    # ----------------------------------------------

    if peer_count > 0:

        median_total_expenses = statistics.median(
            peer_total_expenses
        )

        median_expense_per_athlete = statistics.median(
            peer_expense_per_athlete
        )

        median_operating_expenses = statistics.median(
            peer_operating_expenses
        )

        median_operating_per_athlete = statistics.median(
            peer_operating_per_athlete
        )

        median_participants = statistics.median(
            peer_participants
        )

        average_expense_per_athlete = statistics.mean(
            peer_expense_per_athlete
        )

        average_operating_per_athlete = statistics.mean(
            peer_operating_per_athlete
        )

        min_expense_per_athlete = min(
            peer_expense_per_athlete
        )

        max_expense_per_athlete = max(
            peer_expense_per_athlete
        )

    else:

        median_total_expenses = 0
        median_expense_per_athlete = 0
        median_operating_expenses = 0
        median_operating_per_athlete = 0
        median_participants = 0
        average_expense_per_athlete = 0
        average_operating_per_athlete = 0
        min_expense_per_athlete = 0
        max_expense_per_athlete = 0

    # ----------------------------------------------
    # SONOMA DIFFERENCES
    # ----------------------------------------------

    expense_per_athlete_difference = (
        sonoma["expense_per_athlete"]
        - median_expense_per_athlete
    )

    operating_per_athlete_difference = (
        sonoma["operating_per_athlete"]
        - median_operating_per_athlete
    )

    total_expense_difference = (
        sonoma["total_expenses"]
        - median_total_expenses
    )

    # Percentage difference from peer median

    if median_expense_per_athlete > 0:

        expense_per_athlete_percent_difference = (
            expense_per_athlete_difference
            / median_expense_per_athlete
            * 100
        )

    else:

        expense_per_athlete_percent_difference = 0

    if median_operating_per_athlete > 0:

        operating_per_athlete_percent_difference = (
            operating_per_athlete_difference
            / median_operating_per_athlete
            * 100
        )

    else:

        operating_per_athlete_percent_difference = 0

    # ----------------------------------------------
    # SIMPLE BENCHMARK LABEL
    # ----------------------------------------------
    #
    # This is NOT saying a team is good or bad.
    # It only describes spending relative to peers.
    #
    # Within +/- 10% = Near Peer Median
    # More than 10% = Above Peer Median
    # Less than -10% = Below Peer Median
    # ----------------------------------------------

    if peer_count == 0:

        benchmark_status = "NO PEER DATA"

    elif expense_per_athlete_percent_difference > 10:

        benchmark_status = "ABOVE PEER MEDIAN"

    elif expense_per_athlete_percent_difference < -10:

        benchmark_status = "BELOW PEER MEDIAN"

    else:

        benchmark_status = "NEAR PEER MEDIAN"

    # ----------------------------------------------
    # RANK SONOMA AGAINST PEERS
    # ----------------------------------------------

    comparison_values = [
        peer["expense_per_athlete"]
        for peer in peers
    ]

    comparison_values.append(
        sonoma["expense_per_athlete"]
    )

    # Highest expense/athlete gets rank 1.

    comparison_values.sort(
        reverse=True
    )

    if comparison_values:

        sonoma_rank = (
            comparison_values.index(
                sonoma["expense_per_athlete"]
            )
            + 1
        )

        total_schools_compared = len(
            comparison_values
        )

    else:

        sonoma_rank = 0
        total_schools_compared = 0

    # ----------------------------------------------
    # SAVE RESULT
    # ----------------------------------------------

    results.append({

        "sport":
            sport,

        "team":
            team,

        "sonoma_participants":
            sonoma["participants"],

        "peer_median_participants":
            round(median_participants, 1),

        "peer_school_count":
            peer_count,

        "sonoma_total_expenses":
            round(sonoma["total_expenses"]),

        "peer_median_total_expenses":
            round(median_total_expenses),

        "total_expense_difference":
            round(total_expense_difference),

        "sonoma_expense_per_athlete":
            round(
                sonoma["expense_per_athlete"],
                2
            ),

        "peer_median_expense_per_athlete":
            round(
                median_expense_per_athlete,
                2
            ),

        "peer_average_expense_per_athlete":
            round(
                average_expense_per_athlete,
                2
            ),

        "peer_min_expense_per_athlete":
            round(
                min_expense_per_athlete,
                2
            ),

        "peer_max_expense_per_athlete":
            round(
                max_expense_per_athlete,
                2
            ),

        "expense_per_athlete_difference":
            round(
                expense_per_athlete_difference,
                2
            ),

        "expense_per_athlete_percent_difference":
            round(
                expense_per_athlete_percent_difference,
                2
            ),

        "sonoma_operating_expenses":
            round(
                sonoma["operating_expenses"]
            ),

        "peer_median_operating_expenses":
            round(
                median_operating_expenses
            ),

        "sonoma_operating_per_athlete":
            round(
                sonoma["operating_per_athlete"],
                2
            ),

        "peer_median_operating_per_athlete":
            round(
                median_operating_per_athlete,
                2
            ),

        "peer_average_operating_per_athlete":
            round(
                average_operating_per_athlete,
                2
            ),

        "operating_per_athlete_difference":
            round(
                operating_per_athlete_difference,
                2
            ),

        "operating_per_athlete_percent_difference":
            round(
                operating_per_athlete_percent_difference,
                2
            ),

        "sonoma_expense_rank_high_to_low":
            sonoma_rank,

        "schools_compared":
            total_schools_compared,

        "benchmark_status":
            benchmark_status,
    })


# --------------------------------------------------
# SORT RESULTS
# --------------------------------------------------

results.sort(
    key=lambda row: (
        row["team"],
        row["sport"]
    )
)


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

fieldnames = [
    "sport",
    "team",
    "sonoma_participants",
    "peer_median_participants",
    "peer_school_count",
    "sonoma_total_expenses",
    "peer_median_total_expenses",
    "total_expense_difference",
    "sonoma_expense_per_athlete",
    "peer_median_expense_per_athlete",
    "peer_average_expense_per_athlete",
    "peer_min_expense_per_athlete",
    "peer_max_expense_per_athlete",
    "expense_per_athlete_difference",
    "expense_per_athlete_percent_difference",
    "sonoma_operating_expenses",
    "peer_median_operating_expenses",
    "sonoma_operating_per_athlete",
    "peer_median_operating_per_athlete",
    "peer_average_operating_per_athlete",
    "operating_per_athlete_difference",
    "operating_per_athlete_percent_difference",
    "sonoma_expense_rank_high_to_low",
    "schools_compared",
    "benchmark_status",
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
print("SONOMA STATE TEAM BENCHMARK")
print("===========================")
print(
    "Benchmark: Same sport + same men's/women's team"
)
print(
    "Peers: 11 CSU Division II schools excluding Sonoma"
)
print(
    "Primary comparison: Expense per athlete vs peer median"
)
print()


for row in results:

    print(
        f"{row['team']} | {row['sport']}"
    )

    print(
        f"  Sonoma Athletes: "
        f"{row['sonoma_participants']}"
    )

    print(
        f"  Peer Schools Sponsoring Team: "
        f"{row['peer_school_count']}"
    )

    print(
        f"  Peer Median Athletes: "
        f"{row['peer_median_participants']:.1f}"
    )

    print(
        f"  Sonoma Total Expenses: "
        f"${row['sonoma_total_expenses']:,.0f}"
    )

    print(
        f"  Peer Median Total Expenses: "
        f"${row['peer_median_total_expenses']:,.0f}"
    )

    print(
        f"  Sonoma Expense/Athlete: "
        f"${row['sonoma_expense_per_athlete']:,.0f}"
    )

    print(
        f"  Peer Median Expense/Athlete: "
        f"${row['peer_median_expense_per_athlete']:,.0f}"
    )

    print(
        f"  Difference: "
        f"${row['expense_per_athlete_difference']:+,.0f} "
        f"({row['expense_per_athlete_percent_difference']:+.1f}%)"
    )

    print(
        f"  Sonoma Operating/Athlete: "
        f"${row['sonoma_operating_per_athlete']:,.0f}"
    )

    print(
        f"  Peer Median Operating/Athlete: "
        f"${row['peer_median_operating_per_athlete']:,.0f}"
    )

    print(
        f"  Operating Difference: "
        f"${row['operating_per_athlete_difference']:+,.0f} "
        f"({row['operating_per_athlete_percent_difference']:+.1f}%)"
    )

    print(
        f"  Expense Rank: "
        f"#{row['sonoma_expense_rank_high_to_low']} "
        f"of {row['schools_compared']} "
        f"(highest to lowest)"
    )

    print(
        f"  Status: "
        f"{row['benchmark_status']}"
    )

    print()


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

above = [
    row
    for row in results
    if row["benchmark_status"] == "ABOVE PEER MEDIAN"
]

near = [
    row
    for row in results
    if row["benchmark_status"] == "NEAR PEER MEDIAN"
]

below = [
    row
    for row in results
    if row["benchmark_status"] == "BELOW PEER MEDIAN"
]

no_data = [
    row
    for row in results
    if row["benchmark_status"] == "NO PEER DATA"
]


print("===========================")
print("SONOMA TEAM SUMMARY")
print("===========================")

print(
    f"Teams Analyzed: "
    f"{len(results)}"
)

print(
    f"Above Peer Median: "
    f"{len(above)}"
)

print(
    f"Near Peer Median: "
    f"{len(near)}"
)

print(
    f"Below Peer Median: "
    f"{len(below)}"
)

print(
    f"No Peer Data: "
    f"{len(no_data)}"
)


# --------------------------------------------------
# LARGEST DIFFERENCES
# --------------------------------------------------

valid_results = [
    row
    for row in results
    if row["peer_school_count"] > 0
]

if valid_results:

    highest_above = max(
        valid_results,
        key=lambda row:
            row[
                "expense_per_athlete_percent_difference"
            ]
    )

    lowest_below = min(
        valid_results,
        key=lambda row:
            row[
                "expense_per_athlete_percent_difference"
            ]
    )

    print()
    print("===========================")
    print("LARGEST VARIANCES")
    print("===========================")

    print(
        f"Highest Above Peer Median: "
        f"{highest_above['team']} "
        f"{highest_above['sport']} | "
        f"{highest_above['expense_per_athlete_percent_difference']:+.1f}%"
    )

    print(
        f"Lowest vs Peer Median: "
        f"{lowest_below['team']} "
        f"{lowest_below['sport']} | "
        f"{lowest_below['expense_per_athlete_percent_difference']:+.1f}%"
    )


# --------------------------------------------------
# FINISHED
# --------------------------------------------------

print()
print("===========================")
print("TEAM BENCHMARK SAVED TO:")
print(OUTPUT_FILE)