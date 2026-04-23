from fastapi import FastAPI, UploadFile, File
from openai import AzureOpenAI
import requests

app = FastAPI()

# ===== GPT =====
client = AzureOpenAI(
    api_key="BD51HHXZ4YMefPheyAd7YeqDBeFg9DAAJJ0YgQIuMCsFQc46cgdxJQQJ99CDACYeBjFXJ3w3AAABACOGTFpF",
    azure_endpoint="https://atabek.openai.azure.com/",
    api_version="2024-12-01-preview"
)

DEPLOYMENT = "gpt-5-chat"

# ===== OCR =====
VISION_ENDPOINT = "https://csasjdo.cognitiveservices.azure.com/"
VISION_KEY = "BPYdLSilsb7sBywnWGTQkAzBct66V4ZrWFtfcq0x2xUX4C4KEwxcJQQJ99CDACYeBjFXJ3w3AAAFACOG4xkZ"


def ocr(image_bytes):
    url = VISION_ENDPOINT + "vision/v3.2/read/analyze"

    headers = {
        "Ocp-Apim-Subscription-Key": VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    r = requests.post(url, headers=headers, data=image_bytes)

    if r.status_code != 202:
        return None

    op = r.headers["Operation-Location"]

    while True:
        res = requests.get(op, headers={
            "Ocp-Apim-Subscription-Key": VISION_KEY
        }).json()

        if res["status"] == "succeeded":
            break

    text = ""
    for page in res["analyzeResult"]["readResults"]:
        for line in page["lines"]:
            text += line["text"] + "\n"

    return text


def ask_gpt(text):
    r = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are IELTS examiner"},
            {"role": "user", "content": text}
        ],
        max_completion_tokens=800,
        temperature=1
    )

    return r.choices[0].message.content


@app.post("/ielts")
def ielts(data: dict):
    return {"result": ask_gpt(data["text"])}


@app.post("/ocr")
async def ocr_api(file: UploadFile = File(...)):
    img = await file.read()

    text = ocr(img)

    if not text:
        return {"text": "OCR failed", "ielts": ""}

    result = ask_gpt(text)

    return {
        "text": text,
        "ielts": result
    }