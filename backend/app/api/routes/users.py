from typing import Annotated, Any
import ast, json
from app import crud
from app.api.deps import CurrentUser, verify_access_token
from app.core import security
from app.core.config import settings
from app.core.pg_engine import PsqlEngine
from app.models import UserBase, UserCreate, UserUpdate
from app.utils import generate_new_account_email, send_email
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/users", tags=["users"])


def get_pg():
    pg = PsqlEngine()
    return pg


# @router.get(
#     "/",
#     dependencies=[Depends(get_current_active_superuser)],
#     response_model=UsersPublic,
# )
# def read_users(pg: Annotated[PsqlEngine, Depends(get_pg)], skip: int = 0, limit: int = 100) -> Any:
#     """
#     檢索所有使用者, 暫時不開發
#     """
#     # count_statement = select(func.count()).select_from(User)
#     # statement = select(User).offset(skip).limit(limit)
#     return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserCreate)
def create_user(
    *, pg: Annotated[PsqlEngine, Depends(get_pg)], user_in: UserCreate
) -> Any:
    """
    註冊新用戶, 發送驗證信件
    """
    user = crud.get_user_by_email(pg=pg, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="此 Email 已存在",
        )
    customer_id = crud.create_user(pg=pg, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
            customer_id=customer_id,
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user_in


# # 點擊驗證信件後就可以啟用使用者
# @router.patch("/verify", response_model=UserBase)
# def update_user_me(
#     *,
#     pg: Annotated[PsqlEngine, Depends(get_pg)],
#     user_in: UserUpdate,
# ) -> Any:
#     """
#     根據信件連結啟用用戶
#     """
#     if user_in.email:
#         existing_user = crud.get_user_by_email(pg=pg, email=user_in.email)
#         # 確認使用者存在且傳送的 id 跟 資料庫 id 一致
#         if existing_user and existing_user.customer_id != user_in.customer_id:
#             raise HTTPException(
#                 status_code=409, detail="User with this email already exists"
#             )
#         elif not existing_user:
#             raise HTTPException(
#                 status_code=409, detail="User with this email already exists"
#             )
#     user_data = user_in.model_dump(exclude_unset=True)
#     user_in.sqlmodel_update(user_data)
#     return user_in


@router.get("/log")
def log():
    return {"message": "帳號啟用成功"}


@router.get("/verify")
def verify_user_from_token(token: str, pg: Annotated[PsqlEngine, Depends(get_pg)]):
    """
    ✅ 信件點擊後的 GET API：僅透過 token 啟用帳號，不需要 body
    """
    token_data = verify_access_token(token)
    data_dict = ast.literal_eval(token_data.sub)
    json_str = json.dumps(data_dict)
    user_data = json.loads(json_str)
    user_data = UserUpdate(**user_data)
    db_user = crud.get_user_by_email(pg=pg, email=user_data.email)
    print(db_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="使用者不存在")
    if not security.verify_password(user_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="密碼錯誤")

    crud.update_user(pg=pg, email=user_data.email, update_data={"activate": True})
    return {"message": "帳號啟用成功"}


# @router.patch("/me/password", response_model=Message)
# def update_password_me(
#     *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
# ) -> Any:
#     """
#     Update own password.
#     """
#     if not verify_password(body.current_password, current_user.hashed_password):
#         raise HTTPException(status_code=400, detail="Incorrect password")
#     if body.current_password == body.new_password:
#         raise HTTPException(
#             status_code=400, detail="New password cannot be the same as the current one"
#         )
#     hashed_password = get_password_hash(body.new_password)
#     current_user.hashed_password = hashed_password
#     session.add(current_user)
#     session.commit()
#     return Message(message="Password updated successfully")


@router.get("/me", response_model=UserBase)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user's information.
    """
    return current_user


# @router.delete("/me", response_model=Message)
# def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
#     """
#     Delete own user.
#     """
#     if current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="Super users are not allowed to delete themselves"
#         )
#     session.delete(current_user)
#     session.commit()
#     return Message(message="User deleted successfully")


# @router.post("/signup", response_model=UserBase)
# def register_user(session: SessionDep, user_in: UserRegister) -> Any:
#     """
#     Create new user without the need to be logged in.
#     """
#     user = crud.get_user_by_email(session=session, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists in the system",
#         )
#     user_create = UserCreate.model_validate(user_in)
#     user = crud.create_user(session=session, user_create=user_create)
#     return user


# @router.get("/{user_id}", response_model=UserBase)
# def read_user_by_id(
#     user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
# ) -> Any:
#     """
#     Get a specific user by id.
#     """
#     user = session.get(User, user_id)
#     if user == current_user:
#         return user
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403,
#             detail="The user doesn't have enough privileges",
#         )
#     return user


# @router.patch(
#     "/{user_id}",
#     dependencies=[Depends(get_current_active_superuser)],
#     response_model=UserBase,
# )
# def update_user(
#     *,
#     session: SessionDep,
#     user_id: uuid.UUID,
#     user_in: UserUpdate,
# ) -> Any:
#     """
#     Update a user.
#     """

#     db_user = session.get(User, user_id)
#     if not db_user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this id does not exist in the system",
#         )
#     if user_in.email:
#         existing_user = crud.get_user_by_email(session=session, email=user_in.email)
#         if existing_user and existing_user.id != user_id:
#             raise HTTPException(
#                 status_code=409, detail="User with this email already exists"
#             )

#     db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
#     return db_user


# @router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
# def delete_user(
#     session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
# ) -> Message:
#     """
#     Delete a user.
#     """
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user == current_user:
#         raise HTTPException(
#             status_code=403, detail="Super users are not allowed to delete themselves"
#         )
#     statement = delete(Item).where(col(Item.owner_id) == user_id)
#     session.exec(statement)  # type: ignore
#     session.delete(user)
#     session.commit()
#     return Message(message="User deleted successfully")
