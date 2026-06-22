from pydantic import BaseModel


class LoginSchema(BaseModel):
    login: str
    password: str