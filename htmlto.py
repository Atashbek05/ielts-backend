from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

materials = [
    {
        "id": 1,
        "title": "Writing Task 1 Template",
        "category": "Writing",
        "content": "Introduction + Overview + Details. Use formal academic style."
    },
    {
        "id": 2,
        "title": "Writing Task 2 Template",
        "category": "Writing",
        "content": "Introduction + Opinion + Arguments + Conclusion."
    },
    {
        "id": 3,
        "title": "Top 50 IELTS Vocabulary",
        "category": "Vocabulary",
        "content": "Significant, essential, decline, increase, impact, approach..."
    },
    {
        "id": 4,
        "title": "Reading Matching Headings Tips",
        "category": "Reading",
        "content": "Read headings first, identify keywords, match main idea not details."
    },
    {
        "id": 5,
        "title": "Listening Section Tips",
        "category": "Listening",
        "content": "Predict answers, listen for synonyms, check spelling carefully."
    }
]

@app.get("/")
def root():
    return {"status": "API is running"}

@app.get("/materials")
def get_materials():
    return materials

@app.get("/materials/{material_id}")
def get_material(material_id: int):
    for material in materials:
        if material["id"] == material_id:
            return material
    return {"message": "Material not found"}

@app.post("/ielts/writing")
def writing(data: dict):
    text = data.get("text", "")
    words = len(text.split())

    if words > 120:
        score = 8
    elif words > 60:
        score = 7
    else:
        score = 6

    return {"result": f"Your overall: {score}"}

@app.post("/ielts/reading")
def reading(data: dict):
    answers = data.get("answers", [])
    score = len(answers)
    return {"section": "Reading", "score": score}

@app.post("/ielts/listening")
def listening(data: dict):
    answers = data.get("answers", [])
    score = len(answers)
    return {"section": "Listening", "score": score}

@app.get("/mock/result")
def mock_result():
    return {
        "Writing": 7,
        "Reading": 8,
        "Listening": 7,
        "Overall": 7.5
    }
