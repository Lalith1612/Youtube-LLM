import os
import re
import uuid
import asyncio
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import the functions from your scripts
from step2_download_audio import download_audio_from_playlist
from step3_transcribe_audio import transcribe_audio_files
from step4_process_and_store import process_and_store_transcripts
from step5_query_data import query_rag_model # We'll create this file next

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure CORS to allow your frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# In-memory storage for job status (in a real app, use Redis or a database)
job_status = {}

class PlaylistRequest(BaseModel):
    playlist_url: str

class AskRequest(BaseModel):
    question: str
    playlist_id: str

def get_playlist_id_from_url(url: str) -> str:
    """Extracts the playlist ID from a YouTube URL."""
    match = re.search(r"list=([\w-]+)", url)
    return match.group(1) if match else "default_playlist"

def process_pipeline(playlist_id: str, playlist_url: str):
    """The full data processing pipeline."""
    job_status[playlist_id] = {"status": "processing", "message": "Step 1/3: Starting audio download..."}
    
    audio_path = f"./data/{playlist_id}/audio"
    transcript_path = f"./data/{playlist_id}/transcripts"
    db_path = f"./data/{playlist_id}/vectordb"

    try:
        # Step 1: Download
        print(f"[{playlist_id}] Downloading audio...")
        job_status[playlist_id]["message"] = "Step 1/3: Downloading audio from playlist. This can take a while..."
        download_audio_from_playlist(playlist_url, audio_path)

        # Step 2: Transcribe
        print(f"[{playlist_id}] Transcribing audio...")
        job_status[playlist_id]["message"] = "Step 2/3: Transcribing audio files..."
        transcribe_audio_files(audio_path, transcript_path)

        # Step 3: Process and Store
        print(f"[{playlist_id}] Processing transcripts and storing in DB...")
        job_status[playlist_id]["message"] = "Step 3/3: Creating embeddings and storing in database..."
        process_and_store_transcripts(transcript_path, db_path)

        job_status[playlist_id] = {"status": "complete", "message": "Processing complete! You can now ask questions."}
        print(f"[{playlist_id}] Processing complete.")
    except Exception as e:
        print(f"Error processing {playlist_id}: {e}")
        job_status[playlist_id] = {"status": "error", "message": f"An error occurred: {e}"}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serves the main HTML file."""
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

@app.post("/process-playlist")
async def process_playlist(request: PlaylistRequest, background_tasks: BackgroundTasks):
    """Starts the background task to process a playlist."""
    playlist_id = get_playlist_id_from_url(request.playlist_url)
    
    if playlist_id in job_status and job_status[playlist_id]["status"] == "processing":
        raise HTTPException(status_code=400, detail="This playlist is already being processed.")

    job_status[playlist_id] = {"status": "queued", "message": "Playlist accepted and queued for processing."}
    background_tasks.add_task(process_pipeline, playlist_id, request.playlist_url)
    return {"message": "Playlist processing started in the background.", "playlist_id": playlist_id}

@app.get("/status/{playlist_id}")
async def get_status(playlist_id: str):
    """Checks the status of a processing job."""
    status = job_status.get(playlist_id)
    if not status:
        raise HTTPException(status_code=404, detail="Playlist ID not found.")
    return status

@app.post("/ask")
async def ask_question(request: AskRequest):
    """Handles asking a question to the RAG model."""
    db_path = f"./data/{request.playlist_id}/vectordb"
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Processed data for this playlist not found. Please process it first.")

    try:
        answer, sources = query_rag_model(request.question, db_path)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))