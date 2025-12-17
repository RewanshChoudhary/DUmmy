from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION_SYLLABUS = os.getenv("MONGO_COLLECTION_SYLLABUS")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def print_syllabus():
   

if __name__ == "__main__":
    print_syllabus()
