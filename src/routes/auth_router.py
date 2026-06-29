from fastapi import APIRouter, Body, Depends, Request, Response
from src.core.dependencies.auth import get_current_staff
from src.core.dependencies.uow import make_service_dependency
from src.schemas.auth.login import LoginResponseSchema, LoginSchema
from src.schemas.staff.request import StaffUpdatePasswordSchema
from src.services.auth_service import AuthService

router = APIRouter()

get_auth_service = make_service_dependency(AuthService)

@router.post(
    "/login",
    status_code = 200,
    response_model = LoginResponseSchema,
    description = "Возращает Cookie с access_token, refresh_token и информацию о пользователи при успешной авторизации")
async def login(data: LoginSchema, response: Response,
                authService: AuthService = Depends(get_auth_service)):
    return await authService.login(data, response)

@router.post("/refresh", status_code = 204)
async def refresh_tokens(
    request: Request, 
    response: Response, 
    authService: AuthService = Depends(get_auth_service)
):
    return await authService.refresh(request, response)

@router.post("/logout", status_code = 204)
async def logout_user(
    response: Response, 
    authService: AuthService = Depends(get_auth_service),
    current_staff: dict = Depends(get_current_staff)
):
    return await authService.logout(response)

# @router.post(
#     "/change-password",
#     status_code = 204)
# async def change_password(
#         data: StaffUpdatePasswordSchema,
#         authService: AuthService = Depends(get_auth_service),
#         current_staff: dict = Depends(get_current_staff)):
#     return await authService.change_password(data = data)

@router.patch(
    "/reset-password",
    status_code = 200,
    response_model = str)
async def reset_password(
        id: int,
        authService: AuthService = Depends(get_auth_service),
        current_staff: dict = Depends(get_current_staff)):
    return await authService.reset_password(id)