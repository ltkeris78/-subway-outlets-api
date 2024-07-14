# Subway Outlets API

![image](https://github.com/user-attachments/assets/e31e2887-1305-434a-9791-bc46b70a9690)

![image](https://github.com/user-attachments/assets/28847d0f-4bbd-4ac6-8b18-79e7ee30179a)

![image](https://github.com/user-attachments/assets/d050e65c-3f7b-44fa-9284-737372f1c2e0)

## Overview
This is a FastAPI-based application that manages Subway outlets' information in Kuala Lumpur. The application connects to an SQLite database and uses a Hugging Face Transformers model for advanced search queries. It includes endpoints to fetch all outlets, fetch an outlet by name, and handle complex search queries.

## Setup Instructions

### Prerequisites
- Python 3.8 to 3.11
- SQLite3

### Clone the Repository
```bash
git clone https://github.com/yourusername/subway-outlets-api.git
cd subway-outlets-api

python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

pip install -r requirements.txt

uvicorn main:app --reload

###



