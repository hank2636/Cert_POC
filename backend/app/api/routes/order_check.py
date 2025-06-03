# from sqlmodel import Session, select, create_engine
from typing import List

from app.core import pg_engine
from app.models import ordercheck
from fastapi import APIRouter, HTTPException

# engine = create_engine("postgresql+psycopg2://omni:omni123@172.16.1.114/cert_demo")

router = APIRouter(prefix="/order_list", tags=["order_list"])

pg = pg_engine.PsqlEngine()
pg.connect_db()


@router.post("/order_list", response_model=List[ordercheck])
def order_list(valus):
    try:
        insert_query = """
                INSERT INTO app.cust_products_det VALUES
            """
        pg.insert_mogrify(insert_query, valus)
        return {"message": "Product added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
