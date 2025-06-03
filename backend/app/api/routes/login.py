import secrets
from datetime import timedelta
from typing import Annotated

from app import crud
from app.api.deps import CsrfDep, TokenVerDep
from app.core import security
from app.core.config import settings
from app.core.db import get_pg
from app.core.pg_engine import PsqlEngine
from app.core.security import get_password_hash, verify_password
from app.models import Message, NewPassword, NewPasswordForgot, user_email
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/login", tags=["login"])


# 登入路徑並回傳 JWT access-token
@router.post("/access-token")
def login_access_token(
    pg: Annotated[PsqlEngine, Depends(get_pg)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> JSONResponse:
    """
    OAuth2 compatible token login, get an access token for future requests
    SessionDep: 傳入 SQLAlchemy 的資料庫 session, 以進行 DB 查詢
    OAuth2PasswordRequestForm FastAPI 提供的內建表單模型，包含 username(實際是 email 傳送近來)
    和 password Depends() 自動解析並將解析後的結果注入到 form_data 中, 稱為依賴注入
    """
    # 驗證帳號密碼
    user = crud.authenticate(
        pg=pg, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="帳號或密碼錯誤, 請重新輸入!")
    elif not user.activate:
        raise HTTPException(status_code=400, detail="用戶已停用")

    # 設定 access_token expire
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    accesstoken = security.create_access_token(
        user.customer_id, expires_delta=access_token_expires
    )

    # 更新使用者登入時間
    crud.update_login_time(pg=pg, email=user.email)
    # 建立 csrf_token 由 32 bytes 的隨機字串
    csrf_token = secrets.token_urlsafe(32)
    # 將 access_token 寫入 cookie 中
    res = JSONResponse(
        content={"message": "Login successful", "csrf_token": csrf_token}
    )
    # res.set_cookie(
    #     key="access_token",
    #     value=accesstoken,
    #     httponly=True,  # 防止 JavaScript 存取（防 XSS）
    #     secure=False,  # 僅 HTTPS 傳送
    #     samesite="Strict",  # 防止 CSRF
    #     max_age=3600,  # 設定過期時間 (s) 1hr
    # )
    # # 設置 csrf_token 雙重認證 防 CSRF
    # res.set_cookie(
    #     key="csrf_token",
    #     value=csrf_token,
    #     httponly=False,  # 讓前端可以讀取
    #     secure=False,
    #     samesite="Strict",
    #     max_age=3600,
    # )

    res.set_cookie(
        key="access_token",
        value=accesstoken,
        httponly=True,  # 防止 JavaScript 存取（防 XSS）
        secure=True,  # 僅 HTTPS 傳送
        samesite="None",  # 防止 CSRF
        max_age=3600,  # 設定過期時間 (s) 1hr
    )
    # 設置 csrf_token 雙重認證 防 CSRF
    res.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,  # 讓前端可以讀取
        secure=True,
        samesite="None",
        max_age=3600,
    )

    return res


@router.post("/reset-password/")
def reset_password(
    pg: Annotated[PsqlEngine, Depends(get_pg)],
    body: NewPassword,
    __: TokenVerDep,
    _: CsrfDep,  # 暫時取消
) -> Message:
    """
    Reset password
    從正常密碼修改頁發送的重設密碼
    TokenVerDep 依賴驗證 access_token
    CsrfDep 依賴驗證 csrf_token
    """
    email = body.email
    if not email:
        raise HTTPException(status_code=400, detail="Invalid email")
    # 根據 email 取得 user 資料
    user = crud.get_user_by_email(pg=pg, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.activate:
        raise HTTPException(status_code=400, detail="Inactive user")
    # 驗證舊密碼
    oldpass = verify_password(body.old_password, user.password)
    if not oldpass:
        raise HTTPException(status_code=400, detail="Invalid old password.")
    # 加密新密碼
    hashed_password = get_password_hash(password=body.new_password)
    # 更新資料庫的密碼
    crud.update_password(pg=pg, email=email, hashed_password=hashed_password)
    return Message(message="Password updated successfully")


@router.post("/password-recovery")
def recover_password(
    pg: Annotated[PsqlEngine, Depends(get_pg)], body: user_email
) -> Message:
    """
    Password Recovery
    由忘記密碼頁請求發送重設密碼連結 email 的 api
    """
    user = crud.get_user_by_email(pg=pg, email=body.email)
    print(user)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=body.email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=body.email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password-forgot/")
def reset_password_forgot(
    pg: Annotated[PsqlEngine, Depends(get_pg)], body: NewPasswordForgot
) -> Message:
    """
    Reset password
    從 email 連結中導向的密碼修改頁所發出的
    """

    # 使用連結進來的頁面需驗證帶有 email 的 token
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    # 根據 email 取得 user 資料
    user = crud.get_user_by_email(pg=pg, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.activate:
        raise HTTPException(status_code=400, detail="Inactive user")
    # 驗證舊密碼
    oldpass = verify_password(body.old_password, user.password)
    if not oldpass:
        raise HTTPException(status_code=400, detail="Invalid old password.")
    # 加密新密碼
    hashed_password = get_password_hash(password=body.new_password)
    # 更新資料庫的密碼
    crud.update_password(pg=pg, email=email, hashed_password=hashed_password)

    return Message(message="Password updated successfully")
