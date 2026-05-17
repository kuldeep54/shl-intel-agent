import time
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from contextlib import asynccontextmanager
from vector_store import build_index, search
from agent import run_agent

# Simple in-memory rate limiter to prevent spam
RATE_LIMIT_SECONDS = 10
MAX_REQUESTS_PER_WINDOW = 5
ip_requests = defaultdict(list)

def check_rate_limit(ip: str):
    now = time.time()
    ip_requests[ip] = [t for t in ip_requests[ip] if now - t < RATE_LIMIT_SECONDS]
    if len(ip_requests[ip]) >= MAX_REQUESTS_PER_WINDOW:
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")
    ip_requests[ip].append(now)

index = None
catalog = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global index, catalog
    index, catalog, _ = build_index("catalog.json")
    print("Vector index ready")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str = Field(..., max_length=20)
    content: str = Field(..., max_length=1500) # Prevents massive text payloads

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., max_length=20) # Hard limit on message history length

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str
    description: str
    duration: str
    remote_testing: str
    adaptive: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, req: Request):
    client_ip = req.client.host if req.client else "127.0.0.1"
    check_rate_limit(client_ip)

    messages = [m.dict() for m in request.messages]

    if len(messages) > 16:
        raise HTTPException(status_code=400, detail="Conversation exceeds 8 turns")

    # build search query from last user message
    last_user_msg = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
    )

    # retrieve relevant assessments from catalog
    catalog_results = search(last_user_msg, index, catalog, top_k=10)

    # run agent
    result = run_agent(messages, catalog_results)

    return ChatResponse(**result)
