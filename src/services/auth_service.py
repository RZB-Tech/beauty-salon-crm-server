from fastapi import HTTPException, Request, Response, status
from src.core.dependencies.uow import UnitOfWork
from src.schemas.auth.login import LoginResponseSchema, LoginSchema
from src.core.auth.security import verify_password, create_access_token, create_refresh_token, decode_token
from src.schemas.employee.response import EmployeeResponseBase

class AuthService():
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def login(self, data: LoginSchema, response: Response) -> LoginResponseSchema:
        staff = await self.uow.staffs.get(data.login)
        if not staff or not verify_password(staff.hashed_password, data.password):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect login or password",
                headers = {"WWW-Authenticate": "Bearer"}
            )
        if not staff.active:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Staff is inactive"
            )
        
        employee = None
        if staff.employee_id:
            employee = await self.uow.employees.get(staff.employee_id)

        
        tokenPayload = {
            "sub": staff.login,
            "id": staff.id,
            "tenant_id": staff.tenant_id
        }

        accessToken = create_access_token(tokenPayload)
        refreshToken = create_refresh_token(tokenPayload)

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

        return LoginResponseSchema(
            login=staff.login,
            employee=EmployeeResponseBase.model_validate(employee) if employee else None,
            firstname=staff.firstname,
            lastname=staff.lastname,
            middlename=staff.middlename,
            active=staff.active,
            staff_type=staff.staff_type,
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
                detail="Invalid or expired refresh token"
            )

        login = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = await self.uow.staffs.get(login)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User associated with this token no longer exists"
            )
        if not user.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive"
            )

        tokenPayload = {
            "sub": user.login,
            "id": user.id,
            "tenant_id": user.tenant_id
        }
        newAccessToken = create_access_token(tokenPayload)
        newRefreshToken = create_refresh_token(tokenPayload)

        response.set_cookie(
            key="access_token", 
            value=newAccessToken, 
            httponly=True, 
            secure=True, 
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token", 
            value=newRefreshToken, 
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