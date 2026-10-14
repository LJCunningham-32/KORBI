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
    / "sonoma_financial_history.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# FINANCIAL RECORDS
# --------------------------------------------------
#
# IMPORTANT:
# Every number must retain:
# - fiscal year
# - category
# - source
# - authority level
# - verification status
#
# We are NOT combining numbers from different
# accounting definitions.
# --------------------------------------------------

records = [

    # ==============================================
    # FY 2023-24
    # ==============================================

    {
        "fiscal_year": "2023-24",
        "category": "Athletics Campus-Based Fee Revenue",
        "amount": 2138643,
        "source_id": "SSU_FALL_2023_BUDGET_FORUM",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Campus Budget",
        "notes": (
            "Intercollegiate Athletics campus-based "
            "fee revenue reported in Sonoma State "
            "Fall 2023 budget planning materials."
        ),
    },

    # ==============================================
    # FY 2024-25 ATHLETICS FUNDING MODEL
    # ==============================================

    {
        "fiscal_year": "2024-25",
        "category": "Operating Fund Allocation",
        "amount": 2813619,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Operating fund allocation reported in "
            "Sonoma State Athletics White Paper."
        ),
    },

    {
        "fiscal_year": "2024-25",
        "category": "IRA Fee Allocation - Annual",
        "amount": 2125149,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Annual IRA allocation at 62.25%."
        ),
    },

    {
        "fiscal_year": "2024-25",
        "category": "IRA Fee Allocation - One-Time",
        "amount": 213864,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": "One-time IRA allocation.",
    },

    {
        "fiscal_year": "2024-25",
        "category": "Fundraising and Scholarship - Operating Fund",
        "amount": 659550,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Fundraising and scholarship funding "
            "reported within operating fund."
        ),
    },

    {
        "fiscal_year": "2024-25",
        "category": "Fundraising and Scholarship - Non-Operating Fund",
        "amount": 108857,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Fundraising and scholarship funding "
            "outside operating fund."
        ),
    },

    {
        "fiscal_year": "2024-25",
        "category": "Other Financial Sources",
        "amount": 403344,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Includes ticket sales and other "
            "financial sources."
        ),
    },

    {
        "fiscal_year": "2024-25",
        "category": "Total Athletics Funding Sources",
        "amount": 6324383,
        "source_id": "SSU_ATHLETICS_WHITE_PAPER_2026",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "Athletics Funding Source",
        "notes": (
            "Reported total of all FY24-25 athletics "
            "funding sources."
        ),
    },

    # ==============================================
    # 2024 EADA
    # ==============================================

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Total Athletics Expenses",
        "amount": 8863311,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": (
            "Do not directly compare to funding-source "
            "total without reconciling accounting "
            "definitions and reporting periods."
        ),
    },

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Team Expenses",
        "amount": 5371480,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": (
            "Men's + women's + coed team-specific "
            "expenses."
        ),
    },

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Unallocated Expenses",
        "amount": 3491831,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": (
            "Expenses not allocated by sex/sport. "
            "39.40% of Sonoma's EADA total."
        ),
    },

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Operating Expenses",
        "amount": 1074501,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": "Grand total operating expenses.",
    },

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Athletic Aid",
        "amount": 992695,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": "Athletic student aid.",
    },

    {
        "fiscal_year": "2024 EADA",
        "category": "EADA Recruiting Expenses",
        "amount": 19865,
        "source_id": "EADA_2024",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "EADA",
        "notes": "Recruiting expenses.",
    },

    # ==============================================
    # FY 2025-26 BUDGET REDUCTION
    # ==============================================

    {
        "fiscal_year": "2025-26",
        "category": "Projected Savings - Discontinuation of NCAA Athletics",
        "amount": 3700000,
        "source_id": "SSU_BUDGET_COMMITTEE_2025",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "University Budget Reduction Plan",
        "notes": (
            "Projected base-budget savings associated "
            "with discontinuing NCAA athletics. This "
            "is not equivalent to total historical "
            "athletics spending."
        ),
    },

    # ==============================================
    # REBUILD FUNDING
    # ==============================================

    {
        "fiscal_year": "2025-26 to 2027-28",
        "category": "One-Time State Athletics Funding",
        "amount": 8000000,
        "source_id": "SSU_COMMITMENT",
        "authority_level": "PRIMARY",
        "verification_status": "VERIFIED",
        "accounting_basis": "One-Time State Appropriation",
        "notes": (
            "One-time funding designated to support "
            "NCAA Division II athletics over three "
            "years. Do not treat as an $8M annual "
            "operating budget."
        ),
    },
]


# --------------------------------------------------
# VALIDATE RECORDS
# --------------------------------------------------

def validate_records():

    errors = 0

    required_fields = [
        "fiscal_year",
        "category",
        "amount",
        "source_id",
        "authority_level",
        "verification_status",
        "accounting_basis",
        "notes",
    ]

    for index, record in enumerate(
        records,
        start=1
    ):

        for field in required_fields:

            if field not in record:

                print(
                    f"ERROR: Record {index} "
                    f"is missing {field}"
                )

                errors += 1

        if record.get("amount", 0) < 0:

            print(
                f"WARNING: Record {index} "
                f"contains a negative amount."
            )

    return errors


# --------------------------------------------------
# VERIFY WHITE PAPER TOTAL
# --------------------------------------------------

def verify_white_paper_total():

    component_categories = {
        "Operating Fund Allocation",
        "IRA Fee Allocation - Annual",
        "IRA Fee Allocation - One-Time",
        "Fundraising and Scholarship - Operating Fund",
        "Fundraising and Scholarship - Non-Operating Fund",
        "Other Financial Sources",
    }

    components = sum(
        record["amount"]
        for record in records
        if (
            record["fiscal_year"] == "2024-25"
            and record["category"]
            in component_categories
        )
    )

    reported_total = next(
        record["amount"]
        for record in records
        if (
            record["fiscal_year"] == "2024-25"
            and record["category"]
            == "Total Athletics Funding Sources"
        )
    )

    difference = (
        components
        - reported_total
    )

    print()
    print("FY24-25 FUNDING RECONCILIATION")
    print("==============================")

    print(
        f"Calculated Components: "
        f"${components:,.0f}"
    )

    print(
        f"Reported Total: "
        f"${reported_total:,.0f}"
    )

    print(
        f"Difference: "
        f"${difference:,.0f}"
    )

    if difference == 0:

        print("Status: MATCH")

    else:

        print("Status: CHECK")


# --------------------------------------------------
# SAVE CSV
# --------------------------------------------------

def save_data():

    fieldnames = [
        "fiscal_year",
        "category",
        "amount",
        "source_id",
        "authority_level",
        "verification_status",
        "accounting_basis",
        "notes",
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

        writer.writerows(records)


# --------------------------------------------------
# DISPLAY HISTORY
# --------------------------------------------------

def show_history():

    print()
    print("SONOMA ATHLETICS FINANCIAL HISTORY")
    print("==================================")

    current_year = None

    for record in records:

        fiscal_year = record[
            "fiscal_year"
        ]

        if fiscal_year != current_year:

            print()
            print(fiscal_year)
            print("-" * len(fiscal_year))

            current_year = fiscal_year

        print(
            f"{record['category']}: "
            f"${record['amount']:,.0f}"
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    errors = validate_records()

    if errors > 0:

        print()
        print(
            f"STOPPED: {errors} validation "
            f"errors found."
        )

        return

    verify_white_paper_total()

    save_data()

    show_history()

    print()
    print("==============================")
    print("FINANCIAL HISTORY SAVED TO:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()