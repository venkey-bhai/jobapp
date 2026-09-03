from typing import Text, TypedDict

from bson import ObjectId


class StudentDocument(TypedDict, total=False):
    """Shape of a student document stored in MongoDB."""

    _id: ObjectId
    fullname: str
    gender: str
    email: str
    mobile: str

    position: str
    qualification: str | None
    experience: str | None

    yearOfPassing: int | None
    percentage: float | None

    college: str | None

    primarySkills: str | None
    secondarySkills: str | None
    languagesKnown: str | None
    
    status: str | None
    resume: str | None
    