from datetime import date
from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr


class CandidateCreate(BaseModel):

    # Personal Information
    fullname: str
    date_of_birth: date
    gender: str
    email: EmailStr
    mobile: str
    alternate_mobile: Optional[str] = None

    # Address
    current_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None

    # Education
    highest_qualification: str
    college: Optional[str] = None
    passing_year: Optional[int] = None
    percentage: Optional[str] = None

    # Professional
    job_position: str
    experience: str
    current_company: Optional[str] = None
    current_designation: Optional[str] = None
    current_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None
    notice_period: Optional[str] = None

    # Skills
    primary_skills: Optional[str] = None
    secondary_skills: Optional[str] = None
    languages_known: Optional[str] = None

    # Additional Information
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    why_join: Optional[str] = None

    # Declaration
    declaration: bool
    resume: UploadFile= None