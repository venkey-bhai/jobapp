import os
import io
import json
import numpy as np
import speech_recognition as sr
import noisereduce as nr
from pydub import AudioSegment, effects
ffmpeg_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ffmpeg_path", "bin")
)
os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")
from bson import ObjectId
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, status
from file_handler import save_resume_file
from database import get_collection
from models import StudentDocument
from schemas import StudentResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(
    title=os.getenv("APP_NAME", "Code AI Careers"),
    version=os.getenv("APP_VERSION", "1.0.0"),
)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4",".webm"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "status": "Pending",
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
        "student": student_data,
    }


def convert_to_wav_bytes(message: bytes, filename: str, reduction_strength: float = 0.5) -> io.BytesIO:
    """Converts M4A, MP3, or other audio formats into Speech-Recognition ready WAV with noise reduction."""
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    try:
        # 1. Load audio segment from bytes
        audio_segment = AudioSegment.from_file(io.BytesIO(message))

        # 2. Force 16kHz sample rate, Mono, 16-bit PCM (2 bytes per sample) FIRST
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # 3. Normalize peak volume
        audio_segment = effects.normalize(audio_segment)

        # 4. Safely extract raw audio bytes into a NumPy array
        raw_samples = audio_segment.raw_data
        if not raw_samples:
            raise ValueError("Audio segment contains no raw data.")

        samples = np.frombuffer(raw_samples, dtype=np.int16).astype(np.float32)

        # 5. Check if array is empty or silent before running noisereduce
        if samples.size == 0:
            raise ValueError("Extracted audio array is empty.")

        # 6. Apply Noise Reduction safely
        cleaned_samples = nr.reduce_noise(
            y=samples,
            sr=16000,
            prop_decrease=reduction_strength,
            stationary=True
        )

        # 7. Convert back to int16 Pydub AudioSegment
        cleaned_bytes = cleaned_samples.astype(np.int16).tobytes()
        cleaned_audio = AudioSegment(
            cleaned_bytes,
            frame_rate=16000,
            sample_width=2,
            channels=1
        )

        # 8. Export clean audio stream
        wav_buffer = io.BytesIO()
        cleaned_audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        return wav_buffer

    except Exception as e:
        print(f"Audio Processing Error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process {ext} audio file: {str(e)}",
        )

@app.post("/students/search/voice")
async def search_student_by_voice(
    file: UploadFile = File(
        ..., description="Upload an audio file (.wav, .mp3, .m4a)"
    )
):
    try:
        # Step A: Read raw audio bytes and validate size
        raw_message = await file.read()
        if len(raw_message) == 0:
            raise HTTPException(
                status_code=400, detail="Uploaded audio file is empty."
            )

        # Step B: Convert to noise-reduced WAV stream
        wav_stream = convert_to_wav_bytes(raw_message, file.filename)

        # Step C: Speech-to-Text Transcription
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_stream) as source:
            # Note: adjust_for_ambient_noise is omitted to prevent cropping short audio clips
            audio_data = recognizer.record(source)

        transcript = recognizer.recognize_google(audio_data)

        search_term = transcript.strip()
        collection = get_collection("students")
        query = {"fullname": {"$regex": search_term, "$options": "i"}}
        students = [
            student_helper(student)
            async for student in collection.find(query)
        ]

        return {
            "transcript": transcript,
            "search_term": search_term,
            "students": students,
        }

    except sr.UnknownValueError:
        raise HTTPException(
            status_code=422,
            detail="Speech could not be recognized. Please record in a quieter environment.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Voice search failed: {str(e)}"
        )






#web scocket


@app.websocket("/ws/search-student")
@app.websocket("/ws/student-search")
async def student_search_websocket(
    websocket: WebSocket
):

    await websocket.accept()

    print("🟢 WebSocket connected")

    try:

        while True:

            # Receive either text or binary data
            message = await websocket.receive()


            # =====================================================
            # VOICE / AUDIO
            # =====================================================

            if message.get("bytes") is not None:

                audio_bytes = message["bytes"]

                print(
                    f"🎤 Received audio: "
                    f"{len(audio_bytes)} bytes"
                )

                try:

                    # ---------------------------------------------
                    # STEP 1: WebM → WAV
                    # ---------------------------------------------

                    wav_stream = convert_to_wav_bytes(
                        audio_bytes,
                        "voice-search.webm"
                    )

                    print("✅ WebM converted to WAV")


                    # ---------------------------------------------
                    # STEP 2: WAV → Speech
                    # ---------------------------------------------

                    recognizer = sr.Recognizer()

                    with sr.AudioFile(
                        wav_stream
                    ) as source:

                        audio_data = (
                            recognizer.record(source)
                        )


                    transcript = (
                        recognizer.recognize_google(
                            audio_data
                        )
                    )

                    print(
                        f"🗣️ Transcript: {transcript}"
                    )


                    # ---------------------------------------------
                    # STEP 3: Send transcript
                    # ---------------------------------------------

                    await websocket.send_json({

                        "type": "transcript",

                        "transcript": transcript

                    })


                except sr.UnknownValueError:

                    await websocket.send_json({

                        "type": "error",

                        "message":
                            "Could not understand the speech."

                    })


                except Exception as e:

                    print(
                        f"❌ Voice processing error: {e}"
                    )

                    await websocket.send_json({

                        "type": "error",

                        "message":
                            f"Voice processing failed: {str(e)}"

                    })


                continue


            # =====================================================
            # TEXT SEARCH
            # =====================================================

            if message.get("text") is not None:

                text_data = message["text"]

                print(
                    f"📩 Received text: {text_data}"
                )

                try:

                    data = json.loads(
                        text_data
                    )

                except json.JSONDecodeError:

                    await websocket.send_json({

                        "type": "error",

                        "message":
                            "Invalid JSON."

                    })

                    continue


                if data.get("action") == "search":

                    fullname = (
                        data
                        .get("fullname", "")
                        .strip().lower()
                    )


                    if not fullname:

                        await websocket.send_json({

                            "type": "error",

                            "message":
                                "student name is required."

                        })

                        continue


                    # ---------------------------------------------
                    # DATABASE SEARCH
                    # ---------------------------------------------

                    collection = get_collection("students")
                    query = {"fullname": {"$regex": fullname, "$options": "i"}}
                    students = [
                        student_helper(student)
                        async for student in collection.find(query)
                    ]


                    # ---------------------------------------------
                    # SEND RESULTS
                    # ---------------------------------------------

                    await websocket.send_json({

                        "type": "results",

                        "search_term": fullname,

                        "message":
                            f"Found {len(students)} student(s).",

                        "students": [

                            student.model_dump()
                            for student in students

                        ]

                    })


                else:

                    await websocket.send_json({

                        "type": "error",

                        "message":
                            "Unsupported WebSocket action."

                    })

                continue


    except WebSocketDisconnect:

        print(
            "🔴 WebSocket disconnected"
        )


    except Exception as e:

        print(
            f"❌ WebSocket error: {e}"
        )


    finally:

        print("🗄️ WebSocket closed")



# GET Endpoint: List all students
@app.get("/students/", response_model=list[StudentResponse])
async def get_students() -> list[StudentResponse]:
    students = []
    async for student in get_collection("students").find():
        students.append(student_helper(student))
    return students


# PUT Endpoint: Update a student's status
@app.put("/students/{student_id}/", status_code=status.HTTP_200_OK)
async def update_student_status(student_id: str, student_status: str = Form(..., alias="status")):
    if not ObjectId.is_valid(student_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID format."
        )

    result = await get_collection("students").update_one(
        {"_id": ObjectId(student_id)},
        {"$set": {"status": student_status}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Student application not found."
        )

    return {
        "success": True,
        "message": "Student status updated successfully."
    }


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
