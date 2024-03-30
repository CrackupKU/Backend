from enum import Enum
from pydantic import BaseModel
from typing import List


class Emotion(str, Enum):
    FEAR = "FEAR"
    HAPPY = "HAPPY"
    ANGRY = "ANGRY"
    SAD = "SAD"
    NEUTRAL = "NEUTRAL"
    SURPRISE = "SURPRISE"


class Status(str, Enum):
    PROCESS = "PROCESS"
    PUBLISH = "PUBLISH"


class VideoModel(BaseModel):
    id: str
    title: str
    caption: str
    videoUrl: str
    emotion: Emotion = None
    status: Status
    isAds: bool
    processingUrl: str = ''
    emotionLength: List[List[float]] = []
    similarVideo: str = ''
    uploadBy: str
    uploadDate: str


class UserModel(BaseModel):
    id: str
    email: str
    username: str
    profilePic: str = ''
    uploadVideo: List[str] = []
    followingList: List[str] = []
    followerList: List[str] = []
