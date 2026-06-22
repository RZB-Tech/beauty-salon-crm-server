from fastapi import APIRouter, Depends, Request, Response, status
from src.core.dependencies.uow import UnitOfWork, get_uow_with_context
from src.schemas.auth.login import LoginSchema
from src.services.auth_service import AuthService

router = APIRouter()

def get_auth_service(uow: UnitOfWork = Depends(get_uow_with_context)) -> AuthService:
    return AuthService(uow=uow)

@router.post(
    "/login",
    status_code = status.HTTP_204_NO_CONTENT,
    description = "Возращает Cookie с access_token и refresh_token при успешной авторизации")
async def login(data: LoginSchema, response: Response,
                authService: AuthService = Depends(get_auth_service)):
    return await authService.login(data, response)

@router.post("/refresh", status_code=status.HTTP_204_NO_CONTENT)
async def refresh_tokens(
    request: Request, 
    response: Response, 
    authService: AuthService = Depends(get_auth_service)
):
    return await authService.refresh(request, response)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user(
    response: Response, 
    authService: AuthService = Depends(get_auth_service)
):
    return await authService.logout(response)