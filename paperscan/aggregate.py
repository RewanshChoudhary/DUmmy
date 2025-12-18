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


stats_col = db["topic_stats"]
from pdf2image import convert_from_path
import pytesseract

def ocr_pdf_as_string(pdf_path: str) -> str:
    pages = convert_from_path(pdf_path, dpi=300)

    text = []
    for page in pages:
        text.append(pytesseract.image_to_string(page))

    return "\n\n".join(text)

def generate_prompt():
    current_code="BITE303L"
    exam_type="FAT"
    syllabus = json.dumps(
    db[MONGO_COLLECTION_SYLLABUS].find_one(
        {"course_code": "BITE303L"},
        {"_id": 0}
    ),
    indent=2
)
    questions=ocr_pdf_as_string("/home/rewansh57/Programming/mlstuff/data/QuestionPapers/BITE303L-FAT-A1-2024-2025.pdf")


    

    if syllabus is None:
        raise ValueError("NO SYLLABUS FOUND")
    else:
        print(syllabus)
    PROMPT_TEMPLATE = """
You are given:
1. A course syllabus in JSON format (modules and topics)
2. One exam question

Task:
Identify which syllabus topic(s) the question belongs to.

Rules:
- Choose ONLY from the topics explicitly listed in the syllabus JSON
- Do NOT invent topics
- Do NOT output module numbers
- If no topic matches, return an empty list
- Return valid JSON only

Syllabus:
{syllabus}

Question Paper :
{questions}

Output format:
{{
  "matched_topics": []
}}
"""


    return PROMPT_TEMPLATE.format(
    syllabus=syllabus,
    questions=questions
)


def call_llm() -> dict:
    prompt=generate_prompt()

    combined_response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    topic_json=combined_response.text


    if (topic_json is None or topic_json.strip()==""):
        return ValueError("Gemini returned an empty string")
    
    

    
    return json.loads(topic_json)



def process_paper():

    extracted_topics=call_llm()
    validated
   

    
if __name__=="__main__":
    process_paper()
