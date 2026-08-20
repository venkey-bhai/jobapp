import csv
import shutil
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "candidates.csv"
UPLOAD_DIR = BASE_DIR / "uploads"
CSV_FIELDS = [
    "fullname",
    "email",
    "mobile",
    "position",
    "qualification",
    "experience", 
    "yearOfPassing",
    "percentage",
    "college",
    "primarySkills",
    "secondarySkills",
    "languagesKnown",
    "resume",
    "applied_date",
]


def ensure_storage():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # if not CSV_FILE.exists():
    #     with CSV_FILE.open("w", newline="", encoding="utf-8") as file:
    #         writer = csv.writer(file)
    #         writer.writerow(CSV_FIELDS)


def save_resume_file(resume_file: UploadFile) -> str:
    ensure_storage()

    original_name = resume_file.filename or "resume.pdf"
    safe_name = "".join(ch for ch in original_name if ch.isalnum() or ch in ("-", "_", "."))
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    saved_name = f"{timestamp}_{safe_name}"
    file_path = UPLOAD_DIR / saved_name

    with file_path.open("wb") as target_file:
        shutil.copyfileobj(resume_file.file, target_file)

    return saved_name


# def save_candidate(form_data: dict, resume_name: str):
#     ensure_storage()

#     row = [
#         (form_data.get("fullname") or "").strip(),
#         (form_data.get("email") or "").strip(),
#         (form_data.get("mobile") or "").strip(),
#         (form_data.get("position") or "Not specified").strip(),
#         (form_data.get("qualification") or "Not specified").strip(),
#         (form_data.get("experience") or "Not specified").strip(),
#         (form_data.get("yearOfPassing") or "Not specified").strip(),
#         (form_data.get("percentage") or "Not specified").strip(),
#         (form_data.get("college") or "Not specified").strip(),
#         (form_data.get("primarySkills") or "Not specified").strip(),
#         (form_data.get("secondarySkills") or "Not specified").strip(),
#         (form_data.get("languagesKnown") or "Not specified").strip(),
#         resume_name,
#         datetime.now().strftime("%d-%m-%Y %H:%M"),
#     ]

#     with CSV_FILE.open("a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         writer.writerow(row)

#     return dict(zip(CSV_FIELDS, row))


# def read_all_candidates():
#     ensure_storage()

#     with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
#         reader = csv.DictReader(file)
#         return list(reader)


# def search_candidate(full_name: str):
#     ensure_storage()

#     with CSV_FILE.open("r", encoding="utf-8", newline="") as file:
#         reader = csv.DictReader(file)

#         for row in reader:
#             if row.get("fullname", "").strip().lower() == full_name.strip().lower():
#                 return row

#     return None
