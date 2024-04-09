from typing import List
from pydantic import BaseModel
from models.database_model import Emotion, Status


class SignUpRequest(BaseModel):
    email: str
    password: str


class UploadRequest(BaseModel):
    filename: str
    title: str
    caption: str
    videoUrl: str
    isAds: bool
    uploadBy: str
    uploadDate: str


class EmotionWatchTimeEntry(BaseModel):
    emotion: Emotion
    duration: int = 0


class RecommendRequest(BaseModel):
    watchedTime: List[EmotionWatchTimeEntry]
    boundVideoIds: List[str]
