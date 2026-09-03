import os

from bson import ObjectId
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile, status
from file_handler import save_resume_file
from database import get_collection
from models import StudentDocument
from schemas import StudentResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=os.getenv("APP_NAME", "Code AI Careers"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def student_helper(student: StudentDocument) -> StudentResponse:
    return StudentResponse(
        id=str(student["_id"]),
        fullname=student.get("fullname", student.get("name", "")),
        gender=student.get("gender", ""),
        email=student.get("email"),
        mobile=student.get("mobile", ""),
        position=student.get("position") or "",
        qualification=student.get("qualification") or "",
        experience=student.get("experience") or "",
        yearOfPassing=student.get("yearOfPassing") or "",
        percentage=student.get("percentage") or "",
        college=student.get("college") or "",
        primarySkills=student.get("primarySkills") or "",
        secondarySkills=student.get("secondarySkills") or "",
        languagesKnown=student.get("languagesKnown") or "",
        resume=student.get("resume") or "",
    )

@app.post("/students/upload_resume/", status_code=status.HTTP_201_CREATED)
async def add_student(
    fullname: str = Form(...),
    gender: str = Form(...),
    email: str = Form(...),
    mobile: str = Form(...),
    position: str = Form(""),
    qualification: str = Form(""),
    experience: str = Form(""),
    yearOfPassing: str = Form(""),
    percentage: str = Form(""),
    college: str = Form(""),
    primarySkills: str = Form(""),
    secondarySkills: str = Form(""),
    languagesKnown: str = Form(""),
    resume: UploadFile = File(...),
):

    if not fullname.strip():
        raise HTTPException(
            status_code=400,
            detail="Full name is required."
        )
    if not gender.strip():
        raise HTTPException(
            status_code=400,
            detail="Gender is required."
        )

    if not email.strip():
        raise HTTPException(
            status_code=400,
            detail="Email is required."
        )

    if not mobile.strip():
        raise HTTPException(
            status_code=400,
            detail="Mobile number is required."
        )

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required."
        )

    allowed_extensions = {
        ".pdf",
        ".doc",
        ".docx"
    }

    file_extension = os.path.splitext(
        resume.filename
    )[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOC, and DOCX files are allowed."
        )

    # Save uploaded file
    resume_name = save_resume_file(resume)

    student_data = {
        "fullname": fullname,
        "gender": gender,
        "email": email,
        "mobile": mobile,
        "position": position,
        "qualification": qualification,
        "experience": experience,
        "yearOfPassing": yearOfPassing,
        "percentage": percentage,
        "college": college,
        "primarySkills": primarySkills,
        "secondarySkills": secondarySkills,
        "languagesKnown": languagesKnown,
        "resume": resume_name,
    }
    
    # MongoDB inserts the record and automatically attaches a raw '_id' field inside student_data
    result = await get_collection("students").insert_one(student_data)

    # FIX: Explicitly convert the raw ObjectId to a clean string so FastAPI can parse it safely
    if "_id" in student_data:
        student_data["_id"] = str(student_data["_id"])

    return {
        "success": True,
        "message": "Application submitted successfully.",
        "id": str(result.inserted_id),
        "candidate": student_data,
    }


# GET Endpoint: List all students
@app.get("/students/", response_model=list[StudentResponse])
async def get_students() -> list[StudentResponse]:
    students = []
    async for student in get_collection("students").find():
        students.append(student_helper(student))
    return students


# DELETE Endpoint: Remove a student by their unique ID
@app.delete("/students/{student_id}/", status_code=status.HTTP_200_OK)
async def delete_student(student_id: str):
    # 1. Ensure the provided URL string is a structurally valid 24-character hex ObjectId
    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID format."
        )

    # 2. Look for the document and delete it using Motor's delete_one
    collection = get_collection("students")
    result = await collection.delete_one({"_id": ObjectId(student_id)}) #

    # 3. Check if a document was actually found and removed
    if result.deleted_count == 0: #
        raise HTTPException(
            status_code=404,
            detail="Student application not found."
        )

    return {
        "success": True,
        "message": f"Student with ID {student_id} was deleted successfully."
    }
    
# GET Endpoint: Search students by name
@app.get("/students/search/{fullname}/", response_model=list[StudentResponse])
async def search_students_by_name(fullname: str = ""):
    # If the user doesn't pass a name parameter, return an empty list or message
    if not fullname.strip():
         return []
         
    students = []
    collection = get_collection("students")
    
    # Use a case-insensitive regex search in MongoDB
    query = {"fullname": {"$regex": fullname, "$options": "i"}}
    
    async for student in collection.find(query):
        students.append(student_helper(student))
        
    return students
