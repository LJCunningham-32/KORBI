import csv
import re
from pathlib import Path
from collections import defaultdict


# --------------------------------------------------
# FILE LOCATIONS
# --------------------------------------------------

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "research_document_hits.csv"
)

OUTPUT_FILE = (
    PROJECT_FOLDER
    / "Data"
    / "Processed"
    / "financial_evidence_passages.csv"
)


# --------------------------------------------------
# NORMALIZE CONTEXT
# --------------------------------------------------

def normalize_context(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# --------------------------------------------------
# CREATE EVIDENCE FINGERPRINT
# --------------------------------------------------
#
# IMPORTANT:
#
# The previous version used part of the context
# to identify duplicates.
#
# That did not work because the same PDF page could
# generate slightly different context windows for
# different keywords.
#
# NEW METHOD:
#
# PDF:
#     source file + page number
#
# NO PAGE NUMBER:
#     source file + normalized context
#
# This lets:
#
# scholarship
# ticket
# fundraising
#
# on the same PDF page become ONE evidence page.
# --------------------------------------------------

def create_fingerprint(row):

    source_file = row["source_file"]

    page_number = row["page_number"]

    # ----------------------------------------------
    # PDF / PAGINATED DOCUMENT
    # ----------------------------------------------

    if page_number:

        return (
            source_file,
            page_number,
        )

    # ----------------------------------------------
    # NON-PAGINATED DOCUMENT
    # ----------------------------------------------

    context = normalize_context(
        row["context"]
    )

    return (
        source_file,
        context[:700],
    )


# --------------------------------------------------
# READ QUANTIFIED HITS
# --------------------------------------------------

def read_quantified_hits():

    if not INPUT_FILE.exists():

        print()
        print(
            "ERROR: Input file not found:"
        )

        print(
            INPUT_FILE
        )

        return []

    hits = []

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

            if (
                row["evidence_type"]
                == "QUANTIFIED"
            ):

                hits.append(
                    row
                )

    return hits


# --------------------------------------------------
# MERGE EVIDENCE PAGES
# --------------------------------------------------

def merge_passages(hits):

    grouped = defaultdict(list)

    # ----------------------------------------------
    # GROUP HITS
    # ----------------------------------------------

    for row in hits:

        fingerprint = (
            create_fingerprint(row)
        )

        grouped[
            fingerprint
        ].append(row)

    evidence_pages = []

    # ----------------------------------------------
    # BUILD ONE RECORD PER EVIDENCE PAGE
    # ----------------------------------------------

    for rows in grouped.values():

        first = rows[0]

        # ------------------------------------------
        # COMBINE SEARCH TERMS
        # ------------------------------------------

        search_terms = sorted(
            set(
                row["search_term"]
                for row in rows
            )
        )

        # ------------------------------------------
        # COMBINE DOLLAR AMOUNTS
        # ------------------------------------------

        dollar_amounts = []

        for row in rows:

            amounts = (
                row["dollar_amounts"]
                .split(" | ")
            )

            for amount in amounts:

                amount = amount.strip()

                if (
                    amount
                    and amount
                    not in dollar_amounts
                ):

                    dollar_amounts.append(
                        amount
                    )

        # ------------------------------------------
        # COMBINE FINANCIAL PHRASES
        # ------------------------------------------

        financial_phrases = []

        for row in rows:

            phrases = (
                row[
                    "strong_financial_phrases"
                ]
                .split(" | ")
            )

            for phrase in phrases:

                phrase = phrase.strip()

                if (
                    phrase
                    and phrase
                    not in financial_phrases
                ):

                    financial_phrases.append(
                        phrase
                    )

        # ------------------------------------------
        # HIGHEST SCORES FROM PAGE
        # ------------------------------------------

        highest_evidence_score = max(
            int(
                row[
                    "financial_evidence_score"
                ]
            )
            for row in rows
        )

        highest_total_score = max(
            int(
                row[
                    "total_score"
                ]
            )
            for row in rows
        )

        # ------------------------------------------
        # DOES ANY HIT CONTAIN FTE?
        # ------------------------------------------

        has_fte = any(
            row["has_fte"] == "YES"
            for row in rows
        )

        # ------------------------------------------
        # KEEP LONGEST CONTEXT
        # ------------------------------------------
        #
        # Different keywords may create different
        # context windows.
        #
        # For now, keep the longest one.
        # ------------------------------------------

        longest_context = max(
            (
                row["context"]
                for row in rows
            ),
            key=len
        )

        # ------------------------------------------
        # CREATE EVIDENCE PAGE
        # ------------------------------------------

        evidence_pages.append({

            "source_file":
                first["source_file"],

            "page_number":
                first["page_number"],

            "keyword_hits_on_page":
                len(rows),

            "total_score":
                highest_total_score,

            "financial_evidence_score":
                highest_evidence_score,

            "search_terms":
                " | ".join(
                    search_terms
                ),

            "dollar_amounts":
                " | ".join(
                    dollar_amounts
                ),

            "financial_phrases":
                " | ".join(
                    financial_phrases
                ),

            "has_fte":
                "YES"
                if has_fte
                else "NO",

            "context":
                longest_context,

            # --------------------------------------
            # FUTURE REVIEW FIELDS
            # --------------------------------------

            "review_status":
                "UNREVIEWED",

            "evidence_category":
                "",

            "financial_fact":
                "",

            "verified_amount":
                "",

            "fiscal_year":
                "",

            "notes":
                "",
        })

    return evidence_pages


# --------------------------------------------------
# SORT EVIDENCE
# --------------------------------------------------

def sort_passages(passages):

    return sorted(
        passages,
        key=lambda row: (
            -row[
                "financial_evidence_score"
            ],
            -row[
                "total_score"
            ],
            -row[
                "keyword_hits_on_page"
            ],
            row[
                "source_file"
            ],
            row[
                "page_number"
            ],
        )
    )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

def save_passages(passages):

    fieldnames = [
        "source_file",
        "page_number",
        "keyword_hits_on_page",
        "total_score",
        "financial_evidence_score",
        "search_terms",
        "dollar_amounts",
        "financial_phrases",
        "has_fte",
        "context",
        "review_status",
        "evidence_category",
        "financial_fact",
        "verified_amount",
        "fiscal_year",
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
            passages
        )


# --------------------------------------------------
# SHOW BEST EVIDENCE PAGES
# --------------------------------------------------

def show_best_passages(passages):

    print()
    print(
        "TOP UNIQUE FINANCIAL EVIDENCE PAGES"
    )

    print(
        "==================================="
    )

    for passage in passages[:10]:

        print()

        print(
            f"FILE: "
            f"{passage['source_file']}"
        )

        print(
            f"PAGE: "
            f"{passage['page_number']}"
        )

        print(
            f"KEYWORD HITS ON PAGE: "
            f"{passage['keyword_hits_on_page']}"
        )

        print(
            f"EVIDENCE SCORE: "
            f"{passage['financial_evidence_score']}"
        )

        print(
            f"SEARCH TERMS: "
            f"{passage['search_terms']}"
        )

        print(
            f"DOLLAR AMOUNTS: "
            f"{passage['dollar_amounts']}"
        )

        print(
            f"FTE: "
            f"{passage['has_fte']}"
        )

        print(
            "CONTEXT:"
        )

        print(
            passage["context"]
        )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

def show_summary(
    hits,
    passages
):

    print()
    print(
        "FINANCIAL EVIDENCE PROCESSOR"
    )

    print(
        "============================"
    )

    print(
        f"Quantified Keyword Hits: "
        f"{len(hits):,}"
    )

    print(
        f"Unique Evidence Pages: "
        f"{len(passages):,}"
    )

    duplicates_removed = (
        len(hits)
        - len(passages)
    )

    print(
        f"Duplicate/Overlapping Hits Collapsed: "
        f"{duplicates_removed:,}"
    )

    print()
    print(
        "Saved To:"
    )

    print(
        OUTPUT_FILE
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    hits = (
        read_quantified_hits()
    )

    if not hits:

        print()
        print(
            "No quantified financial evidence found."
        )

        return

    passages = (
        merge_passages(
            hits
        )
    )

    passages = (
        sort_passages(
            passages
        )
    )

    save_passages(
        passages
    )

    show_summary(
        hits,
        passages
    )

    show_best_passages(
        passages
    )


if __name__ == "__main__":
    main()