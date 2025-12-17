import google.generativeai as genai

import os
from pdf2image import convert_from_path
import pytesseract
from pymongo import MongoClient
import json

from dotenv import load_dotenv
load_dotenv()
PDF_DIR = os.getenv("PDF_DIR")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION_SYLLABUS")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_PROMPT= """

You are given OCR-extracted text from an academic syllabus document.

Your task is to extract ONLY the syllabus structure strictly according to the rules below.

RULES (STRICT — NO EXCEPTIONS):

1. Extract ONLY the following fields:
   - course_code
   - course_title
   - modules

2. DO NOT include objectives, outcomes, textbooks, reference books, evaluation, or any other sections.

3. The course_code MUST:
   - Match this exact pattern: ABCD123L or ABC123L (uppercase letters + 3 digits + L)
   - Example: "BCHY101L"
   - If the document contains long or repeated strings like:
     "BCHY101L_ENGINEERING-CHEMISTRY_TH_1.0_68_BCHY101L..."
     you MUST extract ONLY the valid course code part: "BCHY101L"
   - course_code MUST ALWAYS be present. If not clearly found, return an empty string.

4. Modules must be extracted strictly module-wise:
   - Preserve exact module order as in the document
   - Preserve exact module titles
   - Preserve exact hours (if mentioned)
   - Extract topics exactly as written (no paraphrasing, no merging, no guessing)

5. Do NOT hallucinate:
   - If a module has no topics listed, return an empty topics array
   - If hours are not mentioned, return an empty string
   - If course_title is missing, return an empty string

6. Output MUST be:
   - Strictly valid JSON
   - No explanations
   - No comments
   - No markdown
   - No extra text before or after JSON

OUTPUT JSON SCHEMA (STRICT):

{
  
  "course_title": "",
  "modules": [
    {
      "module_number": "",
      "module_title": "",
      "hours": "",
      "topics": []
    }
  ]
}


"""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
coll = db[MONGO_COLLECTION]
print("Resolved PDF_DIR:", PDF_DIR)
print("Directory exists:", os.path.exists(PDF_DIR))
print("Files inside:", os.listdir(PDF_DIR))


def extract_ocr_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    text_chunks = []
    for page in pages:
        text_chunks.append(
            pytesseract.image_to_string(page, config="--psm 6")
        )
    return "\n".join(text_chunks)


def extract_syllabus_json(ocr_text):
    prompt = GEMINI_PROMPT + "\n\nOCR TEXT STARTS BELOW:\n\n" + ocr_text

   
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )


   
    raw = response.text
    if raw is None or raw.strip() == "":
        raise ValueError("Gemini returnedempty output check OCR or prompt.")

    return json.loads(raw)

def store_in_mongo(course_code, syllabus_json):
    doc = {
        "course_code": course_code,
        
        "extracted_syllabus": syllabus_json
        
    }
    # Inserts if not present and replaces if present
    coll.replace_one(
        {"course_code": course_code},  
        doc,                           
        upsert=True                    
    )




def process_folder():
    for file in os.listdir(PDF_DIR):
        if not file.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(PDF_DIR, file)
       
        ocr_text = extract_ocr_from_pdf(pdf_path)
      

        
        syllabus_json = extract_syllabus_json(ocr_text)

        filename_no_ext = os.path.splitext(file)[0]
        course_code = filename_no_ext.split("_")[0]

        store_in_mongo(course_code,  syllabus_json)

        print("Done:", course_code)


if __name__ == "__main__":
    process_folder()



