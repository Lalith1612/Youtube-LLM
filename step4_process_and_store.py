# step4_process_and_store.py
import os
import json
import chromadb
import google.generativeai as genai

def process_and_store_transcripts(transcript_path: str, db_path: str):
    """
    Processes JSON transcripts, creates embeddings using Google AI, 
    and stores them in ChromaDB.

    Args:
        transcript_path: Folder containing the transcript JSON files.
        db_path: Path to store the ChromaDB database.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not found.")
        genai.configure(api_key=api_key)
        
        db_client = chromadb.PersistentClient(path=db_path)
    except Exception as e:
        print(f"Error initializing clients: {e}")
        return

    collection_name = "youtube_transcripts_google"
    print(f"Accessing ChromaDB collection: '{collection_name}'")
    collection = db_client.get_or_create_collection(name=collection_name)

    try:
        transcript_files = [f for f in os.listdir(transcript_path) if f.endswith('.json')]
        if not transcript_files:
            print(f"No transcript files found in '{transcript_path}'.")
            return
    except FileNotFoundError:
        print(f"Error: The directory '{transcript_path}' was not found.")
        return

    print(f"Found {len(transcript_files)} transcripts to process.")

    for filename in transcript_files:
        transcript_file_path = os.path.join(transcript_path, filename)
        print(f"-> Processing: {filename}...")

        with open(transcript_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        video_title = os.path.splitext(filename)[0]

        for segment in data['segments']:
            text = segment['text']
            start_time = segment['start']
            chunk_id = f"{video_title}_{start_time}"

            try:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="RETRIEVAL_DOCUMENT"
                )
                embedding = result['embedding']
            except Exception as e:
                print(f"   Could not get embedding for chunk: {text[:30]}... Error: {e}")
                continue

            collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[{"source": video_title, "start_time": start_time}],
                ids=[chunk_id]
            )

        print(f"   Done. Stored {len(data['segments'])} segments in the database.")

    print(f"\n--- Processing and storing complete! ---")
    print(f"Total documents in collection: {collection.count()}")