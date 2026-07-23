from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from google import genai
from backend.pdf_utils import extract_text_from_pdf
from backend.db import (
    save_message,
    get_chat_history,
    clear_chat_history
)
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

print("API Key:", os.getenv("GEMINI_API_KEY"))

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

# Store extracted PDF text
pdf_text = ""

# -----------------------------
# Gemini Client
# -----------------------------
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Request Models
# -----------------------------
class ChatRequest(BaseModel):
    message: str


class PDFQuestion(BaseModel):
    question: str


# -----------------------------
# Home API
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "AI Chatbot API is running"
    }


# -----------------------------
# Normal Chat API
# -----------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    try:
        # Save user message
        save_message("user", request.message)

        # Gemini response
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=request.message
        )

        # Save assistant response
        save_message("assistant", response.text)

        return {
            "reply": response.text
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# -----------------------------
# Upload PDF API
# -----------------------------
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global pdf_text

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from PDF
    pdf_text = extract_text_from_pdf(file_path)

    return {
        "message": "PDF uploaded successfully!",
        "filename": file.filename,
        "characters_extracted": len(pdf_text)
    }


# -----------------------------
# Ask Questions from Uploaded PDF
# -----------------------------
@app.post("/ask_pdf")
def ask_pdf(request: PDFQuestion):
    global pdf_text

    if not pdf_text.strip():
        return {
            "error": "No PDF uploaded. Please upload a PDF first."
        }

    # Save user question
    save_message("user", request.question)

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the information provided in the PDF below.

If the answer is not present in the PDF, reply exactly:
"I couldn't find the answer in the uploaded PDF."

---------------- PDF CONTENT ----------------

{pdf_text}

------------------------------------------------

Question:
{request.question}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        # Save assistant response
        save_message("assistant", response.text)

        return {
            "reply": response.text
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# -----------------------------
# Chat History API
# -----------------------------
@app.get("/history")
def history():

    chats = get_chat_history()

    return {
        "history": [
            {
                "role": role,
                "message": message,
                "timestamp": timestamp
            }
            for role, message, timestamp in chats
        ]
    }


# -----------------------------
# Clear Chat History API
# -----------------------------
@app.delete("/clear_history")
def clear_history():

    clear_chat_history()

    return {
        "message": "Chat history cleared successfully."
    }