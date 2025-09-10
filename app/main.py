from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
import psycopg2
from psycopg2.extras import RealDictCursor 
from app.routes import expenses,income, savings  # your routes go here
from . import models
from app.routes import balance
from app.routes import summary
from app.routes import auth




# Create database tables from models
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(title="Expense Tracker")

# Allow frontend connections (CORS)
origins = [
    "http://localhost:8000",  # example frontend
    "https://www.google.com", # sample allowed domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

while True:
    try:
        conn= psycopg2.connect(host="db",database="FASTAPI", user="postgres", password="FF66fK0=", cursor_factory=RealDictCursor) #connect to the PostgreSQL database    
        cursor= conn.cursor() #create a cursor to execute SQL queries
        print("Connection to database successful")
        break
    except Exception as e: #if connection fails, print the error and try again
        print("Connection to database failed, retrying...")
        print("Error:", e)
        break
        time.sleep(2) #wait for 2 seconds before retrying

# Basic root route
@app.get("/")
def root():
    return {"message": "Welcome to Expense Tracker API!"}

# Include expense-related endpoints
app.include_router(expenses.router)
app.include_router(income.router)
app.include_router(savings.router)
app.include_router(balance.router)
app.include_router(summary.router)
app.include_router(auth.router)




