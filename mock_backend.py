from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import time

app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    time.sleep(1) # Simulate thinking
    
    last_message = req.messages[-1].content.lower()
    
    reply = "I can help with that. Are you looking for technical assessments or personality tests?"
    recommendations = []
    end_of_conversation = False
    
    if "java" in last_message:
        reply = "Here are the top Java assessments we offer:"
        recommendations = [
            {"name": "Core Java (Advanced Level) (New)", "url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/", "test_type": "K", "duration": "13 minutes"},
            {"name": "Spring (New)", "url": "https://www.shl.com/products/product-catalog/view/spring-new/", "test_type": "K", "duration": "9 minutes"}
        ]
        end_of_conversation = True
    elif "personality" in last_message:
        reply = "Here is our most popular personality assessment:"
        recommendations = [
            {"name": "OPQ32r", "url": "https://www.shl.com/products/product-catalog/view/occupational-personality-questionnaire-opq32r/", "test_type": "P", "duration": "25 minutes"}
        ]
        end_of_conversation = True
        
    return {
        "reply": reply,
        "recommendations": recommendations,
        "end_of_conversation": end_of_conversation
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
