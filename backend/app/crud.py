from typing import Any
import uuid
from sqlmodel import Session, select

from app.core.pg_engine import PsqlEngine
from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate
from datetime import timedelta, datetime, timezone

def create_user(*, pg:PsqlEngine, user_create: UserCreate) -> User:
    customer_id = str(uuid.uuid4())
    pay_methods = ['credit_card','line_pay']
    stmt =[(f'{customer_id}',
            f'{user_create.customer_name}',
            f'{user_create.email}',
            f'{user_create.phone_number}',
            f'{get_password_hash(user_create.password)}',
            f'{user_create.address}',
            pay_methods,
            False,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
            datetime.now(timezone.utc).date() + timedelta(days=365),
            0
            )]
    pg.insert_mogrify("app.customs", stmt)
    return customer_id


# def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
#     user_data = user_in.model_dump(exclude_unset=True)
#     extra_data = {}
#     if "password" in user_data:
#         password = user_data["password"]
#         hashed_password = get_password_hash(password)
#         extra_data["hashed_password"] = hashed_password
#     db_user.sqlmodel_update(user_data, update=extra_data)
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)
#     return db_user

def update_user(*, pg: PsqlEngine, email: str, update_data: dict):
    # 組合 SQL SET 子句
    set_clause = ", ".join([
        f"{key} = {value}"  # 防止 SQL injection
        for key, value in update_data.items()
    ])

    stmt = f"""
        UPDATE app.customs
        SET {set_clause}
        WHERE email = '{email}';
    """
    
    print(stmt)
    pg.execute_cmd(stmt)

    # 更新後重新讀取使用者並回傳
    return get_user_by_email(pg=pg, email=email)

def get_user_by_email(*, pg: PsqlEngine, email: str) -> User | None:
    """
    根據 email 取得 user 資料
    """
    stmt = f"""
    select * from app.customs where email = '{email}'; 
    """
    user = pg.execute_query(stmt, first=True)
    return user


def get_user_by_user_id(*, session: Session, user_id: str) -> User | None:
    statement = select(User).where(User.user_id == user_id)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, pg: PsqlEngine, email: str, password: str) -> User | None:
    # 根據 email 取得資料庫中使用者的所有訊息
    db_user = get_user_by_email(pg=pg, email=email)
    if not db_user:  # 回傳空則跳開
        return None
    # 驗證請求中的密碼是否與 hashed_password 解開後的一致
    if not verify_password(password, db_user.password):
        return None
    return db_user


def update_login_time(*, pg: PsqlEngine, email: str):
    stmt = f"""
        UPDATE app.customs
        SET last_login = NOW()
        WHERE email = '{email}';
    """
    pg.execute_cmd(stmt)


def update_password(*, pg: PsqlEngine, email: str, hashed_password: str):
    stmt = f"""
        UPDATE app.customs
        SET password = '{hashed_password}'
        WHERE email = '{email}';
    """
    pg.execute_cmd(stmt)
