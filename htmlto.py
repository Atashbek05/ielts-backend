from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
import requests
import time

app = FastAPI()

# ===== CORS =====
origins = [
    "https://s-git-main-jaqqon9-6154s-projects.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CONFIG =====
AZURE_OPENAI_KEY = "BD51HHXZ4YMefPheyAd7YeqDBeFg9DAAJJ0YgQIuMCsFQc46cgdxJQQJ99CDACYeBjFXJ3w3AAABACOGTFpF"
AZURE_OPENAI_ENDPOINT = "https://atabek.openai.azure.com/"
AZURE_OPENAI_VERSION = "2024-12-01-preview"
AZURE_DEPLOYMENT = "gpt-5-chat"

VISION_ENDPOINT = "https://csasjdo.cognitiveservices.azure.com/"
VISION_KEY = "BPYdLSilsb7sBywnWGTQkAzBct66V4ZrWFtfcq0x2xUX4C4KEwxcJQQJ99CDACYeBjFXJ3w3AAAFACOG4xkZ"

# ===== CLIENT =====
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_VERSION
)


# ===== HEALTH CHECK =====
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ===== OCR =====
def extract_text(image_bytes: bytes):
    try:
        url = VISION_ENDPOINT + "vision/v3.2/read/analyze"

        headers = {
            "Ocp-Apim-Subscription-Key": VISION_KEY,
            "Content-Type": "application/octet-stream"
        }

        r = requests.post(url, headers=headers, data=image_bytes, timeout=30)

        if r.status_code != 202:
            return None

        operation_url = r.headers.get("Operation-Location")
        if not operation_url:
            return None

        for _ in range(20):
            result = requests.get(
                operation_url,
                headers={"Ocp-Apim-Subscription-Key": VISION_KEY},
                timeout=30
            ).json()

            status = result.get("status")

            if status == "succeeded":
                text = ""
                for page in result["analyzeResult"]["readResults"]:
                    for line in page["lines"]:
                        text += line["text"] + "\n"
                return text

            if status == "failed":
                return None

            time.sleep(1)

        return None

    except Exception as e:
        return f"OCR error: {str(e)}"


# ===== GPT =====
def ask_gpt(text: str):
    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are an IELTS examiner. Check grammar, vocabulary, coherence and give band score."},
                {"role": "user", "content": text}
            ],
            max_completion_tokens=800,
            temperature=1
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"GPT error: {str(e)}"


# ===== IELTS TEXT CHECK =====
@app.post("/ielts")
async def ielts(data: dict):
    try:
        text = data.get("text", "")

        if not text:
            return {"error": "No text provided"}

        result = ask_gpt(text)
        return {"result": result}

    except Exception as e:
        return {"error": str(e)}


# ===== OCR + IELTS =====
@app.post("/ocr")
async def ocr_api(file: UploadFile = File(...)):
    try:
        image = await file.read()

        text = extract_text(image)

        if not text:
            return {"text": "", "ielts": "OCR failed"}

        result = ask_gpt(text)

        return {
            "text": text,
            "ielts": result
        }

    except Exception as e:
        return {
            "text": "",
            "ielts": f"Server error: {str(e)}"
        }
