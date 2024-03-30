from pydantic import BaseModel
from models.database_model import Status


class SignUpRequest(BaseModel):
    email: str
    password: str


class UploadRequest(BaseModel):
    title: str
    caption: str
    videoUrl: str
    isAds: bool
    uploadBy: str
    uploadDate: str
