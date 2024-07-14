import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import re
from datetime import datetime
from transformers import pipeline

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost:8080",  # Add your frontend URL here
    "http://127.0.0.1:8080",  # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Hugging Face pipeline
question_answering = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('subway_outlets.db')
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for outlet data
class Outlet(BaseModel):
    name: str
    address: str
    hours: str
    waze_link: str
    latitude: float
    longitude: float

class QueryModel(BaseModel):
    query: str

# API to fetch all outlets
@app.get("/outlets", response_model=list[Outlet])
def get_outlets():
    conn = get_db_connection()
    outlets = conn.execute('SELECT * FROM outlets').fetchall()
    conn.close()
    
    if not outlets:
        raise HTTPException(status_code=404, detail="No outlets found")
    
    return [dict(outlet) for outlet in outlets]

# API to fetch a single outlet by name
@app.get("/outlets/{name}", response_model=Outlet, description="Fetch an outlet by name. Sample query: 'Subway Menara UOA Bangsar'")
def get_outlet(name: str):
    conn = get_db_connection()
    outlet = conn.execute('SELECT * FROM outlets WHERE name = ?', (name,)).fetchone()
    conn.close()
    
    if not outlet:
        raise HTTPException(status_code=404, detail="Outlet not found")
    
    return dict(outlet)

# Function to parse closing time from hours string
def parse_closing_time(hours: str) -> datetime:
    try:
        times = re.findall(r'(\d{1,2}:\d{2}\s*[APM]+)', hours, re.IGNORECASE)
        if times:
            closing_times = [datetime.strptime(time.strip(), "%I:%M %p") for time in times]
            return max(closing_times)
        raise ValueError(f"Unrecognized time format: {hours}")
    except Exception as e:
        print(f"Error parsing time: {e}")
        return None

# Function to query the Hugging Face model
def query_huggingface(query: str, context: str):
    try:
        result = question_answering(question=query, context=context)
        return result["answer"]
    except Exception as e:
        print(f"Error querying Hugging Face model: {e}")
        return "There was an error processing your query."

# API to handle search queries using Hugging Face Transformers
@app.post("/search")
def search_outlets(query_model: QueryModel):
    query = query_model.query
    conn = get_db_connection()
    try:
        if re.search(r'closes the latest', query, re.IGNORECASE):
            outlets = conn.execute('SELECT * FROM outlets').fetchall()
            conn.close()
            if not outlets:
                raise HTTPException(status_code=404, detail="No outlets found")
            
            outlets_with_closing_times = [
                {**outlet, 'closing_time': parse_closing_time(outlet['hours'])}
                for outlet in outlets if parse_closing_time(outlet['hours'])
            ]
            sorted_outlets = sorted(outlets_with_closing_times, key=lambda x: x['closing_time'], reverse=True)
            return [dict(outlet) for outlet in sorted_outlets[:5]]

        elif re.search(r'closes the earliest', query, re.IGNORECASE):
            outlets = conn.execute('SELECT * FROM outlets').fetchall()
            conn.close()
            if not outlets:
                raise HTTPException(status_code=404, detail="No outlets found")
            
            outlets_with_closing_times = [
                {**outlet, 'closing_time': parse_closing_time(outlet['hours'])}
                for outlet in outlets if parse_closing_time(outlet['hours'])
            ]
            sorted_outlets = sorted(outlets_with_closing_times, key=lambda x: x['closing_time'])
            return [dict(outlet) for outlet in sorted_outlets[:5]]

        elif re.search(r'located in (\w+)', query, re.IGNORECASE):
            location = re.search(r'located in (\w+)', query, re.IGNORECASE).group(1)
            outlets = conn.execute('SELECT * FROM outlets WHERE address LIKE ?', ('%' + location + '%',)).fetchall()
            conn.close()
            return {"count": len(outlets), "outlets": [dict(outlet) for outlet in outlets]}

        else:
            context = "\n".join([f"{outlet['name']} located at {outlet['address']} operates {outlet['hours']}" for outlet in conn.execute('SELECT * FROM outlets').fetchall()])
            llm_response = query_huggingface(query, context)
            conn.close()
            return {"response": llm_response}

    except Exception as e:
        conn.close()
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
