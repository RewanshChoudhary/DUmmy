from dotenv import load_dotenv
import google.generativeai as genai

import os
from pymongo import MongoClient
import json
from pymongo import MongoClient
load_dotenv()
QUESTION_DIR = os.getenv("QUESTION_DIR")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION_SYLLABUS = os.getenv("MONGO_COLLECTION_SYLLABUS")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

current_code="BITE303L"
exam_type="FAT"
syllabus = json.dumps(
db[MONGO_COLLECTION_SYLLABUS].find_one(
        {"course_code": "BITE303L"},
        {"_id": 0}
    ),
    indent=2
)

print(syllabus)
