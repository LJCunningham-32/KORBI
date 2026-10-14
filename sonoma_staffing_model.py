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
    / "sonoma_staffing_model.csv"
)


# --------------------------------------------------
# SOURCE INFORMATION
# --------------------------------------------------

SOURCE_FILE = "SSU_ATHLETICS_WHITE_PAPER_2026.pdf"
SOURCE_PAGE = 16
SOURCE_SECTION = "Chapter 8: Athletics Staffing"
VERIFICATION_STATUS = "VERIFIED_FROM_SOURCE"


# --------------------------------------------------
# ADMINISTRATIVE STAFFING MODEL
# --------------------------------------------------
#
# Salary ranges are preserved exactly where the
# White Paper gives a range.
#
# Commission for External Affairs is NOT included
# in salary totals because the source does not give
# a guaranteed commission amount.
# --------------------------------------------------

STAFF_POSITIONS = [

    {
        "position": "Director of Athletics",
        "area": "Administration",
        "fte": 1.0,
        "minimum_salary": 170000,
        "maximum_salary": 180000,
        "salary_type": "RANGE",
        "notes": "",
    },

    {
        "position": (
            "Associate Director of Athletics "
            "for External Affairs"
        ),
        "area": "External Affairs",
        "fte": 1.0,
        "minimum_salary": 60000,
        "maximum_salary": 70000,
        "salary_type": "RANGE_PLUS_COMMISSION",
        "notes": (
            "White Paper specifies salary plus commission. "
            "Commission excluded from base salary totals."
        ),
    },

    {
        "position": "Athletics Development Position",
        "area": "Development",
        "fte": 1.0,
        "minimum_salary": 104000,
        "maximum_salary": 104000,
        "salary_type": "FIXED",
        "notes": (
            "Recommended to report to the Director of Athletics "
            "with dotted-line reporting to University Advancement."
        ),
    },

    {
        "position": (
            "Associate Director of Athletics "
            "for Internal Affairs"
        ),
        "area": "Compliance / Internal Affairs",
        "fte": 1.0,
        "minimum_salary": 96336,
        "maximum_salary": 96336,
        "salary_type": "FIXED",
        "notes": "Includes SWA, compliance, and other duties.",
    },

    {
        "position": (
            "Associate Athletics Director "
            "for Sports Communications"
        ),
        "area": "Sports Communications",
        "fte": 1.0,
        "minimum_salary": 70000,
        "maximum_salary": 80000,
        "salary_type": "RANGE",
        "notes": "",
    },

    {
        "position": "Public Affairs / Communications Specialist",
        "area": "Sports Communications",
        "fte": 1.0,
        "minimum_salary": 54840,
        "maximum_salary": 54840,
        "salary_type": "FIXED",
        "notes": "Assistant to sports communications.",
    },

    {
        "position": "Athletics Administration Professional III",
        "area": "Business Operations",
        "fte": 1.0,
        "minimum_salary": 70620,
        "maximum_salary": 70620,
        "salary_type": "FIXED",
        "notes": (
            "Business operations, facilities, "
            "and equipment responsibilities."
        ),
    },

    {
        "position": "Head Athletic Trainer",
        "area": "Sports Medicine",
        "fte": 1.0,
        "minimum_salary": 87984,
        "maximum_salary": 87984,
        "salary_type": "FIXED",
        "notes": "",
    },

    {
        "position": "Assistant Athletic Trainer II",
        "area": "Sports Medicine",
        "fte": 1.0,
        "minimum_salary": 70416,
        "maximum_salary": 70416,
        "salary_type": "FIXED",
        "notes": "",
    },

    {
        "position": "Assistant Athletic Trainer I",
        "area": "Sports Medicine",
        "fte": 0.5,
        "minimum_salary": 26892,
        "maximum_salary": 26892,
        "salary_type": "FIXED",
        "notes": "White Paper identifies this position as 50% FTE.",
    },

    {
        "position": "Coaching Specialist - Strength",
        "area": "Strength and Conditioning",
        "fte": 1.0,
        "minimum_salary": 80544,
        "maximum_salary": 80544,
        "salary_type": "FIXED",
        "notes": (
            "Faculty position and identified as a prior position."
        ),
    },
]


# --------------------------------------------------
# COACHING STRUCTURE NOTES
# --------------------------------------------------

COACHING_STRUCTURE = [

    {
        "program_group": "Men's Basketball",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": "One full-time head coach and one full-time assistant.",
    },

    {
        "program_group": "Women's Basketball",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": "One full-time head coach and one full-time assistant.",
    },

    {
        "program_group": "Men's Soccer",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": "One full-time head coach and one full-time assistant.",
    },

    {
        "program_group": "Women's Soccer",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": "One full-time head coach and one full-time assistant.",
    },

    {
        "program_group": "Women's Volleyball",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": "One full-time head coach and one full-time assistant.",
    },

    {
        "program_group": (
            "Men's/Women's Cross Country "
            "and Track & Field"
        ),
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 1.0,
        "notes": (
            "One full-time head coach and one full-time assistant "
            "for the six cross-country/indoor/outdoor programs."
        ),
    },

    {
        "program_group": "Men's and Women's Golf",
        "head_coach_fte": 1.0,
        "assistant_coach_fte": 0.5,
        "notes": (
            "One full-time head coach and one half-time "
            "assistant covering both golf programs."
        ),
    },
]


# --------------------------------------------------
# VALIDATE STAFFING
# --------------------------------------------------

def validate_staffing():

    total_fte = sum(
        row["fte"]
        for row in STAFF_POSITIONS
    )

    minimum_salary_total = sum(
        row["minimum_salary"]
        for row in STAFF_POSITIONS
    )

    maximum_salary_total = sum(
        row["maximum_salary"]
        for row in STAFF_POSITIONS
    )

    return (
        total_fte,
        minimum_salary_total,
        maximum_salary_total,
    )


# --------------------------------------------------
# SAVE MODEL
# --------------------------------------------------

def save_model():

    fieldnames = [
        "institution",
        "record_type",
        "position_or_program",
        "area",
        "fte",
        "head_coach_fte",
        "assistant_coach_fte",
        "minimum_salary",
        "maximum_salary",
        "salary_type",
        "source_file",
        "source_page",
        "source_section",
        "verification_status",
        "notes",
    ]

    records = []

    for row in STAFF_POSITIONS:

        records.append({

            "institution":
                "Sonoma State University",

            "record_type":
                "ADMINISTRATIVE_STAFF",

            "position_or_program":
                row["position"],

            "area":
                row["area"],

            "fte":
                row["fte"],

            "head_coach_fte":
                "",

            "assistant_coach_fte":
                "",

            "minimum_salary":
                row["minimum_salary"],

            "maximum_salary":
                row["maximum_salary"],

            "salary_type":
                row["salary_type"],

            "source_file":
                SOURCE_FILE,

            "source_page":
                SOURCE_PAGE,

            "source_section":
                SOURCE_SECTION,

            "verification_status":
                VERIFICATION_STATUS,

            "notes":
                row["notes"],
        })

    for row in COACHING_STRUCTURE:

        records.append({

            "institution":
                "Sonoma State University",

            "record_type":
                "COACHING_STRUCTURE",

            "position_or_program":
                row["program_group"],

            "area":
                "Coaching",

            "fte":
                "",

            "head_coach_fte":
                row["head_coach_fte"],

            "assistant_coach_fte":
                row["assistant_coach_fte"],

            "minimum_salary":
                "",

            "maximum_salary":
                "",

            "salary_type":
                "NOT_SPECIFIED",

            "source_file":
                SOURCE_FILE,

            "source_page":
                SOURCE_PAGE,

            "source_section":
                SOURCE_SECTION,

            "verification_status":
                VERIFICATION_STATUS,

            "notes":
                row["notes"],
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
        writer.writerows(records)

    return records


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print()
    print("SONOMA ATHLETICS STAFFING MODEL")
    print("==============================")

    (
        total_fte,
        minimum_salary_total,
        maximum_salary_total,
    ) = validate_staffing()

    print()
    print("ADMINISTRATIVE STAFFING SUMMARY")
    print("===============================")

    print(
        f"Administrative Positions: "
        f"{len(STAFF_POSITIONS)}"
    )

    print(
        f"Administrative FTE:       "
        f"{total_fte:.1f}"
    )

    print(
        f"Minimum Base Salaries:    "
        f"${minimum_salary_total:,.0f}"
    )

    print(
        f"Maximum Base Salaries:    "
        f"${maximum_salary_total:,.0f}"
    )

    print()
    print(
        "NOTE: External Affairs commission is "
        "not included in these totals."
    )

    records = save_model()

    print()
    print(
        f"Structured Staffing Records: "
        f"{len(records)}"
    )

    print()
    print("Saved To:")
    print(OUTPUT_FILE)

    print()
    print("ADMINISTRATIVE POSITIONS")
    print("========================")

    for row in STAFF_POSITIONS:

        if (
            row["minimum_salary"]
            == row["maximum_salary"]
        ):

            salary_display = (
                f"${row['minimum_salary']:,.0f}"
            )

        else:

            salary_display = (
                f"${row['minimum_salary']:,.0f} - "
                f"${row['maximum_salary']:,.0f}"
            )

        print()
        print(row["position"])

        print(
            f"Area:   {row['area']}"
        )

        print(
            f"FTE:    {row['fte']}"
        )

        print(
            f"Salary: {salary_display}"
        )


if __name__ == "__main__":
    main()