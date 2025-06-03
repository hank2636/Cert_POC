from fastapi import APIRouter, Response, Request


router = APIRouter(prefix="/logout", tags=["logout"])

@router.post("/")
def logout(request: Request, response: Response):
    print("Request url:", request.url)
    # 清除 cookie
    response.delete_cookie("access_token")
    response.delete_cookie("csrf_token")
    return {"message": "Logged out"}