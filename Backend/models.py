from sqlalchemy import Column, Float, Integer, String, Text

try:
    from .database import Base
except ImportError:
    from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)

    fullname = Column(String(150), nullable=False)
    gender = Column(String(20), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    mobile = Column(String(20), nullable=False)

    position = Column(String(100), nullable=False)
    qualification = Column(String(150), nullable=True)
    experience = Column(String(50), nullable=True)

    yearOfPassing = Column(Integer, nullable=True)
    percentage = Column(Float, nullable=True)

    college = Column(String(200), nullable=True)

    primarySkills = Column(Text, nullable=True)
    secondarySkills = Column(Text, nullable=True)
    languagesKnown = Column(Text, nullable=True)
    
    status = Column(String(200), nullable=True, default="Pending")

    resume = Column(String(255), nullable=True)
    