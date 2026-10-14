import csv
import shutil
from pathlib import Path


# ============================================================
# KORBI
# Knowledge & Operations Resource for Business Intelligence
#
# SONOMA STATE ATHLETICS
# YEAR 1 - START OF Q2 SIMULATION
#
# Simulation Date: October 1, 2027
#
# PURPOSE
# -------
# Simulate a realistic athletics department after Q1 has closed.
#
# OFFICIAL / SOURCE-BASED:
# - Annual department budget structure
# - Returning sport structure
# - White Paper planning information
# - Historical EADA information where noted
#
# SIMULATED:
# - Q1 actual spending
# - Open POs
# - Future scheduled expenses
# - Expected remaining expenses
# - Individual sport financial condition
#
# NO simulated activity should ever be represented as
# actual Sonoma State financial data.
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
PROCESSED_FOLDER = PROJECT_FOLDER / "Data" / "Processed"


CATEGORY_BUDGET_FILE = (
    PROCESSED_FOLDER
    / "korbi_category_budgets.csv"
)

OLD_BUDGET_BACKUP = (
    PROCESSED_FOLDER
    / "korbi_category_budgets_pre_q2_simulation.csv"
)

LEDGER_FILE = (
    PROCESSED_FOLDER
    / "korbi_operational_ledger.csv"
)

FUTURE_FILE = (
    PROCESSED_FOLDER
    / "korbi_future_expenses.csv"
)

DEPARTMENT_FILE = (
    PROCESSED_FOLDER
    / "korbi_department_q1_snapshot.csv"
)

SHARED_OPERATIONS_FILE = (
    PROCESSED_FOLDER
    / "korbi_shared_operations_q1.csv"
)

SIMULATION_FILE = (
    PROCESSED_FOLDER
    / "korbi_simulation_metadata.csv"
)


SIMULATION_DATE = "2027-10-01"

SIMULATION_LABEL = (
    "KORBI Q1 CLOSE SIMULATION - "
    "TEST DATA ONLY - NOT SONOMA ACTUALS"
)


# ============================================================
# OFFICIAL ANNUAL ATHLETICS PLAN
#
# Current KORBI controlling model:
# Sonoma Athletics Fiscal Feasibility planning model
#
# Total = $6,687,000
# ============================================================


ANNUAL_BUDGET = {

    "ATHLETIC_STUDENT_AID":
        1_045_300,

    "COACHING_COMPENSATION":
        2_720_800,

    "SUPPORT_ADMIN_COMPENSATION":
        1_338_400,

    "TEAM_TRAVEL":
        682_600,

    "EQUIPMENT_UNIFORMS_SUPPLIES":
        246_100,

    "OTHER_OPERATING":
        653_800,
}


ANNUAL_TOTAL = sum(
    ANNUAL_BUDGET.values()
)


# ============================================================
# RETURNING SPORTS
#
# 10-sport restart scenario
#
# Operating weights are planning tools.
#
# White Paper detailed operating amounts are used where
# applicable.
#
# Women's Softball uses historical Sonoma EADA operating
# expense because it was not included in the earlier White
# Paper sport table being used for the other programs.
#
# These weights distribute the current operating pools.
# They are NOT represented as official final sport budgets.
# ============================================================


SPORTS = {

    "MBB": {
        "name":
            "Men's Basketball",

        "season":
            "WINTER",

        "weight":
            149318,

        "weight_source":
            "White Paper planning detail",
    },

    "WBB": {
        "name":
            "Women's Basketball",

        "season":
            "WINTER",

        "weight":
            131987,

        "weight_source":
            "White Paper planning detail",
    },

    "MGO": {
        "name":
            "Men's Golf",

        "season":
            "FALL_SPRING",

        "weight":
            126797,

        "weight_source":
            "White Paper planning detail",
    },

    "WGO": {
        "name":
            "Women's Golf",

        "season":
            "FALL_SPRING",

        "weight":
            119751,

        "weight_source":
            "White Paper planning detail",
    },

    "MSO": {
        "name":
            "Men's Soccer",

        "season":
            "FALL",

        "weight":
            113069,

        "weight_source":
            "White Paper planning detail",
    },

    "WSO": {
        "name":
            "Women's Soccer",

        "season":
            "FALL",

        "weight":
            120347,

        "weight_source":
            "White Paper planning detail",
    },

    "MCC": {
        "name":
            "Men's Cross Country",

        "season":
            "FALL",

        "weight":
            52331,

        "weight_source":
            "White Paper planning detail",
    },

    "WCC": {
        "name":
            "Women's Cross Country",

        "season":
            "FALL",

        "weight":
            52331,

        "weight_source":
            "White Paper planning detail",
    },

    "WVB": {
        "name":
            "Women's Volleyball",

        "season":
            "FALL",

        "weight":
            125068,

        "weight_source":
            "White Paper planning detail",
    },

    "WSB": {
        "name":
            "Women's Softball",

        "season":
            "SPRING",

        "weight":
            154917,

        "weight_source":
            "Historical Sonoma EADA operating expense",
    },
}


# ============================================================
# INDIVIDUAL SPORT FINANCIAL PROFILES
#
# These deliberately DO NOT use identical percentages.
#
# The purpose is to create a realistic management environment:
#
# - some programs have flexibility
# - some programs need caution
# - some programs are approaching budget limits
#
# ALL percentages below are SIMULATION ASSUMPTIONS.
#
# Actual + PO + Scheduled + Expected = projected year-end.
# ============================================================


SPORT_FINANCIAL_PROFILES = {

    "MBB": {
        "actual_pct": 0.14,
        "po_pct": 0.10,
        "scheduled_pct": 0.34,
        "expected_pct": 0.27,
    },

    "WBB": {
        "actual_pct": 0.13,
        "po_pct": 0.08,
        "scheduled_pct": 0.30,
        "expected_pct": 0.28,
    },

    "MGO": {
        "actual_pct": 0.22,
        "po_pct": 0.09,
        "scheduled_pct": 0.30,
        "expected_pct": 0.23,
    },

    "WGO": {
        "actual_pct": 0.24,
        "po_pct": 0.12,
        "scheduled_pct": 0.34,
        "expected_pct": 0.23,
    },

    "MSO": {
        "actual_pct": 0.33,
        "po_pct": 0.16,
        "scheduled_pct": 0.28,
        "expected_pct": 0.18,
    },

    "WSO": {
        "actual_pct": 0.28,
        "po_pct": 0.11,
        "scheduled_pct": 0.29,
        "expected_pct": 0.20,
    },

    "MCC": {
        "actual_pct": 0.25,
        "po_pct": 0.10,
        "scheduled_pct": 0.27,
        "expected_pct": 0.19,
    },

    "WCC": {
        "actual_pct": 0.27,
        "po_pct": 0.11,
        "scheduled_pct": 0.30,
        "expected_pct": 0.18,
    },

    "WVB": {
        "actual_pct": 0.30,
        "po_pct": 0.13,
        "scheduled_pct": 0.30,
        "expected_pct": 0.18,
    },

    "WSB": {
        "actual_pct": 0.09,
        "po_pct": 0.07,
        "scheduled_pct": 0.28,
        "expected_pct": 0.22,
    },
}


# ============================================================
# HELPERS
# ============================================================


def money(value):

    return f"${value:,.0f}"


def write_csv(
    file_path,
    rows,
    fieldnames
):

    with open(
        file_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)


def allocate_pool(
    total_amount
):

    total_weight = sum(
        sport["weight"]
        for sport in SPORTS.values()
    )

    allocations = {}

    running_total = 0

    codes = list(
        SPORTS.keys()
    )

    for code in codes[:-1]:

        weight = (
            SPORTS[code]["weight"]
        )

        amount = round(
            total_amount
            * weight
            / total_weight
        )

        allocations[code] = amount

        running_total += amount

    final_code = codes[-1]

    allocations[final_code] = (
        total_amount
        - running_total
    )

    return allocations


# ============================================================
# TEAM OPERATING POOLS
#
# Travel:
# 100% attributed to teams.
#
# Equipment:
# 90% team use
# 10% shared athletics use
#
# Other Operating:
# 70% team use
# 30% shared athletics operations
#
# These are planning allocations, not official accounting
# assignments.
# ============================================================


def build_operating_allocations():

    travel_pool = (
        ANNUAL_BUDGET[
            "TEAM_TRAVEL"
        ]
    )

    equipment_team_pool = round(
        ANNUAL_BUDGET[
            "EQUIPMENT_UNIFORMS_SUPPLIES"
        ]
        * 0.90
    )

    equipment_shared_pool = (
        ANNUAL_BUDGET[
            "EQUIPMENT_UNIFORMS_SUPPLIES"
        ]
        - equipment_team_pool
    )

    other_team_pool = round(
        ANNUAL_BUDGET[
            "OTHER_OPERATING"
        ]
        * 0.70
    )

    other_shared_pool = (
        ANNUAL_BUDGET[
            "OTHER_OPERATING"
        ]
        - other_team_pool
    )

    travel = allocate_pool(
        travel_pool
    )

    equipment = allocate_pool(
        equipment_team_pool
    )

    other = allocate_pool(
        other_team_pool
    )

    allocations = {}

    budget_rows = []

    for code, sport in (
        SPORTS.items()
    ):

        team_total = (
            travel[code]
            + equipment[code]
            + other[code]
        )

        allocations[code] = {

            "travel":
                travel[code],

            "equipment":
                equipment[code],

            "other":
                other[code],

            "total":
                team_total,
        }

        budget_rows.append({

            "program_code":
                code,

            "program_name":
                sport["name"],

            "expense_category":
                "GENERAL_OPERATING",

            "category_budget":
                team_total,

            "budget_status":
                "PLANNING_ALLOCATION",

            "source":
                (
                    "Current department operating pools "
                    "distributed using White Paper / "
                    "historical EADA planning weights"
                ),

            "notes":
                (
                    "KORBI simulation allocation. "
                    "Not an official final Sonoma "
                    "sport budget."
                ),
        })

    shared = {

        "equipment_shared":
            equipment_shared_pool,

        "other_shared":
            other_shared_pool,
    }

    return (
        budget_rows,
        allocations,
        shared
    )


# ============================================================
# ACTUAL EXPENSE MIX
#
# Q1 spending differs depending upon season.
# ============================================================


def actual_mix(
    season
):

    if season == "FALL":

        return [

            (
                "TRAVEL",
                "Early-season competition travel",
                0.40,
            ),

            (
                "EQUIPMENT",
                "Uniforms, equipment, and supplies",
                0.30,
            ),

            (
                "GAME_OPERATIONS",
                "Home competition and event operations",
                0.20,
            ),

            (
                "RECRUITING",
                "Recruiting and program operations",
                0.10,
            ),
        ]

    if season == "WINTER":

        return [

            (
                "EQUIPMENT",
                "Uniforms and preseason equipment",
                0.45,
            ),

            (
                "PRESEASON_OPERATIONS",
                "Training and preseason preparation",
                0.30,
            ),

            (
                "RECRUITING",
                "Recruiting activity",
                0.15,
            ),

            (
                "TRAVEL",
                "Early preseason travel deposits",
                0.10,
            ),
        ]

    if season == "FALL_SPRING":

        return [

            (
                "TRAVEL",
                "Fall tournaments and competition travel",
                0.40,
            ),

            (
                "EQUIPMENT",
                "Equipment and apparel",
                0.30,
            ),

            (
                "RECRUITING",
                "Recruiting activity",
                0.20,
            ),

            (
                "PROGRAM_OPERATIONS",
                "Program administration and operations",
                0.10,
            ),
        ]

    # Spring sport

    return [

        (
            "EQUIPMENT",
            "Preseason equipment, uniforms, and supplies",
            0.40,
        ),

        (
            "FACILITY_MAINTENANCE",
            "Field preparation and maintenance",
            0.30,
        ),

        (
            "RECRUITING",
            "Fall recruiting",
            0.20,
        ),

        (
            "PROGRAM_OPERATIONS",
            "Preseason program preparation",
            0.10,
        ),
    ]


# ============================================================
# OPEN PO DESCRIPTION
# ============================================================


def po_description(
    season
):

    if season == "FALL":

        return (
            "Open fall travel, hotel, transportation, "
            "and competition commitments"
        )

    if season == "WINTER":

        return (
            "Open winter travel deposits, equipment, "
            "and preseason commitments"
        )

    if season == "FALL_SPRING":

        return (
            "Open tournament travel and equipment "
            "commitments"
        )

    return (
        "Open equipment, facility preparation, "
        "and preseason commitments"
    )


# ============================================================
# FUTURE SCHEDULED DESCRIPTION
# ============================================================


def scheduled_description(
    season
):

    if season == "FALL":

        return (
            "Remaining scheduled fall travel, "
            "lodging, officials, and game operations"
        )

    if season == "WINTER":

        return (
            "Scheduled winter travel, lodging, "
            "officials, and competition operations"
        )

    if season == "FALL_SPRING":

        return (
            "Remaining fall and spring tournament "
            "travel and competition costs"
        )

    return (
        "Scheduled spring competition travel, "
        "lodging, officials, and game operations"
    )


# ============================================================
# EXPECTED DESCRIPTION
# ============================================================


def expected_description(
    season
):

    if season == "SPRING":

        return (
            "Expected spring equipment replacement, "
            "field needs, recruiting, and other "
            "season operating requirements"
        )

    return (
        "Expected remaining equipment, recruiting, "
        "supplies, and season operating requirements"
    )


# ============================================================
# LEDGER ROW
# ============================================================


def ledger_row(
    transaction_id,
    code,
    transaction_type,
    status,
    vendor,
    description,
    amount,
    transaction_date,
    po_number=""
):

    return {

        "transaction_id":
            transaction_id,

        "program_code":
            code,

        "program_name":
            SPORTS[code]["name"],

        "expense_category":
            "GENERAL_OPERATING",

        "transaction_type":
            transaction_type,

        "status":
            status,

        "vendor":
            vendor,

        "description":
            description,

        "amount":
            amount,

        "transaction_date":
            transaction_date,

        "po_number":
            po_number,

        "notes":
            SIMULATION_LABEL,
    }


# ============================================================
# FUTURE EXPENSE ROW
# ============================================================


def future_row(
    expense_id,
    code,
    expense_type,
    description,
    amount,
    expected_date,
    confidence
):

    return {

        "expense_id":
            expense_id,

        "entry_date":
            SIMULATION_DATE,

        "expected_date":
            expected_date,

        "program_code":
            code,

        "program_name":
            SPORTS[code]["name"],

        "expense_category":
            "GENERAL_OPERATING",

        "expense_type":
            expense_type,

        "vendor":
            "Multiple / TBD",

        "description":
            description,

        "amount":
            amount,

        "confidence":
            confidence,

        "status":
            "PLANNED",

        "entered_by":
            "KORBI Q1 Simulation",

        "notes":
            SIMULATION_LABEL,
    }


# ============================================================
# BUILD SPORT ACTIVITY
# ============================================================


def build_sport_activity(
    allocations
):

    ledger = []

    future = []

    transaction_number = 1

    future_number = 1

    for code, sport in (
        SPORTS.items()
    ):

        budget = (
            allocations[code]["total"]
        )

        profile = (
            SPORT_FINANCIAL_PROFILES[
                code
            ]
        )

        q1_actual = round(
            budget
            * profile["actual_pct"]
        )

        open_po = round(
            budget
            * profile["po_pct"]
        )

        scheduled = round(
            budget
            * profile[
                "scheduled_pct"
            ]
        )

        expected = round(
            budget
            * profile[
                "expected_pct"
            ]
        )

        # ----------------------------------------------------
        # Q1 ACTUAL TRANSACTIONS
        # ----------------------------------------------------

        mix = actual_mix(
            sport["season"]
        )

        allocated_actual = 0

        for index, item in enumerate(
            mix
        ):

            expense_type = item[0]

            description = item[1]

            percentage = item[2]

            if index == (
                len(mix) - 1
            ):

                amount = (
                    q1_actual
                    - allocated_actual
                )

            else:

                amount = round(
                    q1_actual
                    * percentage
                )

                allocated_actual += (
                    amount
                )

            ledger.append(
                ledger_row(

                    f"SIM-TXN-"
                    f"{transaction_number:04d}",

                    code,

                    "ACTUAL",

                    "PAID",

                    "Multiple Vendors",

                    description,

                    amount,

                    "2027-09-30"
                )
            )

            transaction_number += 1

        # ----------------------------------------------------
        # OPEN PURCHASE ORDER
        # ----------------------------------------------------

        ledger.append(
            ledger_row(

                f"SIM-TXN-"
                f"{transaction_number:04d}",

                code,

                "PO",

                "OPEN",

                "Multiple Vendors",

                po_description(
                    sport["season"]
                ),

                open_po,

                "2027-09-30",

                f"SIM-PO-{code}-001"
            )
        )

        transaction_number += 1

        # ----------------------------------------------------
        # SCHEDULED FUTURE EXPENSE
        # ----------------------------------------------------

        if sport["season"] == "FALL":

            scheduled_date = (
                "2027-11-15"
            )

        elif sport["season"] == "WINTER":

            scheduled_date = (
                "2028-01-15"
            )

        elif sport["season"] == "FALL_SPRING":

            scheduled_date = (
                "2028-02-15"
            )

        else:

            scheduled_date = (
                "2028-03-01"
            )

        future.append(
            future_row(

                f"SIM-FUT-"
                f"{future_number:04d}",

                code,

                "SCHEDULED",

                scheduled_description(
                    sport["season"]
                ),

                scheduled,

                scheduled_date,

                "HIGH"
            )
        )

        future_number += 1

        # ----------------------------------------------------
        # EXPECTED FUTURE EXPENSE
        # ----------------------------------------------------

        future.append(
            future_row(

                f"SIM-FUT-"
                f"{future_number:04d}",

                code,

                "EXPECTED",

                expected_description(
                    sport["season"]
                ),

                expected,

                "2028-05-01",

                "MEDIUM"
            )
        )

        future_number += 1

    return (
        ledger,
        future
    )


# ============================================================
# DEPARTMENT-WIDE OBLIGATIONS
#
# These records keep KORBI aware of the full $6.687M
# financial environment.
#
# IMPORTANT:
# These records are reconciliation / departmental records.
#
# They should NOT later be added to the sport ledger again,
# because travel/equipment/operating team allocations are
# already represented in the sport planning layer.
# ============================================================


def build_department_snapshot():

    rows = []

    assumptions = {

        "ATHLETIC_STUDENT_AID": {
            "actual_pct": 0.00,
            "committed_pct": 0.50,
            "future_pct": 0.50,
            "reason":
                (
                    "Fall-term aid represented as committed "
                    "rather than discretionary purchasing."
                ),
        },

        "COACHING_COMPENSATION": {
            "actual_pct": 0.25,
            "committed_pct": 0.00,
            "future_pct": 0.75,
            "reason":
                (
                    "Q1 payroll posted; remaining annual "
                    "coach compensation is a known obligation."
                ),
        },

        "SUPPORT_ADMIN_COMPENSATION": {
            "actual_pct": 0.25,
            "committed_pct": 0.00,
            "future_pct": 0.75,
            "reason":
                (
                    "Q1 payroll posted; remaining support "
                    "and administrative compensation is "
                    "a known obligation."
                ),
        },

        "TEAM_TRAVEL": {
            "actual_pct": 0.18,
            "committed_pct": 0.12,
            "future_pct": 0.60,
            "reason":
                (
                    "Fall travel underway while most winter "
                    "and spring travel remains ahead."
                ),
        },

        "EQUIPMENT_UNIFORMS_SUPPLIES": {
            "actual_pct": 0.30,
            "committed_pct": 0.15,
            "future_pct": 0.40,
            "reason":
                (
                    "Equipment and uniform purchasing is "
                    "front-loaded before and early in seasons."
                ),
        },

        "OTHER_OPERATING": {
            "actual_pct": 0.22,
            "committed_pct": 0.10,
            "future_pct": 0.50,
            "reason":
                (
                    "Administration, game operations, "
                    "software, facilities, memberships, "
                    "services, training, and other expenses."
                ),
        },
    }

    for category, budget in (
        ANNUAL_BUDGET.items()
    ):

        assumption = (
            assumptions[category]
        )

        actual = round(
            budget
            * assumption[
                "actual_pct"
            ]
        )

        committed = round(
            budget
            * assumption[
                "committed_pct"
            ]
        )

        future = round(
            budget
            * assumption[
                "future_pct"
            ]
        )

        projected = (
            actual
            + committed
            + future
        )

        reserve = (
            budget
            - projected
        )

        rows.append({

            "budget_category":
                category,

            "annual_budget":
                budget,

            "q1_actual":
                actual,

            "open_commitments":
                committed,

            "future_reserved":
                future,

            "projected_year_end":
                projected,

            "uncommitted_reserve":
                reserve,

            "source_status":
                (
                    "OFFICIAL BUDGET / "
                    "SIMULATED ACTIVITY"
                ),

            "simulation_reason":
                assumption["reason"],
        })

    return rows


# ============================================================
# SHARED ATHLETICS OPERATIONS
#
# These are expenses that should not be unfairly assigned
# to one coach/team.
#
# Examples:
# - department technology
# - athletic training operations
# - compliance/admin systems
# - department equipment
# - event support
# - shared facility operations
# ============================================================


def build_shared_operations(
    shared
):

    equipment_budget = (
        shared[
            "equipment_shared"
        ]
    )

    other_budget = (
        shared[
            "other_shared"
        ]
    )

    rows = [

        {
            "shared_category":
                "DEPARTMENT_EQUIPMENT",

            "annual_budget":
                equipment_budget,

            "q1_actual":
                round(
                    equipment_budget
                    * 0.28
                ),

            "open_commitments":
                round(
                    equipment_budget
                    * 0.12
                ),

            "future_reserved":
                round(
                    equipment_budget
                    * 0.40
                ),

            "description":
                (
                    "Shared athletics equipment, "
                    "technology, and department supplies"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },

        {
            "shared_category":
                "ATHLETIC_TRAINING_AND_MEDICAL",

            "annual_budget":
                round(
                    other_budget
                    * 0.25
                ),

            "q1_actual":
                round(
                    other_budget
                    * 0.25
                    * 0.25
                ),

            "open_commitments":
                round(
                    other_budget
                    * 0.25
                    * 0.10
                ),

            "future_reserved":
                round(
                    other_budget
                    * 0.25
                    * 0.50
                ),

            "description":
                (
                    "Athletic training supplies, "
                    "medical operations, and "
                    "student-athlete support"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },

        {
            "shared_category":
                "COMPLIANCE_AND_ADMINISTRATION",

            "annual_budget":
                round(
                    other_budget
                    * 0.20
                ),

            "q1_actual":
                round(
                    other_budget
                    * 0.20
                    * 0.22
                ),

            "open_commitments":
                round(
                    other_budget
                    * 0.20
                    * 0.10
                ),

            "future_reserved":
                round(
                    other_budget
                    * 0.20
                    * 0.50
                ),

            "description":
                (
                    "Compliance, memberships, "
                    "administrative systems, "
                    "and department operations"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },

        {
            "shared_category":
                "FACILITIES_AND_EVENT_SUPPORT",

            "annual_budget":
                round(
                    other_budget
                    * 0.30
                ),

            "q1_actual":
                round(
                    other_budget
                    * 0.30
                    * 0.25
                ),

            "open_commitments":
                round(
                    other_budget
                    * 0.30
                    * 0.12
                ),

            "future_reserved":
                round(
                    other_budget
                    * 0.30
                    * 0.48
                ),

            "description":
                (
                    "Shared facilities, event support, "
                    "game management, rentals, "
                    "and operational services"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },

        {
            "shared_category":
                "TECHNOLOGY_AND_SERVICES",

            "annual_budget":
                round(
                    other_budget
                    * 0.15
                ),

            "q1_actual":
                round(
                    other_budget
                    * 0.15
                    * 0.30
                ),

            "open_commitments":
                round(
                    other_budget
                    * 0.15
                    * 0.10
                ),

            "future_reserved":
                round(
                    other_budget
                    * 0.15
                    * 0.45
                ),

            "description":
                (
                    "Software, subscriptions, "
                    "communications, and shared technology"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },

        {
            "shared_category":
                "GENERAL_SHARED_OPERATIONS",

            "annual_budget":
                (
                    other_budget
                    - round(
                        other_budget * 0.25
                    )
                    - round(
                        other_budget * 0.20
                    )
                    - round(
                        other_budget * 0.30
                    )
                    - round(
                        other_budget * 0.15
                    )
                ),

            "q1_actual":
                0,

            "open_commitments":
                0,

            "future_reserved":
                0,

            "description":
                (
                    "Remaining shared athletics "
                    "operating reserve"
                ),

            "data_status":
                "SIMULATED PLANNING ALLOCATION",
        },
    ]

    # Add remaining reserve numbers correctly
    for row in rows:

        row["projected_year_end"] = (
            row["q1_actual"]
            + row["open_commitments"]
            + row["future_reserved"]
        )

        row["uncommitted_reserve"] = (
            row["annual_budget"]
            - row["projected_year_end"]
        )

    return rows


# ============================================================
# SPORT FINANCIAL STATUS
# ============================================================


def financial_status(
    projected_pct
):

    if projected_pct >= 1.00:
        return "OVER BUDGET"

    if projected_pct >= 0.95:
        return "HIGH RISK"

    if projected_pct >= 0.90:
        return "CAUTION"

    if projected_pct >= 0.80:
        return "MONITOR"

    return "HEALTHY"


# ============================================================
# DISPLAY DEPARTMENT POSITION
# ============================================================


def display_department(
    snapshot
):

    annual = sum(
        row["annual_budget"]
        for row in snapshot
    )

    actual = sum(
        row["q1_actual"]
        for row in snapshot
    )

    committed = sum(
        row["open_commitments"]
        for row in snapshot
    )

    future = sum(
        row["future_reserved"]
        for row in snapshot
    )

    projected = (
        actual
        + committed
        + future
    )

    reserve = (
        annual
        - projected
    )

    print()
    print(
        "FULL ATHLETICS FINANCIAL POSITION"
    )

    print(
        "================================="
    )

    print()

    print(
        f"Official Annual Budget:  "
        f"{money(annual)}"
    )

    print(
        f"Q1 Actual Spend:         "
        f"{money(actual)}"
    )

    print(
        f"Open / Committed:        "
        f"{money(committed)}"
    )

    print(
        f"Future Reserved:         "
        f"{money(future)}"
    )

    print(
        f"Projected Spend:         "
        f"{money(projected)}"
    )

    print(
        f"Uncommitted Reserve:     "
        f"{money(reserve)}"
    )

    print()

    print(
        f"Department Forecast:     "
        f"{projected / annual * 100:.1f}%"
    )


# ============================================================
# DISPLAY SPORT POSITION
# ============================================================


def display_sports(
    budget_rows,
    ledger,
    future
):

    print()
    print(
        "SPORT OPERATING POSITION"
    )

    print(
        "========================"
    )

    for budget_row in budget_rows:

        code = (
            budget_row[
                "program_code"
            ]
        )

        budget = float(
            budget_row[
                "category_budget"
            ]
        )

        actual = sum(
            float(row["amount"])
            for row in ledger
            if row[
                "program_code"
            ] == code
            and row[
                "transaction_type"
            ] == "ACTUAL"
        )

        open_po = sum(
            float(row["amount"])
            for row in ledger
            if row[
                "program_code"
            ] == code
            and row[
                "transaction_type"
            ] == "PO"
            and row[
                "status"
            ] == "OPEN"
        )

        future_spend = sum(
            float(row["amount"])
            for row in future
            if row[
                "program_code"
            ] == code
        )

        projected = (
            actual
            + open_po
            + future_spend
        )

        remaining = (
            budget
            - projected
        )

        percent = (
            projected
            / budget
        )

        status = financial_status(
            percent
        )

        print()

        print(
            f"{SPORTS[code]['name']} "
            f"({SPORTS[code]['season']})"
        )

        print(
            f"  Annual Operating Budget: "
            f"{money(budget)}"
        )

        print(
            f"  Q1 Actual Spend:          "
            f"{money(actual)}"
        )

        print(
            f"  Open POs:                 "
            f"{money(open_po)}"
        )

        print(
            f"  Future Planned Spend:     "
            f"{money(future_spend)}"
        )

        print(
            f"  Projected Year-End:       "
            f"{money(projected)}"
        )

        print(
            f"  Remaining Cushion:        "
            f"{money(remaining)}"
        )

        print(
            f"  Projected Budget Used:    "
            f"{percent * 100:.1f}%"
        )

        print(
            f"  KORBI Financial Status:   "
            f"{status}"
        )


# ============================================================
# DISPLAY FULL DEPARTMENT CATEGORIES
# ============================================================


def display_categories(
    snapshot
):

    print()
    print(
        "DEPARTMENT BUDGET CATEGORIES"
    )

    print(
        "============================"
    )

    for row in snapshot:

        print()

        print(
            row[
                "budget_category"
            ]
        )

        print(
            f"  Annual:      "
            f"{money(row['annual_budget'])}"
        )

        print(
            f"  Q1 Actual:   "
            f"{money(row['q1_actual'])}"
        )

        print(
            f"  Committed:   "
            f"{money(row['open_commitments'])}"
        )

        print(
            f"  Future:      "
            f"{money(row['future_reserved'])}"
        )

        print(
            f"  Reserve:     "
            f"{money(row['uncommitted_reserve'])}"
        )


# ============================================================
# BACKUP EXISTING BUDGET
# ============================================================


def backup_existing_budget():

    if (
        CATEGORY_BUDGET_FILE.exists()
        and not OLD_BUDGET_BACKUP.exists()
    ):

        shutil.copy2(
            CATEGORY_BUDGET_FILE,
            OLD_BUDGET_BACKUP
        )


# ============================================================
# SAVE SIMULATION
# ============================================================


def save_simulation(
    budget_rows,
    ledger,
    future,
    department_snapshot,
    shared_operations
):

    backup_existing_budget()

    write_csv(
        CATEGORY_BUDGET_FILE,
        budget_rows,
        [
            "program_code",
            "program_name",
            "expense_category",
            "category_budget",
            "budget_status",
            "source",
            "notes",
        ]
    )

    write_csv(
        LEDGER_FILE,
        ledger,
        [
            "transaction_id",
            "program_code",
            "program_name",
            "expense_category",
            "transaction_type",
            "status",
            "vendor",
            "description",
            "amount",
            "transaction_date",
            "po_number",
            "notes",
        ]
    )

    write_csv(
        FUTURE_FILE,
        future,
        [
            "expense_id",
            "entry_date",
            "expected_date",
            "program_code",
            "program_name",
            "expense_category",
            "expense_type",
            "vendor",
            "description",
            "amount",
            "confidence",
            "status",
            "entered_by",
            "notes",
        ]
    )

    write_csv(
        DEPARTMENT_FILE,
        department_snapshot,
        [
            "budget_category",
            "annual_budget",
            "q1_actual",
            "open_commitments",
            "future_reserved",
            "projected_year_end",
            "uncommitted_reserve",
            "source_status",
            "simulation_reason",
        ]
    )

    write_csv(
        SHARED_OPERATIONS_FILE,
        shared_operations,
        [
            "shared_category",
            "annual_budget",
            "q1_actual",
            "open_commitments",
            "future_reserved",
            "projected_year_end",
            "uncommitted_reserve",
            "description",
            "data_status",
        ]
    )

    metadata = [

        {
            "scenario":
                "SONOMA YEAR 1 Q1 CLOSE",

            "simulation_date":
                SIMULATION_DATE,

            "annual_budget":
                ANNUAL_TOTAL,

            "sports":
                len(SPORTS),

            "budget_status":
                "SOURCE-BASED DEPARTMENT MODEL",

            "activity_status":
                "SIMULATED",

            "notes":
                (
                    "Q1 actuals, open POs, and future "
                    "expenses are test data for KORBI."
                ),
        }
    ]

    write_csv(
        SIMULATION_FILE,
        metadata,
        [
            "scenario",
            "simulation_date",
            "annual_budget",
            "sports",
            "budget_status",
            "activity_status",
            "notes",
        ]
    )


# ============================================================
# MAIN
# ============================================================


def run():

    print()
    print("KORBI")
    print("=====")

    print(
        "Knowledge & Operations Resource "
        "for Business Intelligence"
    )

    print()
    print(
        "SONOMA STATE ATHLETICS"
    )

    print(
        "YEAR 1 - Q1 CLOSED / Q2 BEGINNING"
    )

    print()
    print(
        "Simulation Date: "
        "October 1, 2027"
    )

    print(
        "Q1 Status: CLOSED"
    )

    print(
        "Competition Year: 2027-28"
    )

    print()
    print(
        f"Annual Athletics Plan: "
        f"{money(ANNUAL_TOTAL)}"
    )

    (
        budget_rows,
        allocations,
        shared
    ) = build_operating_allocations()

    (
        ledger,
        future
    ) = build_sport_activity(
        allocations
    )

    department_snapshot = (
        build_department_snapshot()
    )

    shared_operations = (
        build_shared_operations(
            shared
        )
    )

    display_department(
        department_snapshot
    )

    display_categories(
        department_snapshot
    )

    display_sports(
        budget_rows,
        ledger,
        future
    )

    print()
    print("SIMULATION DESIGN")
    print("=================")

    print()

    print(
        "Fall sports have meaningful travel "
        "and competition costs already posted."
    )

    print(
        "Winter sports have preseason spending "
        "but most competition costs remain ahead."
    )

    print(
        "Golf carries both fall and spring activity."
    )

    print(
        "Softball has limited Q1 travel spending "
        "but equipment, field, recruiting, and "
        "spring obligations are represented."
    )

    print()

    print(
        "Payroll and student aid remain protected "
        "department obligations."
    )

    print(
        "Shared athletics operations are tracked "
        "separately from individual team budgets."
    )

    print()

    print("DATA QUALITY")
    print("============")

    print()

    print(
        "Annual department budget: "
        "SOURCE-BASED"
    )

    print(
        "Sport structure: "
        "SOURCE-BASED"
    )

    print(
        "Sport operating allocations: "
        "PLANNING MODEL"
    )

    print(
        "Q1 transactions: "
        "SIMULATED"
    )

    print(
        "Open POs: "
        "SIMULATED"
    )

    print(
        "Future expenses: "
        "SIMULATED"
    )

    print(
        "Shared operations: "
        "SIMULATED"
    )

    print()
    print(
        "This will replace the current "
        "KORBI TEST ledger, future expense "
        "register, and sport planning budgets."
    )

    print()
    print(
        "The existing budget file will be "
        "backed up first."
    )

    while True:

        answer = input(
            "\nLoad realistic Q1-close "
            "simulation? (Y/N): "
        ).strip().upper()

        if answer == "Y":

            save_simulation(
                budget_rows,
                ledger,
                future,
                department_snapshot,
                shared_operations
            )

            print()
            print(
                "KORBI Q1 CLOSE LOADED"
            )

            print(
                "====================="
            )

            print()

            print(
                "KORBI is now positioned at "
                "October 1, 2027."
            )

            print()

            print(
                "Q1 actual expenses exist."
            )

            print(
                "Open purchase orders exist."
            )

            print(
                "Scheduled future expenses exist."
            )

            print(
                "Expected future expenses exist."
            )

            print(
                "Payroll obligations exist."
            )

            print(
                "Student aid obligations exist."
            )

            print(
                "Shared department operations exist."
            )

            print()

            print(
                "All simulated activity remains "
                "clearly marked as TEST DATA."
            )

            break

        if answer == "N":

            print()
            print(
                "SIMULATION CANCELLED"
            )

            print(
                "===================="
            )

            print(
                "No files were changed."
            )

            break

        print(
            "Enter Y or N."
        )


if __name__ == "__main__":

    try:

        run()

    except Exception as error:

        print()
        print(
            "KORBI SIMULATION ERROR"
        )

        print(
            "======================"
        )

        print(error)