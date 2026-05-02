from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional
#from database.db_manager import get_engine

app = FastAPI()

from sqlalchemy import create_engine
import os

def get_engine():
    try:
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        db = os.getenv("DB_NAME", "kalnet_db")

        print("DEBUG:", host, port, user, db) 

        engine = create_engine(
            f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        )
        return engine

    except Exception as e:
        print(f"Engine creation failed: {e}")
        return None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Data(BaseModel):
    id: Optional[int] = None
    search: Optional[str] = None
    state: Optional[str] = None
    school_type: Optional[str] = None
    tier: Optional[str] = None
    has_email: Optional[bool] = None


@app.get("/leads")
def get_leads(
    id: Optional[int] = None,
    search: Optional[str] = None,
    state: Optional[str] = None,
    school_type: Optional[str] = None,
    tier: Optional[str] = None,
    has_email: Optional[bool] = None
):
    try:
        engine = get_engine()
        print("ENGINE:", engine)

        if engine is None:
            return {"error": "Database connection failed"}

        query = "SELECT * FROM institutions WHERE 1=1"
        params = {}

        if search:
            query += " AND name LIKE :search"
            params["search"] = f"%{search}%"

        if state:
            query += " AND state = :state"
            params["state"] = state

        if school_type:
            query += " AND school_type = :school_type"
            params["school_type"] = school_type

        if tier:
            query += " AND tier = :tier"
            params["tier"] = tier

        if has_email is not None:
            if has_email:
                query += " AND email != ''"
            else:
                query += " AND email = ''"

        print("QUERY:", query)
        print("PARAMS:", params)

        ans = pd.read_sql(query, engine, params=params)

        return {"message": ans.to_dict(orient="records")}

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}


@app.get("/leads/{id}")
def get_lead(id: int):
    try:
        engine = get_engine()

        if engine is None:
            return {"error": "Database connection failed"}

        query = "SELECT * FROM institutions WHERE id = :id"
        params = {"id": id}

        ans = pd.read_sql(query, engine, params=params)

        if ans.empty:
            return {"message": "No Record Found"}
        else:
            return {"message": ans.to_dict(orient="records")}

    except Exception as e:
        print("ERROR:", e)
        return {"error": str(e)}