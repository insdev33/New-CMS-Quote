import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Vercel frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For security, replace "*" with ["https://your-vercel-app.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API key from environment variables
CMS_API_KEY = os.getenv("CMS_API_KEY")
CMS_BASE_URL = "https://developer.cms.gov/marketplace-api/v1"  # Ensure correct CMS API base URL

# Data model for request body
class QuoteRequest(BaseModel):
    zip_code: str
    income: float
    age: int
    household_size: int
    health_conditions: List[str]

@app.get("/")
def health_check():
    return {"message": "FastAPI backend is running!"}

@app.post("/get-quotes/")
def get_quotes(request: QuoteRequest):
    if not CMS_API_KEY:
        raise HTTPException(status_code=500, detail="CMS API Key is missing")

    headers = {"Authorization": f"Bearer {CMS_API_KEY}"}
    params = {
        "zip": request.zip_code,
        "income": request.income,
        "age": request.age,
        "householdSize": request.household_size,
        "conditions": ",".join(request.health_conditions),
    }

    try:
        response = requests.get(f"{CMS_BASE_URL}/plans", headers=headers, params=params)
        
        # Debugging log
        print("CMS API Response:", response.text)

        if response.status_code != 200:
            return {"error": response.status_code, "message": response.text}

        return response.json()
    
    except Exception as e:
        return {"error": "Internal Server Error", "details": str(e)}
