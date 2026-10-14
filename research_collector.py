import csv
from pathlib import Path
from datetime import date


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

REGISTRY_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Raw"
    / "Research"
    / "source_registry.csv"
)

REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# REGISTRY COLUMNS
# --------------------------------------------------

FIELDNAMES = [
    "source_id",
    "source_name",
    "source_type",
    "organization",
    "url",
    "data_year",
    "date_accessed",
    "topic",
    "school",
    "authority_level",
    "status",
    "local_file",
    "notes",
]


VALID_AUTHORITY_LEVELS = {
    "PRIMARY",
    "SECONDARY",
    "DISCOVERY",
}


# --------------------------------------------------
# LOAD CURRENT REGISTRY
# --------------------------------------------------

def load_registry():

    if not REGISTRY_FILE.exists():
        return []

    if REGISTRY_FILE.stat().st_size == 0:
        return []

    with open(
        REGISTRY_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


# --------------------------------------------------
# DUPLICATE CHECK
# --------------------------------------------------

def source_exists(sources, source_id, url):

    for source in sources:

        if source.get("source_id") == source_id:
            return True

        existing_url = source.get("url", "").strip()

        if url and existing_url == url:
            return True

    return False


# --------------------------------------------------
# ADD ONE SOURCE
# --------------------------------------------------

def add_source(source):

    sources = load_registry()

    source_id = source["source_id"]
    url = source.get("url", "")

    authority = (
        source.get("authority_level", "")
        .upper()
    )

    if authority not in VALID_AUTHORITY_LEVELS:

        print(
            f"ERROR: Invalid authority level "
            f"for {source_id}: {authority}"
        )

        return "ERROR"

    if source_exists(
        sources,
        source_id,
        url
    ):

        print(
            f"SKIPPED: Source already exists -> "
            f"{source_id}"
        )

        return "SKIPPED"

    new_source = {
        "source_id":
            source_id,

        "source_name":
            source.get("source_name", ""),

        "source_type":
            source.get("source_type", ""),

        "organization":
            source.get("organization", ""),

        "url":
            url,

        "data_year":
            source.get("data_year", ""),

        "date_accessed":
            date.today().isoformat(),

        "topic":
            source.get("topic", ""),

        "school":
            source.get("school", ""),

        "authority_level":
            authority,

        "status":
            source.get(
                "status",
                "ACTIVE"
            ),

        "local_file":
            source.get("local_file", ""),

        "notes":
            source.get("notes", ""),
    }

    file_exists = (
        REGISTRY_FILE.exists()
        and REGISTRY_FILE.stat().st_size > 0
    )

    with open(
        REGISTRY_FILE,
        "a",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(new_source)

    print(
        f"ADDED: {source_id} | "
        f"{new_source['source_name']}"
    )

    return "ADDED"


# --------------------------------------------------
# SOURCES TO REGISTER
# --------------------------------------------------
#
# PRIMARY:
# Official government/university/system data
#
# SECONDARY:
# Credible research/reporting
#
# DISCOVERY:
# Open-source tools/projects that may help us
# build the AI Business Operations Intern
# --------------------------------------------------

SOURCES = [

    # ==============================================
    # EXISTING EADA DATA
    # ==============================================

    {
        "source_id":
            "EADA_2024",

        "source_name":
            "Equity in Athletics Disclosure Act Data",

        "source_type":
            "Government Dataset",

        "organization":
            "U.S. Department of Education",

        "url":
            "https://ope.ed.gov/athletics/",

        "data_year":
            "2024",

        "topic":
            "Athletics Finance and Participation",

        "school":
            "Multiple",

        "authority_level":
            "PRIMARY",

        "status":
            "DOWNLOADED",

        "local_file":
            "Data/Raw/All_Data_Combined_2024.csv",

        "notes":
            (
                "Primary athletics dataset used for "
                "Sonoma, CSU peer, and GVSU analysis."
            ),
    },


    # ==============================================
    # SONOMA ATHLETICS WHITE PAPER
    # ==============================================

    {
        "source_id":
            "SSU_ATHLETICS_WHITE_PAPER_2026",

        "source_name":
            "Sonoma State Athletics White Paper",

        "source_type":
            "University Report",

        "organization":
            "Sonoma State University",

        "url":
            (
                "https://president.sonoma.edu/sites/"
                "president/files/2026-01/"
                "Athletics%20White%20Paper%20Final%"
                "20Jan2026.pdf"
            ),

        "data_year":
            "2026",

        "topic":
            (
                "Athletics Funding, Historical Costs, "
                "Program Structure"
            ),

        "school":
            "Sonoma State University",

        "authority_level":
            "PRIMARY",

        "status":
            "TO_DOWNLOAD",

        "local_file":
            "",

        "notes":
            (
                "High-priority source for understanding "
                "Sonoma athletics funding and rebuilding "
                "the department."
            ),
    },


    # ==============================================
    # SONOMA BUDGET OFFICE
    # ==============================================

    {
        "source_id":
            "SSU_BUDGET_OFFICE",

        "source_name":
            "Sonoma State Budget and Resource Planning",

        "source_type":
            "University Budget Portal",

        "organization":
            "Sonoma State University",

        "url":
            "https://budget.sonoma.edu/",

        "data_year":
            "Current/Historical",

        "topic":
            (
                "University Budget, OpenBook, "
                "Historical Budget Plans"
            ),

        "school":
            "Sonoma State University",

        "authority_level":
            "PRIMARY",

        "status":
            "ACTIVE",

        "local_file":
            "",

        "notes":
            (
                "Primary location for Sonoma budget "
                "documents and historical financial "
                "planning records."
            ),
    },


    # ==============================================
    # SONOMA BUDGET COMMITTEE
    # ==============================================

    {
        "source_id":
            "SSU_BUDGET_COMMITTEE_2025",

        "source_name":
            "Sonoma State Budget Committee Records",

        "source_type":
            "University Public Records",

        "organization":
            "Sonoma State University",

        "url":
            (
                "https://budget.sonoma.edu/"
                "agendas-minutes/"
                "february-20-2025-minutes"
            ),

        "data_year":
            "2025",

        "topic":
            (
                "Athletics Savings, Budget Reductions, "
                "Institutional Financial Planning"
            ),

        "school":
            "Sonoma State University",

        "authority_level":
            "PRIMARY",

        "status":
            "ACTIVE",

        "local_file":
            "",

        "notes":
            (
                "Includes university budget discussion "
                "related to NCAA athletics."
            ),
    },


    # ==============================================
    # IPEDS
    # ==============================================

    {
        "source_id":
            "IPEDS",

        "source_name":
            "Integrated Postsecondary Education Data System",

        "source_type":
            "Government Dataset",

        "organization":
            "National Center for Education Statistics",

        "url":
            "https://nces.ed.gov/ipeds/",

        "data_year":
            "Annual",

        "topic":
            (
                "Enrollment, Finance, Staffing, "
                "Graduation, Institutional Data"
            ),

        "school":
            "Multiple",

        "authority_level":
            "PRIMARY",

        "status":
            "ACTIVE",

        "local_file":
            "",

        "notes":
            (
                "Will support enrollment, institutional "
                "finance, staffing, and demographic "
                "analysis."
            ),
    },


    # ==============================================
    # COLLEGE SCORECARD
    # ==============================================

    {
        "source_id":
            "COLLEGE_SCORECARD",

        "source_name":
            "College Scorecard",

        "source_type":
            "Government Dataset",

        "organization":
            "U.S. Department of Education",

        "url":
            "https://collegescorecard.ed.gov/data/",

        "data_year":
            "Annual",

        "topic":
            (
                "Enrollment, Cost, Student Outcomes, "
                "Socioeconomic Data"
            ),

        "school":
            "Multiple",

        "authority_level":
            "PRIMARY",

        "status":
            "ACTIVE",

        "local_file":
            "",

        "notes":
            (
                "Useful for connecting athletics strategy "
                "to enrollment and institutional outcomes."
            ),
    },


    # ==============================================
    # NCAA
    # ==============================================

    {
        "source_id":
            "NCAA_DII_FINANCIAL_RESEARCH",

        "source_name":
            "NCAA Division II Financial Research",

        "source_type":
            "Association Research",

        "organization":
            "NCAA",

        "url":
            "https://www.ncaa.org/",

        "data_year":
            "Multiple",

        "topic":
            (
                "Division II Athletics Financial "
                "Benchmarks"
            ),

        "school":
            "Multiple",

        "authority_level":
            "PRIMARY",

        "status":
            "RESEARCH",

        "local_file":
            "",

        "notes":
            (
                "Use NCAA aggregate research for national "
                "D-II benchmarks. Individual institutional "
                "NCAA financial submissions may not be "
                "public."
            ),
    },


    # ==============================================
    # CSU SYSTEM
    # ==============================================

    {
        "source_id":
            "CSU_FINANCIAL_SERVICES",

        "source_name":
            "California State University Financial Services",

        "source_type":
            "University System",

        "organization":
            "California State University",

        "url":
            "https://www.calstate.edu/",

        "data_year":
            "Current/Historical",

        "topic":
            (
                "Finance, Procurement, Budget, "
                "Policies and Procedures"
            ),

        "school":
            "CSU System",

        "authority_level":
            "PRIMARY",

        "status":
            "RESEARCH",

        "local_file":
            "",

        "notes":
            (
                "Starting point for CSU-wide financial "
                "and procurement rules relevant to the "
                "future business operations system."
            ),
    },


    # ==============================================
    # OPEN-SOURCE ERP / PROCUREMENT
    # ==============================================

    {
        "source_id":
            "GITHUB_ERPNEXT_CONSTRUCTION",

        "source_name":
            "ERPNext Construction Module",

        "source_type":
            "Open Source Project",

        "organization":
            "GitHub Community",

        "url":
            (
                "https://github.com/amet123/"
                "ERPNext-Construction-Module"
            ),

        "data_year":
            "Current",

        "topic":
            (
                "Budget Commitments, Purchase Orders, "
                "Actual Expenses"
            ),

        "school":
            "Not Applicable",

        "authority_level":
            "DISCOVERY",

        "status":
            "REVIEW",

        "local_file":
            "",

        "notes":
            (
                "Potential architecture reference for "
                "Budget - Commitments - Actuals - "
                "Available Budget workflow."
            ),
    },


    # ==============================================
    # OPEN-SOURCE PYTHON ERP
    # ==============================================

    {
        "source_id":
            "GITHUB_FASTERP",

        "source_name":
            "FastERP",

        "source_type":
            "Open Source Project",

        "organization":
            "Predictive Labs AI",

        "url":
            (
                "https://github.com/"
                "predictivelabsai/FastERP"
            ),

        "data_year":
            "Current",

        "topic":
            (
                "ERP, Purchasing, Accounting, Budgets, "
                "AI Assistant"
            ),

        "school":
            "Not Applicable",

        "authority_level":
            "DISCOVERY",

        "status":
            "REVIEW",

        "local_file":
            "",

        "notes":
            (
                "Potential architecture reference for "
                "the future AI Athletics Business "
                "Operations Intern."
            ),
    },
]


# --------------------------------------------------
# BATCH REGISTER SOURCES
# --------------------------------------------------

def register_sources():

    added = 0
    skipped = 0
    errors = 0

    print()
    print("REGISTERING RESEARCH SOURCES")
    print("============================")

    for source in SOURCES:

        result = add_source(source)

        if result == "ADDED":
            added += 1

        elif result == "SKIPPED":
            skipped += 1

        else:
            errors += 1

    print()
    print("REGISTRATION SUMMARY")
    print("====================")
    print(f"Added: {added}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")


# --------------------------------------------------
# SHOW REGISTRY
# --------------------------------------------------

def show_registry():

    sources = load_registry()

    print()
    print("CURRENT SOURCE REGISTRY")
    print("=======================")

    primary = 0
    secondary = 0
    discovery = 0

    for source in sources:

        authority = source.get(
            "authority_level",
            ""
        )

        print(
            f"{source.get('source_id', '')} | "
            f"{authority} | "
            f"{source.get('status', '')}"
        )

        if authority == "PRIMARY":
            primary += 1

        elif authority == "SECONDARY":
            secondary += 1

        elif authority == "DISCOVERY":
            discovery += 1

    print()
    print(f"Total Sources: {len(sources)}")
    print(f"Primary: {primary}")
    print(f"Secondary: {secondary}")
    print(f"Discovery: {discovery}")


# --------------------------------------------------
# RUN
# --------------------------------------------------

register_sources()

show_registry()