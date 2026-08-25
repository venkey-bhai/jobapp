# from datetime import date
# from typing import Optional

# from fastapi import UploadFile
# from pydantic import BaseModel, EmailStr


# class CandidateCreate(BaseModel):

#     # Personal Information
#     fullname: str
#     date_of_birth: date
#     gender: str
#     email: EmailStr
#     mobile: str
#     alternate_mobile: Optional[str] = None

#     # Address
#     current_address: Optional[str] = None
#     city: Optional[str] = None
#     state: Optional[str] = None
#     country: Optional[str] = None
#     pincode: Optional[str] = None

#     # Education
#     highest_qualification: str
#     college: Optional[str] = None
#     passing_year: Optional[int] = None
#     percentage: Optional[str] = None

#     # Professional
#     job_position: str
#     experience: str
#     current_company: Optional[str] = None
#     current_designation: Optional[str] = None
#     current_ctc: Optional[str] = None
#     expected_ctc: Optional[str] = None
#     notice_period: Optional[str] = None

#     # Skills
#     primary_skills: Optional[str] = None
#     secondary_skills: Optional[str] = None
#     languages_known: Optional[str] = None

#     # Additional Information
#     linkedin: Optional[str] = None
#     github: Optional[str] = None
#     portfolio: Optional[str] = None
#     why_join: Optional[str] = None

#     # Declaration
#     declaration: bool
#     resume: UploadFile= None


from typing import Optional
from pydantic import BaseModel, Field


class CandidateVoiceSchema(BaseModel):
    fullname: str = Field(description="Full name of candidate")
    gender: str = Field(description="Gender (e.g., Male, Female, Other)")
    email: str = Field(
        description="Email address. Transcribe accurately without spaces."
    )
    mobile: str = Field(description="Phone/Mobile number")
    position: str = Field(description="Job position applied for")

    qualification: Optional[str] = Field(
        default=None, description="Educational degree/qualification"
    )
    experience: Optional[str] = Field(
        default=None, description="Total work experience (e.g., 3 years)"
    )

    yearOfPassing: Optional[int] = Field(
        default=None, description="Graduation year as 4-digit integer"
    )
    percentage: Optional[float] = Field(
        default=None, description="Marks or CGPA percentage as float"
    )

    college: Optional[str] = Field(
        default=None, description="College or University name"
    )

    primarySkills: Optional[str] = Field(
        default=None, description="Primary technical skills"
    )
    secondarySkills: Optional[str] = Field(
        default=None, description="Secondary skills"
    )
    languagesKnown: Optional[str] = Field(
        default=None, description="Languages spoken/known"
    )