from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory counter
counter = 0

class CounterResponse(BaseModel):
    count: int
    message: str

@app.get("/api/counter", response_model=CounterResponse)
async def get_counter():
    return CounterResponse(count=counter, message="Current count retrieved")

@app.post("/api/counter/increment", response_model=CounterResponse)
async def increment_counter():
    global counter
    counter += 1
    return CounterResponse(count=counter, message="Counter incremented")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
