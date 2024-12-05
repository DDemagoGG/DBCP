from datetime import datetime, timedelta

from fastapi import *
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from schemas.shop import LoginShopForm
from schemas.user import LoginUserForm, RegisterUserForm
from services.auth import (
    authenticate_shop,
    authenticate_user,
    create_access_token,
    get_current_user,
    register_user,
)

router = APIRouter()

template = Jinja2Templates(directory="templates")


@router.get("/register", response_class=responses.HTMLResponse)
async def show_register_page(request: Request):
    return template.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_handle(user: RegisterUserForm):
    if await register_user(user):
        return Response(status_code=status.HTTP_201_CREATED)
    return Response(status_code=status.HTTP_409_CONFLICT)


@router.get("/user/login", response_class=responses.HTMLResponse)
async def show_login_page(request: Request):
    return template.TemplateResponse("UserLogin.html", {"request": request})


@router.post("/user/login")
async def login(user: LoginUserForm):
    user_model = await authenticate_user(user.username, user.password)
    if not user_model:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    access_token = create_access_token(id=user_model.user_id, role=user_model.role)
    new_response = Response(status_code=status.HTTP_200_OK)
    new_response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=datetime.utcnow() + timedelta(days=30),
    )
    return new_response


@router.get("/shop/login", response_class=responses.HTMLResponse)
async def show_login_page(request: Request):
    return template.TemplateResponse("ShopLogin.html", {"request": request})


@router.post("/shop/login")
async def login(response: Response, shop: LoginShopForm):
    shop_model = await authenticate_shop(shop.shopname, shop.password)
    if not shop_model:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    access_token = create_access_token(id=shop_model.shop_id, role="shop")
    new_response = Response(status_code=status.HTTP_200_OK)
    new_response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=datetime.utcnow() + timedelta(days=30),
    )
    return new_response
