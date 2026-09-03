# import os
# from motor.motor_asyncio import AsyncIOMotorClient

# # Replace with your local or MongoDB Atlas connection string
# MONGO_DETAILS = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# client = AsyncIOMotorClient(MONGO_DETAILS)

# # Define the database name
# database = client.students_db

# # Define the collection name
# student_collection = database.get_collection("students_collection")

import os
from motor.motor_asyncio import AsyncIOMotorClient

# 1. Paste your ACTUAL MongoDB Atlas connection string here
# IMPORTANT: Replace <db_username> and <db_password> with your Atlas database credentials
ATLAS_URI = "mongodb+srv://venkatj1986_db_user:VenkeyBhai1209@cluster0.70mhohb.mongodb.net/?appName=Cluster0&authSource=admin&readPreference=primary&ssl=true"

# 2. Automatically switches between Render's production settings and your laptop settings
MONGO_URI = os.getenv("MONGO_URL", ATLAS_URI)

# 3. Create the asynchronous database client
client = AsyncIOMotorClient(MONGO_URI)

# 4. Define your cloud database name
db = client["students_db"]

def get_collection(collection_name: str):
    return db[collection_name]