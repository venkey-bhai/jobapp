from typing import Optional

from pydantic import BaseModel, EmailStr


class StudentResponse(BaseModel):
    """Student data returned from MongoDB."""

    id: str
    fullname: str = ""
    gender: str = ""
    email: Optional[EmailStr] = None
    mobile: str = ""
    position: str = ""
    qualification: Optional[str] = None
    experience: Optional[str] = None
    yearOfPassing: Optional[str] = None
    percentage: Optional[str] = None
    college: Optional[str] = None
    primarySkills: Optional[str] = None
    secondarySkills: Optional[str] = None
    languagesKnown: Optional[str] = None
    resume: Optional[str] = None