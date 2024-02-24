import firebase_admin
from fastapi import FastAPI
from decouple import config
from firebase_admin import credentials, firestore


cred = credentials.Certificate(config('CRED'))
firebase_admin.initialize_app(cred)

db = firestore.client()


app = FastAPI()


@app.get("/videos")
def videos():
    videos_ref = db.collection("videos")
    docs = videos_ref.stream()

    video_list = []
    for doc in docs:
        video_list.append(doc.to_dict())
    return video_list
