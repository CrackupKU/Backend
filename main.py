import firebase_admin
from fastapi import FastAPI, HTTPException
from decouple import config
from firebase_admin import credentials, firestore
from pydantic import BaseModel



cred = credentials.Certificate(config('CRED'))
firebase_admin.initialize_app(cred)

db = firestore.client()


app = FastAPI()

class User(BaseModel):
    username: str
    password: str
    
class VideoUpload(BaseModel):
    title: str
    videoUrl: str
    isAds: bool

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
    try:
        # Reference to the "videos" collection
        videos_ref = db.collection("videos")

        # Add a new document to the collection with the provided video data
        doc_ref = videos_ref.add({
            "title": video_data.title,
            "videoUrl": video_data.videoUrl,
            "isAds": video_data.isAds
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

    return {"video": video_data[0]}  # Returning the first video found (assuming there should be only one)


@app.get("/findNotDoneVideo")
def find_not_done_video():
    videos_ref = db.collection("videos")
    
    
    """
    return video base on status of uploading & processing of the same users
    ans: there is no attribute for checking status of the videos 
    """
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
        query = videos_ref.where("emotion", "array_contains", emo).limit(10).stream()

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
    
