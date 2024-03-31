from fastapi import FastAPI, HTTPException
from firebase_admin import auth, credentials, firestore, initialize_app
from decouple import config
import os
import pyrebase

from models.database_model import Status, UserModel, VideoModel
from models.request_body import SignUpRequest, UploadRequest


cred = credentials.Certificate(config('CRED'))
initialize_app(cred)

config = {
    "apiKey": "AIzaSyCnKFxvLy787xvvLRvgOu9Sq2Nemb8Jrac",
    "authDomain": "crackup-c6205.firebaseapp.com",
    "databaseURL": "gs://crackup-c6205.appspot.com",
    "projectId": "crackup-c6205",
    "storageBucket": "crackup-c6205.appspot.com",
    "messagingSenderId": "183322287418",
    "appId": "1:183322287418:web:fa6e63de33a02778434403",
    "measurementId": "G-R0QWEL7K9Y",
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

db = firestore.client()

app = FastAPI()


@app.get("/")
def health_check():
    return {"message": "Good health check"}


@app.get("/videos")
def videos():
    videos_ref = db.collection("videos")
    docs = videos_ref.stream()

    video_list = []
    for doc in docs:
        video_list.append(doc.to_dict())
    return video_list


# @app.post("/login")
# async def login(request: SignUpRequest):
#     try:
#         user_credential = auth.get_user_by_email(
#             email=request.email,
#             # password=request.password
#         )
#         user_id = user_credential.uid

#         users_ref = db.collection("users")
#         user_doc = users_ref.document(user_id).get()
#         user_data = user_doc.to_dict() if user_doc.exists else {}

#         return {"message": "Login successful", "user_id": user_id, "user_data": user_data}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


@app.post("/signup")
async def signup(request: SignUpRequest):
    try:
        user_credential = auth.create_user(
            email=request.email,
            password=request.password
        )
        user_id = user_credential.uid
        user_model = UserModel(
            id=user_id,
            email=request.email,
            username=request.email.split("@")[0],
        )

        users_ref = db.collection("users")
        doc_ref = users_ref.document(user_id)
        doc_ref.set(user_model.model_dump())

        return {"message": "Signup successful", "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/upload")
async def upload(request: UploadRequest):
    """
    comment for temp in mocking
    response = requests.get(video_data.video_url)

    if response.status_code == 200:
        # Open the file in binary write mode and write the content of the response to it
        with open(video_data.title, 'wb') as f:
            f.write(response.content)
        print(f"Video downloaded successfully")
    else:
        print("Failed to download video")
    """

    try:
        videos_ref = db.collection("videos")
        doc_ref = videos_ref.document()

        video_model = VideoModel(
            id=doc_ref.id,
            filename=request.filename,
            title=request.title,
            caption=request.caption,
            videoUrl=request.videoUrl,
            status=Status.PROCESS,
            isAds=request.isAds,
            uploadBy=request.uploadBy,
            uploadDate=request.uploadDate,
        )

        doc_ref.set(video_model.model_dump())
        user_doc_ref = db.collection("users").document(request.uploadBy)
        user_doc_ref.update(
            {"uploadVideo": firestore.ArrayUnion([doc_ref.id])}
        )

        return {"message": "Document created successfully", "video_id": doc_ref.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/videos/{id}")
async def get_video(id: str):
    videos_ref = db.collection("videos")
    query = videos_ref.where("id", "==", id).limit(1).stream()

    # Iterate over the query results to fetch the actual data
    video_data = []
    for doc in query:
        video_data.append(doc.to_dict())

    # Check if any data was found for the given ID
    if not video_data:
        raise HTTPException(status_code=404, detail="Video not found")

    # Returning the first video found (assuming there should be only one)
    return {"video": video_data[0]}


@app.get("/videos/user/{user_id}")
async def get_user_videos(user_id: str):
    try:
        videos_ref = db.collection("videos")
        videos_query = videos_ref.where("uploadBy", "==", user_id)
        videos = videos_query.get()

        video_list = [video.to_dict() for video in videos]

        return {"video_list": video_list}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/findNotDoneVideo")
def find_not_done_video():
    """
    return video base on status of uploading & processing of the same users
    ans: there is no attribute for checking status of the videos 
    """
    videos_ref = db.collection("videos")

    pass


@app.put("/videos/chose/{id}")
def edit_title(id: str, title: str):
    try:
        # Reference to the "videos" collection
        videos_ref = db.collection("videos")
        query = videos_ref.where("id", "==", id).stream()

        # Update the document with the provided ID with the updated data
        for doc in query:
            # Update each document with the provided updated data
            doc.reference.update({
                "title": title
            })

        return {"message": "Document updated successfully"}
    except Exception as e:
        # Handle any potential errors
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/categories/{emo}")
async def get_videos_by_emo(emo: str):
    try:
        # Reference to the "videos" collection
        videos_ref = db.collection("videos")

        # Query the collection to find documents where "emo" array contains the specified value
        query = videos_ref.where(
            "emotion", "array_contains", emo).limit(10).stream()

        # Initialize a list to store the results
        video_list = []

        # Iterate over the query results
        for doc in query:
            # Convert Firestore document to a Python dictionary
            video_data = doc.to_dict()
            video_list.append(video_data)

        return {"videos": video_list}
    except Exception as e:
        # Handle any potential errors
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/videos/{id}")
async def delete_video_by_title(id: str):
    try:
        # Reference to the "videos" collection
        videos_ref = db.collection("videos")

        # Query the collection to find the document(s) with the specified title
        query = videos_ref.where("id", "==", id).stream()

        # Iterate over the query results
        for doc in query:
            # Delete each document found
            doc.reference.delete()

        return {"message": f"Video(s) with title '{id}' deleted successfully"}
    except Exception as e:
        # Handle any potential errors
        raise HTTPException(status_code=500, detail=str(e))
