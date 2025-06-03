from sqlmodel import Session, select, create_engine
from fastapi import APIRouter
from app.models import Production
from typing import List
engine = create_engine("postgresql+psycopg2://omni:omni123@172.16.1.114/cert_demo")

router = APIRouter()

@router.get("/production", response_model=List[Production])
def read_hello():
    with Session(engine) as session:
        statement = select(Production)
        results = session.exec(statement).all()
        return results