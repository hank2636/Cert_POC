from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel


# 使用者資料表中的欄位
class UserBase(SQLModel):
    customer_id: str = Field(max_length=100, primary_key=True)
    customer_name: str = Field(unique=True, max_length=50)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    phone_number: int
    address: str
    pay_methods: list
    activate: bool
    last_login: datetime
    created_at: datetime
    password_expiry: date
    password_reset_count: int


class UserPublic(SQLModel):
    customer_name: str = Field(unique=True, max_length=50)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    phone_number: str
    address: str


class Production(SQLModel, table=True):
    __tablename__ = "production"  # 明確指定資料表名稱
    __table_args__ = {"schema": "app"}  # 指定 schema

    license_id: str = Field(primary_key=True)
    license_name: Optional[str] = None
    license_info: Optional[str] = None
    exam_date: Optional[str] = None
    price: Optional[str] = None
    exam_location: Optional[str] = None
    registration_start: Optional[datetime] = None
    registration_end: Optional[datetime] = None
    display_status: Optional[int] = None
    created_at: Optional[datetime] = None
    picture_url: Optional[str] = None


class ordercheck(BaseModel):
    User_ID: int
    custom_name: str
    email: str
    phone: str
    license_id: int
    license_name: str  # 這兩個欄位不會存入 DB
    license_info: str


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "app"}

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="app.orders.order_id")

    license_id: str = Field(foreign_key="app.production.license_id")
    license_name: str
    quantity: int
    price_at_order_time: int
    created_by: str
    created_date: datetime = Field(default_factory=datetime.now)

    # 回到 Order 關聯
    order: Optional["Order"] = Relationship(back_populates="items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = {"schema": "app"}  # 指定 schema

    order_id: Optional[int] = Field(default=None, primary_key=True)
    customer_id: str
    customer_name: str
    status: bool
    total_amount: int
    comment: str
    created_date: datetime = Field(default_factory=datetime.now)
    updated_date: datetime = Field(default_factory=datetime.now)

    # 建立一對多關聯
    items: List[OrderItem] = Relationship(back_populates="order")


# Pydantic 模型用於請求和回應
class CartItemCreate(BaseModel):
    license_id: str
    license_name: str
    quantity: int
    price_at_order_time: int
    created_by: str


class CartResponse(BaseModel):
    order_id: int
    customer_id: str
    customer_name: str
    status: bool
    total_amount: int
    comment: str
    items: List[OrderItem]


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# Properties to receive via API on creation
class UserCreate(UserPublic):
    password: str = Field(min_length=7, max_length=40)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    customer_id: str = Field(max_length=100, primary_key=True)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=7, max_length=40)
    activate: bool


# Database model, database table inferred from class name
class User(UserBase):
    __tablename__ = "customs"
    __table_args__ = {"schema": "app"}
    password: str


# Generic message
class Message(SQLModel):
    message: str


class NewPassword(SQLModel):
    email: str | None
    old_password: str = Field(min_length=4, max_length=40)
    new_password: str = Field(min_length=4, max_length=40)


class NewPasswordForgot(SQLModel):
    email: str | None
    token: str | None
    old_password: str = Field(min_length=4, max_length=40)
    new_password: str = Field(min_length=4, max_length=40)


class user_email(SQLModel):
    email: str


# 檢索多個使用者資訊, 提供給管理員使用
class UsersPublic(SQLModel):
    data: list[UserBase]
    count: int
