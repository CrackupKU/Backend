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
    uploadBy: str
    title: str
    uploadDate: str
    videoUrl: str
    emotion: Emotion
    status: Status
    isAds: bool
    processingUrl: str
    emotionLength: List[List[float]]
    similarVideo: str


class UserModel(BaseModel):
    id: str
    username: str
    uploadVideo: List[str] = []
    email: str
    profilePic: str = ''
    followingList: List[str] = []
    followerList: List[str] = []
