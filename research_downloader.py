import csv
import re
from pathlib import Path

import requests


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

DOCUMENT_FOLDER = (
    PROJECT_FOLDER
    / "Data"
    / "Raw"
    / "Research"
    / "Documents"
)

DOCUMENT_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

TIMEOUT = 30

HEADERS = {
    "User-Agent":
        "AI-Athletics-Research-Project/1.0"
}


# --------------------------------------------------
# CLEAN FILE NAMES
# --------------------------------------------------

def safe_filename(text):

    text = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        text
    )

    return text.strip("_")


# --------------------------------------------------
# LOAD REGISTRY
# --------------------------------------------------

def load_registry():

    if not REGISTRY_FILE.exists():

        print("ERROR: source_registry.csv not found.")
        return []

    with open(
        REGISTRY_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        return list(
            csv.DictReader(file)
        )


# --------------------------------------------------
# SAVE UPDATED REGISTRY
# --------------------------------------------------

def save_registry(sources):

    if not sources:
        return

    fieldnames = list(
        sources[0].keys()
    )

    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(sources)


# --------------------------------------------------
# DETERMINE FILE TYPE
# --------------------------------------------------

def determine_extension(
    url,
    content_type
):

    url_lower = url.lower()

    content_type = (
        content_type
        .lower()
    )

    if (
        ".pdf" in url_lower
        or "application/pdf" in content_type
    ):
        return ".pdf"

    if (
        "text/html" in content_type
        or url_lower.endswith("/")
    ):
        return ".html"

    if "text/csv" in content_type:
        return ".csv"

    if "application/json" in content_type:
        return ".json"

    return ".bin"


# --------------------------------------------------
# DOWNLOAD ONE SOURCE
# --------------------------------------------------

def download_source(source):

    source_id = source.get(
        "source_id",
        ""
    ).strip()

    url = source.get(
        "url",
        ""
    ).strip()

    authority = source.get(
        "authority_level",
        ""
    ).strip()

    status = source.get(
        "status",
        ""
    ).strip()

    # ----------------------------------------------
    # ONLY DOWNLOAD PRIMARY SOURCES FOR NOW
    # ----------------------------------------------

    if authority != "PRIMARY":
        return "IGNORED"

    # ----------------------------------------------
    # DON'T REDOWNLOAD EADA
    # ----------------------------------------------

    if source_id == "EADA_2024":
        return "EXISTING"

    # ----------------------------------------------
    # DON'T DOWNLOAD GENERIC RESEARCH PORTALS YET
    # ----------------------------------------------

    if status == "RESEARCH":
        return "IGNORED"

    if not url:
        return "IGNORED"

    # ----------------------------------------------
    # CHECK EXISTING LOCAL FILE
    # ----------------------------------------------

    existing_file = source.get(
        "local_file",
        ""
    ).strip()

    if existing_file:

        existing_path = (
            PROJECT_FOLDER
            / existing_file
        )

        if existing_path.exists():

            print(
                f"EXISTS: {source_id} -> "
                f"{existing_file}"
            )

            return "EXISTING"

    # ----------------------------------------------
    # DOWNLOAD
    # ----------------------------------------------

    print()
    print(
        f"DOWNLOADING: {source_id}"
    )

    print(
        f"URL: {url}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT,
            allow_redirects=True
        )

        response.raise_for_status()

    except requests.RequestException as error:

        print(
            f"FAILED: {source_id}"
        )

        print(
            f"Reason: {error}"
        )

        source["status"] = "DOWNLOAD_FAILED"

        return "FAILED"

    # ----------------------------------------------
    # DETERMINE FILE EXTENSION
    # ----------------------------------------------

    content_type = response.headers.get(
        "Content-Type",
        ""
    )

    extension = determine_extension(
        response.url,
        content_type
    )

    filename = (
        safe_filename(source_id)
        + extension
    )

    output_path = (
        DOCUMENT_FOLDER
        / filename
    )

    # ----------------------------------------------
    # SAVE ORIGINAL DOCUMENT
    # ----------------------------------------------

    with open(
        output_path,
        "wb"
    ) as file:

        file.write(
            response.content
        )

    # ----------------------------------------------
    # UPDATE REGISTRY
    # ----------------------------------------------

    relative_path = (
        output_path
        .relative_to(PROJECT_FOLDER)
        .as_posix()
    )

    source["local_file"] = (
        relative_path
    )

    source["status"] = "DOWNLOADED"

    print(
        f"SAVED: {relative_path}"
    )

    print(
        f"TYPE: {content_type}"
    )

    print(
        f"SIZE: "
        f"{len(response.content):,} bytes"
    )

    return "DOWNLOADED"


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    sources = load_registry()

    if not sources:
        return

    downloaded = 0
    existing = 0
    ignored = 0
    failed = 0

    print()
    print("ATHLETICS RESEARCH DOWNLOADER")
    print("=============================")

    for source in sources:

        result = download_source(
            source
        )

        if result == "DOWNLOADED":
            downloaded += 1

        elif result == "EXISTING":
            existing += 1

        elif result == "IGNORED":
            ignored += 1

        elif result == "FAILED":
            failed += 1

    # ----------------------------------------------
    # SAVE REGISTRY CHANGES
    # ----------------------------------------------

    save_registry(sources)

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    print()
    print("=============================")
    print("DOWNLOAD SUMMARY")
    print("=============================")

    print(
        f"Downloaded: {downloaded}"
    )

    print(
        f"Already Existing: {existing}"
    )

    print(
        f"Ignored For Now: {ignored}"
    )

    print(
        f"Failed: {failed}"
    )

    print()
    print(
        f"Documents Folder:"
    )

    print(
        DOCUMENT_FOLDER
    )


if __name__ == "__main__":
    main()