from pydantic import BaseModel


class LoginOrSignUp(BaseModel):
    email: str
    password: str
