from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/app_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Counter model
class Counter(Base):
    __tablename__ = "counter"
    id = Column(Integer, primary_key=True)
    value = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize counter if it doesn't exist
def init_counter():
    db = SessionLocal()
    counter = db.query(Counter).first()
    if not counter:
        counter = Counter(value=0)
        db.add(counter)
        db.commit()
    db.close()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv('FRONTEND_URL', 'http://localhost:3000')],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CounterResponse(BaseModel):
    count: int
    message: str

@app.get("/api/counter", response_model=CounterResponse)
async def get_counter(db: Session = Depends(get_db)):
    counter = db.query(Counter).first()
    return CounterResponse(count=counter.value, message="Current count retrieved")

@app.post("/api/counter/increment", response_model=CounterResponse)
async def increment_counter(db: Session = Depends(get_db)):
    counter = db.query(Counter).first()
    counter.value += 1
    db.commit()
    return CounterResponse(count=counter.value, message="Counter incremented")

@app.on_event("startup")
async def startup_event():
    init_counter()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
