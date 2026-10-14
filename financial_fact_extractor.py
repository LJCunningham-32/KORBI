import csv
import re
from pathlib import Path


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "financial_evidence_passages.csv"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "financial_fact_candidates.csv"
)


# --------------------------------------------------
# DOLLAR AMOUNT PATTERN
# --------------------------------------------------

DOLLAR_PATTERN = re.compile(
    r"\$\s*"
    r"\d{1,3}"
    r"(?:,\d{3})*"
    r"(?:\.\d+)?"
    r"(?:\s*[KkMm])?"
)


# --------------------------------------------------
# CLEAN TEXT
# --------------------------------------------------

def clean_text(text):

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


# --------------------------------------------------
# NORMALIZE DOLLAR VALUE
# --------------------------------------------------
#
# Examples:
#
# $595,956  -> 595956
# $70K      -> 70000
# $1.2M     -> 1200000
#
# We preserve the original value separately.
# --------------------------------------------------

def normalize_amount(amount_text):

    cleaned = (
        amount_text
        .replace("$", "")
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )

    multiplier = 1

    if cleaned.lower().endswith("k"):

        multiplier = 1000
        cleaned = cleaned[:-1]

    elif cleaned.lower().endswith("m"):

        multiplier = 1000000
        cleaned = cleaned[:-1]

    try:

        value = (
            float(cleaned)
            * multiplier
        )

        return round(value, 2)

    except ValueError:

        return ""


# --------------------------------------------------
# READ EVIDENCE PAGES
# --------------------------------------------------

def read_evidence_pages():

    if not INPUT_FILE.exists():

        print()
        print(
            "ERROR: Evidence file not found:"
        )

        print(
            INPUT_FILE
        )

        return []

    pages = []

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        for row in reader:

            pages.append(
                row
            )

    return pages


# --------------------------------------------------
# EXTRACT CANDIDATE FACTS
# --------------------------------------------------

def extract_candidates(page):

    context = page["context"]

    candidates = []

    matches = list(
        DOLLAR_PATTERN.finditer(
            context
        )
    )

    for number, match in enumerate(
        matches,
        start=1
    ):

        raw_amount = (
            match.group()
        )

        normalized_amount = (
            normalize_amount(
                raw_amount
            )
        )

        # ------------------------------------------
        # CAPTURE TEXT AROUND AMOUNT
        # ------------------------------------------

        context_start = max(
            0,
            match.start() - 160
        )

        context_end = min(
            len(context),
            match.end() + 220
        )

        local_context = clean_text(
            context[
                context_start:
                context_end
            ]
        )

        # ------------------------------------------
        # CAPTURE TEXT IMMEDIATELY BEFORE AMOUNT
        # ------------------------------------------
        #
        # This is useful because financial tables
        # frequently look like:
        #
        # Administrator Salary $595,956
        #
        # or
        #
        # Operating Fund Allocation $2,813,619
        # ------------------------------------------

        label_start = max(
            0,
            match.start() - 100
        )

        text_before_amount = clean_text(
            context[
                label_start:
                match.start()
            ]
        )

        candidates.append({

            "source_file":
                page["source_file"],

            "page_number":
                page["page_number"],

            "candidate_number":
                number,

            "raw_amount":
                raw_amount,

            "normalized_amount":
                normalized_amount,

            "text_before_amount":
                text_before_amount,

            "local_context":
                local_context,

            # --------------------------------------
            # REVIEW / STRUCTURED DATA FIELDS
            # --------------------------------------

            "review_status":
                "UNREVIEWED",

            "fiscal_year":
                "",

            "category":
                "",

            "subcategory":
                "",

            "description":
                "",

            "fact_type":
                "",

            "verified_amount":
                "",

            "include_in_model":
                "",

            "notes":
                "",
        })

    return candidates


# --------------------------------------------------
# PROCESS ALL EVIDENCE PAGES
# --------------------------------------------------

def process_pages(pages):

    all_candidates = []

    print()
    print(
        "FINANCIAL FACT EXTRACTION"
    )

    print(
        "========================="
    )

    for page in pages:

        candidates = (
            extract_candidates(
                page
            )
        )

        print()

        print(
            f"FILE: "
            f"{page['source_file']}"
        )

        print(
            f"PAGE: "
            f"{page['page_number']}"
        )

        print(
            f"Candidate Dollar Facts: "
            f"{len(candidates):,}"
        )

        all_candidates.extend(
            candidates
        )

    return all_candidates


# --------------------------------------------------
# SAVE CANDIDATES
# --------------------------------------------------

def save_candidates(candidates):

    fieldnames = [
        "source_file",
        "page_number",
        "candidate_number",
        "raw_amount",
        "normalized_amount",
        "text_before_amount",
        "local_context",
        "review_status",
        "fiscal_year",
        "category",
        "subcategory",
        "description",
        "fact_type",
        "verified_amount",
        "include_in_model",
        "notes",
    ]

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
            candidates
        )


# --------------------------------------------------
# SHOW SAMPLE
# --------------------------------------------------

def show_sample(candidates):

    print()
    print(
        "SAMPLE FACT CANDIDATES"
    )

    print(
        "======================"
    )

    for candidate in candidates[:15]:

        print()

        print(
            f"FILE: "
            f"{candidate['source_file']}"
        )

        print(
            f"PAGE: "
            f"{candidate['page_number']}"
        )

        print(
            f"AMOUNT: "
            f"{candidate['raw_amount']}"
        )

        print(
            f"NORMALIZED: "
            f"{candidate['normalized_amount']}"
        )

        print(
            "POSSIBLE LABEL:"
        )

        print(
            candidate[
                "text_before_amount"
            ]
        )

        print(
            "LOCAL CONTEXT:"
        )

        print(
            candidate[
                "local_context"
            ]
        )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def show_summary(
    pages,
    candidates
):

    unique_pages = len(
        {
            (
                row["source_file"],
                row["page_number"]
            )
            for row in pages
        }
    )

    print()
    print(
        "FACT EXTRACTION SUMMARY"
    )

    print(
        "======================="
    )

    print(
        f"Evidence Pages Read: "
        f"{unique_pages:,}"
    )

    print(
        f"Candidate Financial Facts: "
        f"{len(candidates):,}"
    )

    print()

    print(
        "Saved To:"
    )

    print(
        OUTPUT_FILE
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "These are candidate facts only."
    )

    print(
        "No extracted amount is considered "
        "verified yet."
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    pages = (
        read_evidence_pages()
    )

    if not pages:

        print(
            "No evidence pages available."
        )

        return

    candidates = (
        process_pages(
            pages
        )
    )

    save_candidates(
        candidates
    )

    show_summary(
        pages,
        candidates
    )

    show_sample(
        candidates
    )


if __name__ == "__main__":
    main()