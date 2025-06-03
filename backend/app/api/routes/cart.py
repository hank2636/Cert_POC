from contextlib import asynccontextmanager
from datetime import datetime

from app.models import CartItemCreate, CartResponse, Order, OrderItem
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlmodel import Session, create_engine, select

# 資料庫配置
DATABASE_URL = "postgresql+psycopg2://omni:omni123@172.16.1.114/cert_demo"
engine = create_engine(DATABASE_URL)

router = APIRouter(prefix="/cart", tags=["cart"])


# FastAPI 應用
@asynccontextmanager
async def lifespan(app: FastAPI):
    Order.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# 資料庫 session 依賴
def get_session():
    with Session(engine) as session:
        yield session


# API 端點
@app.post("/cart/add", response_model=CartResponse)
async def add_to_cart(
    item: CartItemCreate,
    customer_id: str,
    customer_name: str,
    session: Session = Depends(get_session),
):
    # 檢查客戶是否已有未結帳的購物車 (status=True)
    existing_cart = session.exec(
        select(Order).where(Order.customer_id == customer_id, Order.status == True)
    ).first()

    if not existing_cart:
        # 創建新購物車
        cart = Order(
            customer_id=customer_id,
            customer_name=customer_name,
            status=True,
            total_amount=0,
            comment="新購物車",
        )
        session.add(cart)
        session.commit()
        session.refresh(cart)
    else:
        cart = existing_cart

    # 新增商品到購物車
    order_item = OrderItem(
        order_id=cart.order_id,
        license_id=item.license_id,
        license_name=item.license_name,
        quantity=item.quantity,
        price_at_order_time=item.price_at_order_time,
        created_by=item.created_by,
    )
    session.add(order_item)

    # 更新總金額
    cart.total_amount += item.quantity * item.price_at_order_time
    cart.updated_date = datetime.now()
    session.add(cart)
    session.commit()
    session.refresh(cart)

    return cart


@app.get("/cart/{customer_id}", response_model=CartResponse)
async def view_cart(customer_id: str, session: Session = Depends(get_session)):
    cart = session.exec(
        select(Order).where(Order.customer_id == customer_id, Order.status == True)
    ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="購物車不存在")

    return cart


@app.post("/cart/{customer_id}/checkout", response_model=CartResponse)
async def checkout(customer_id: str, session: Session = Depends(get_session)):
    cart = session.exec(
        select(Order).where(Order.customer_id == customer_id, Order.status == True)
    ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="購物車不存在")

    # 標記購物車為已結帳
    cart.status = False
    cart.updated_date = datetime.now()
    cart.comment = f"訂單於 {datetime.now()} 完成"
    session.add(cart)
    session.commit()
    session.refresh(cart)

    return cart


@app.delete("/cart/{customer_id}/item/{item_id}")
async def remove_item(
    customer_id: str, item_id: int, session: Session = Depends(get_session)
):
    cart = session.exec(
        select(Order).where(Order.customer_id == customer_id, Order.status == True)
    ).first()

    if not cart:
        raise HTTPException(status_code=404, detail="購物車不存在")

    item = session.exec(
        select(OrderItem).where(
            OrderItem.id == item_id, OrderItem.order_id == cart.order_id
        )
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 更新總金額
    cart.total_amount -= item.quantity * item.price_at_order_time
    cart.updated_date = datetime.now()

    # 移除商品
    session.delete(item)
    session.add(cart)
    session.commit()

    return {"message": "商品已從購物車移除"}
