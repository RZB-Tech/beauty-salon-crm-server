import string

from fastapi import HTTPException, Request, Response, status
from src.core.dependencies.uow import UnitOfWork
from src.schemas.auth.login import LoginResponseSchema, LoginSchema
from src.core.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from src.schemas.employee.response import EmployeeResponseBase
import secrets

from src.schemas.staff.request import StaffUpdatePasswordSchema

class AuthService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def login(self, data: LoginSchema, response: Response) -> LoginResponseSchema:
        staff = await self.uow.staffs.get(login = data.login)
        if staff is None:
            raise HTTPException(404, "Некорректный логин или пароль")
            
        if not staff.active:
            raise HTTPException(401, detail = "Пользователь неактивен")
        
        if not verify_password(staff.hashed_password, data.password):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Некорректный логин или пароль",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        
        employee = None
        if staff.employee_id:
            employee = await self.uow.employees.get(staff.employee_id)

        
        accessTokenPayload = {
            "sub": staff.login,
            "id": staff.id,
            "tenant_id": staff.tenant_id,
            "type": "access"
        }
        refreshTokenPayload = accessTokenPayload.copy()
        refreshTokenPayload["type"] = "refresh"

        accessToken = create_access_token(accessTokenPayload)
        refreshToken = create_refresh_token(refreshTokenPayload)

        response.set_cookie(
            key = "access_token",
            value = accessToken,
            httponly = True,
            secure = True,
            samesite = "lax"
        )

        response.set_cookie(
            key = "refresh_token",
            value = refreshToken,
            httponly = True,
            secure = True,
            samesite = "lax"
        )

        tenant = await self.uow.tenants.get(id = staff.tenant_id)

        return LoginResponseSchema(
            id = staff.id,
            tenant_id = staff.tenant_id,
            created_at = staff.created_at,
            updated_at = staff.updated_at,
            created_by = staff.created_by,
            archived = staff.archived,
            login=staff.login,
            employee=EmployeeResponseBase.model_validate(employee) if employee else None,
            firstname=staff.firstname,
            lastname=staff.lastname,
            middlename=staff.middlename,
            active=staff.active,
            staff_type=staff.staff_type,
            tenant_name = tenant.name
        )

    async def refresh(self, request: Request, response: Response):
        refreshToken = request.cookies.get("refresh_token")
        if not refreshToken:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing"
            )

        payload = decode_token(refreshToken) 
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен невалиден или время использования исчерпан"
            )
        
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Невалидный токен")

        login = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидное тело токена"
            )

        user = await self.uow.staffs.get(login = login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь неактивен"
            )

        accessTokenPayload = {
            "sub": user.login,
            "id": user.id,
            "tenant_id": user.tenant_id,
            "type": "access"
        }
        refreshTokenPayload = accessTokenPayload.copy()
        refreshTokenPayload["type"] = "refresh"

        accessToken = create_access_token(accessTokenPayload)
        refreshToken = create_refresh_token(refreshTokenPayload)

        response.set_cookie(
            key="access_token", 
            value=accessToken, 
            httponly=True, 
            secure=True, 
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token", 
            value=refreshToken, 
            httponly=True, 
            secure=True, 
            samesite="lax"
        )

    async def logout(self, response: Response):
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )

    async def change_password(self, data: StaffUpdatePasswordSchema):
        user = await self.uow.staffs.get(id = data.id)
        if user is None: raise HTTPException(404)

        verify = verify_password(user.hashed_password, data.oldPassword)
        print("reached service")
        if not verify: raise HTTPException(401)

        hashed = hash_password(data.newPassword)
        await self.uow.staffs.update(data.id, hashed_password = hashed)
    
    async def reset_password(self, id: int) -> str:
        user = await self.uow.staffs.get(id = id)
        if user is None: raise HTTPException(404)

        alphabet = (
            string.ascii_letters +
            string.digits +
            "!@#$%^&*-_=+?"
        )

        newPassword = "".join(secrets.choice(alphabet) for _ in range(16))

        hashed = hash_password(newPassword)
        await self.uow.staffs.update(id, hashed_password = hashed)
        return newPassword