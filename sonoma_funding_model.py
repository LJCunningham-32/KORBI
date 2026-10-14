import csv
from pathlib import Path


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "sonoma_funding_model.csv"
)


# --------------------------------------------------
# SOURCE INFORMATION
# --------------------------------------------------

SOURCE_FILE = "SSU_ATHLETICS_WHITE_PAPER_2026.pdf"

VERIFICATION_STATUS = "VERIFIED_FROM_SOURCE"


# --------------------------------------------------
# FUNDING RECORDS
# --------------------------------------------------
#
# IMPORTANT:
#
# These records represent DIFFERENT financial models.
#
# HISTORICAL:
# FY24/25 actual/reported funding sources.
#
# ONE_TIME_REBUILD:
# Separate $8M state funding designated for
# Division II athletics.
#
# We do NOT assume the historical FY24/25 funding
# structure automatically funds the proposed
# reinstated athletics budget.
# --------------------------------------------------

FUNDING_RECORDS = [

    # ------------------------------------------------
    # HISTORICAL FY24/25 FUNDING
    # ------------------------------------------------

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "INSTITUTIONAL_SUPPORT",
        "funding_source": "Operating Fund Allocation",
        "amount": 2813619,
        "recurring_status": "HISTORICAL_RECURRING",
        "restricted_use": "Operations and Scholarships",
        "source_page": 7,
        "notes": (
            "Historical athletics funding source "
            "reported for FY24/25."
        ),
    },

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "STUDENT_FEES",
        "funding_source": "IRA Fee Allocation - Annual (62.25%)",
        "amount": 2125149,
        "recurring_status": "HISTORICAL_RECURRING",
        "restricted_use": "Athletics",
        "source_page": 7,
        "notes": (
            "Annual IRA allocation. White Paper "
            "identifies Athletics as permanently "
            "funded at 62.25% under the 2003 "
            "student fee referendum."
        ),
    },

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "STUDENT_FEES",
        "funding_source": "IRA Fee Allocation - One-Time",
        "amount": 213864,
        "recurring_status": "ONE_TIME",
        "restricted_use": "Athletics",
        "source_page": 7,
        "notes": (
            "One-time IRA allocation reported "
            "for FY24/25."
        ),
    },

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "FUNDRAISING_SCHOLARSHIP",
        "funding_source": (
            "Fundraising and Scholarship - Operating Fund"
        ),
        "amount": 659550,
        "recurring_status": "HISTORICAL",
        "restricted_use": "Not fully specified",
        "source_page": 7,
        "notes": (
            "Preserved exactly as categorized "
            "in the White Paper."
        ),
    },

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "FUNDRAISING_SCHOLARSHIP",
        "funding_source": (
            "Fundraising and Scholarship - Non-Operating Fund"
        ),
        "amount": 108857,
        "recurring_status": "HISTORICAL",
        "restricted_use": "Not fully specified",
        "source_page": 7,
        "notes": (
            "Preserved exactly as categorized "
            "in the White Paper."
        ),
    },

    {
        "model_type": "HISTORICAL_FUNDING",
        "fiscal_period": "FY24/25",
        "funding_category": "OTHER_REVENUE",
        "funding_source": (
            "Other Financial Sources (incl. Ticket Sales)"
        ),
        "amount": 403344,
        "recurring_status": "HISTORICAL",
        "restricted_use": "Not fully specified",
        "source_page": 7,
        "notes": (
            "Includes ticket sales. White Paper "
            "does not provide a complete breakdown "
            "of this amount on Page 7."
        ),
    },

    # ------------------------------------------------
    # ONE-TIME $8M REBUILD FUNDING
    # ------------------------------------------------

    {
        "model_type": "ONE_TIME_REBUILD",
        "fiscal_period": "MULTI_YEAR",
        "funding_category": "STATE_ONE_TIME",
        "funding_source": (
            "CSU One-Time Funding for DII Athletics"
        ),
        "amount": 8000000,
        "recurring_status": "ONE_TIME",
        "restricted_use": (
            "Division II Athletics Rebuild"
        ),
        "source_page": 8,
        "notes": (
            "Separate one-time funding pool. "
            "Do not treat as an $8M annual "
            "athletics operating budget."
        ),
    },
]


# --------------------------------------------------
# PROPOSED USES OF ONE-TIME FUNDING
# --------------------------------------------------
#
# These are NOT additional funding sources.
#
# They are proposed uses of the $8M pool.
#
# Ranges are preserved where the source gives ranges.
# --------------------------------------------------

ONE_TIME_USES = [

    {
        "use_category": "EXTERNAL_REVENUE_DEVELOPMENT",
        "description": (
            "Athletics development position and "
            "Associate Athletic Director for External Affairs "
            "expenses over three years"
        ),
        "minimum_amount": 300000,
        "maximum_amount": 300000,
        "source_page": 8,
    },

    {
        "use_category": "STARTUP_EQUIPMENT",
        "description": (
            "Start-up equipment and supplies "
            "for athletics programs"
        ),
        "minimum_amount": 200000,
        "maximum_amount": 200000,
        "source_page": 8,
    },

    {
        "use_category": "FACILITIES",
        "description": (
            "New track and artificial turf infield "
            "and related amenities"
        ),
        "minimum_amount": 3500000,
        "maximum_amount": 5000000,
        "source_page": 8,
    },

    {
        "use_category": "FACILITIES",
        "description": (
            "Athletics weight room, locker rooms, "
            "and athletic training room renovations"
        ),
        "minimum_amount": 1000000,
        "maximum_amount": 1500000,
        "source_page": 9,
    },

    {
        "use_category": "FACILITIES",
        "description": "New gym floor",
        "minimum_amount": 500000,
        "maximum_amount": 1000000,
        "source_page": 9,
    },
]


# --------------------------------------------------
# VALIDATE HISTORICAL FUNDING
# --------------------------------------------------

def validate_historical_funding():

    historical_records = [
        row
        for row in FUNDING_RECORDS
        if row["model_type"] == "HISTORICAL_FUNDING"
    ]

    calculated_total = sum(
        row["amount"]
        for row in historical_records
    )

    reported_total = 6324383

    variance = (
        calculated_total
        - reported_total
    )

    return (
        calculated_total,
        reported_total,
        variance
    )


# --------------------------------------------------
# VALIDATE ONE-TIME FUND
# --------------------------------------------------

def validate_one_time_fund():

    minimum_committed = sum(
        row["minimum_amount"]
        for row in ONE_TIME_USES
    )

    maximum_committed = sum(
        row["maximum_amount"]
        for row in ONE_TIME_USES
    )

    total_fund = 8000000

    minimum_remaining = (
        total_fund
        - maximum_committed
    )

    maximum_remaining = (
        total_fund
        - minimum_committed
    )

    return (
        minimum_committed,
        maximum_committed,
        minimum_remaining,
        maximum_remaining,
    )


# --------------------------------------------------
# SAVE FUNDING MODEL
# --------------------------------------------------

def save_funding_model():

    fieldnames = [
        "institution",
        "record_type",
        "model_type",
        "fiscal_period",
        "funding_category",
        "funding_source",
        "amount",
        "minimum_amount",
        "maximum_amount",
        "recurring_status",
        "restricted_use",
        "source_file",
        "source_page",
        "verification_status",
        "notes",
    ]

    records = []

    # ------------------------------------------------
    # FUNDING SOURCES
    # ------------------------------------------------

    for row in FUNDING_RECORDS:

        records.append({

            "institution":
                "Sonoma State University",

            "record_type":
                "FUNDING_SOURCE",

            "model_type":
                row["model_type"],

            "fiscal_period":
                row["fiscal_period"],

            "funding_category":
                row["funding_category"],

            "funding_source":
                row["funding_source"],

            "amount":
                row["amount"],

            "minimum_amount":
                "",

            "maximum_amount":
                "",

            "recurring_status":
                row["recurring_status"],

            "restricted_use":
                row["restricted_use"],

            "source_file":
                SOURCE_FILE,

            "source_page":
                row["source_page"],

            "verification_status":
                VERIFICATION_STATUS,

            "notes":
                row["notes"],
        })

    # ------------------------------------------------
    # ONE-TIME FUND USES
    # ------------------------------------------------

    for row in ONE_TIME_USES:

        records.append({

            "institution":
                "Sonoma State University",

            "record_type":
                "PROPOSED_USE",

            "model_type":
                "ONE_TIME_REBUILD",

            "fiscal_period":
                "MULTI_YEAR",

            "funding_category":
                row["use_category"],

            "funding_source":
                row["description"],

            "amount":
                "",

            "minimum_amount":
                row["minimum_amount"],

            "maximum_amount":
                row["maximum_amount"],

            "recurring_status":
                "ONE_TIME",

            "restricted_use":
                row["description"],

            "source_file":
                SOURCE_FILE,

            "source_page":
                row["source_page"],

            "verification_status":
                VERIFICATION_STATUS,

            "notes":
                (
                    "Proposed use of the $8M "
                    "one-time athletics funding pool."
                ),
        })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            records
        )

    return records


# --------------------------------------------------
# SHOW HISTORICAL FUNDING
# --------------------------------------------------

def show_historical_funding():

    print()
    print("FY24/25 HISTORICAL FUNDING")
    print("==========================")

    for row in FUNDING_RECORDS:

        if row["model_type"] != "HISTORICAL_FUNDING":
            continue

        print(
            f"{row['funding_source']:<55} "
            f"${row['amount']:>12,.0f}"
        )


# --------------------------------------------------
# SHOW ONE-TIME FUND
# --------------------------------------------------

def show_one_time_fund():

    print()
    print("$8M ONE-TIME REBUILD FUND")
    print("=========================")

    for row in ONE_TIME_USES:

        minimum = row["minimum_amount"]
        maximum = row["maximum_amount"]

        if minimum == maximum:

            amount_display = (
                f"${minimum:,.0f}"
            )

        else:

            amount_display = (
                f"${minimum:,.0f} - "
                f"${maximum:,.0f}"
            )

        print()
        print(
            row["description"]
        )

        print(
            f"Proposed Amount: "
            f"{amount_display}"
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print()
    print("SONOMA ATHLETICS FUNDING MODEL")
    print("=============================")

    (
        historical_calculated,
        historical_reported,
        historical_variance,
    ) = validate_historical_funding()

    print()
    print("HISTORICAL FUNDING VALIDATION")
    print("=============================")

    print(
        f"Calculated FY24/25 Funding: "
        f"${historical_calculated:,.0f}"
    )

    print(
        f"Reported FY24/25 Funding:   "
        f"${historical_reported:,.0f}"
    )

    print(
        f"Variance:                   "
        f"${historical_variance:,.0f}"
    )

    if historical_variance == 0:

        print(
            "Status: MATCH"
        )

    else:

        print(
            "Status: REVIEW REQUIRED"
        )

    (
        minimum_committed,
        maximum_committed,
        minimum_remaining,
        maximum_remaining,
    ) = validate_one_time_fund()

    print()
    print("ONE-TIME FUNDING CHECK")
    print("======================")

    print(
        f"Total One-Time Fund:        "
        f"${8000000:,.0f}"
    )

    print(
        f"Minimum Proposed Uses:      "
        f"${minimum_committed:,.0f}"
    )

    print(
        f"Maximum Proposed Uses:      "
        f"${maximum_committed:,.0f}"
    )

    print(
        f"Remaining Range:            "
        f"${minimum_remaining:,.0f} to "
        f"${maximum_remaining:,.0f}"
    )

    records = save_funding_model()

    print()
    print(
        f"Structured Funding Records: "
        f"{len(records):,}"
    )

    print()
    print("Saved To:")
    print(OUTPUT_FILE)

    show_historical_funding()

    show_one_time_fund()


if __name__ == "__main__":
    main()