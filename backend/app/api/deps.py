from typing import Annotated, Optional

import jwt
from app.core import security
from app.core.config import settings
from app.core.db import get_pg
from app.core.pg_engine import PsqlEngine
from app.models import TokenPayload, User, UserBase
from fastapi import Cookie, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_token_from_cookie(access_token: Optional[str] = Cookie(...)) -> str:
    """
    根據 cookie 中取得 access_token, 確認為同一個登入者
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing access token in cookie",
        )
    return access_token


def verify_csrf_token(request: Request):
    """
    雙重驗證 csrf token, 從 cookie 及 headers 取出 csrf_token 比對,
    若一致才代表是同個登入者且同頁面發出的請求。
    """
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid CSRF token"
        )
    return True


TokenDep = Annotated[str, Depends(get_token_from_cookie)]
CsrfDep = Annotated[str, Depends(verify_csrf_token)]


def verify_access_token(token: TokenDep):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        return token_data
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


TokenVerDep = Annotated[str, Depends(verify_access_token)]


def get_current_user(
    pg: Annotated[PsqlEngine, Depends(get_pg)], token: TokenDep, _: CsrfDep
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    stmt = f"""
        select * from app.customs where customer_id = '{token_data.sub}'; 
    """
    user: UserBase = pg.execute_query(stmt, first=True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.activate:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.activate:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
