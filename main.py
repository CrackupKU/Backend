from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from firebase_admin import credentials, firestore, initialize_app
from decouple import config
import os
import pyrebase


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


class User(BaseModel):
    username: str
    password: str


class VideoUpload(BaseModel):
    title: str
    video_url: str
    is_ads: bool


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


@app.get("/login")
def login(user: User):
    username = user.username
    password = user.password

    users_ref = db.collection("users")
    query = users_ref.where("username", "==", username).limit(1).stream()
    for doc in query:
        user_data = doc.to_dict()
        # Check if password matches (assuming password is stored securely)
        if user_data.get("password") == password:
            return {"message": "Login successful", "user": user_data}

    raise HTTPException(status_code=401, detail="Invalid username or password")


@app.post("/signup")
async def signup(user: User):
    try:
        # Reference to the "users" collection
        users_ref = db.collection("users")

        # Add a new document to the collection with the provided user data
        doc_ref = users_ref.add({
            "username": user.username,
            "password": user.password
        })

        return {"message": "Document created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload")
async def upload(video_data: VideoUpload):
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
        # Create a directory with the specified name
        file = open(f'{video_data.title}.txt', 'w')
        file.close()
        print(f"Empty file '{video_data.title}' created successfully.")
    except FileExistsError:
        print(f"Folder '{video_data.title}' already exists.")

    storage.child(
        f"videos/{video_data.title}.txt").put(f'{video_data.title}.txt')

    os.remove(f"{video_data.title}.txt")

    try:
        videos_ref = db.collection("videos")

        # Add a new document to the collection with the provided video data
        doc_ref = videos_ref.add({
            "title": video_data.title,
            "videoUrl": video_data.video_url,
            "isAds": video_data.is_ads
        })

        return {"message": "Document created successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/video/{id}")
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


@app.get("/findNotDoneVideo")
def find_not_done_video():
    """
    return video base on status of uploading & processing of the same users
    ans: there is no attribute for checking status of the videos 
    """
    videos_ref = db.collection("videos")

    pass


@app.put("/video/chose/{id}")
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


@app.delete("/video/{id}")
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
