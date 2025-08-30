# step3_transcribe_audio.py
import os
import whisper
import json

def transcribe_audio_files(audio_path: str, transcript_path: str):
    """
    Transcribes all audio files in a directory using Whisper.

    Args:
        audio_path: The folder where the audio files are located.
        transcript_path: The folder where the transcript files will be saved.
    """
    # Create the transcript directory if it doesn't exist
    if not os.path.exists(transcript_path):
        os.makedirs(transcript_path)
        print(f"Created directory: {transcript_path}")

    # Load the Whisper model. Using "base" is a good balance.
    print("Loading Whisper model (this may take a moment)...")
    model = whisper.load_model("base")
    print("Whisper model loaded.")

    try:
        audio_files = [f for f in os.listdir(audio_path) if f.endswith(('.mp3', '.mp4', '.m4a'))]
        if not audio_files:
            print(f"No audio files found in '{audio_path}'. Please check the directory.")
            return
    except FileNotFoundError:
        print(f"Error: The directory '{audio_path}' was not found.")
        return

    print(f"\nFound {len(audio_files)} audio files to transcribe.")

    for filename in audio_files:
        audio_file_path = os.path.join(audio_path, filename)
        print(f"-> Transcribing: {filename}...")

        try:
            # Perform the transcription
            result = model.transcribe(audio_file_path, verbose=False)

            # Define the output filename
            transcript_filename = os.path.splitext(filename)[0] + ".json"
            transcript_file_path = os.path.join(transcript_path, transcript_filename)

            # Save the detailed transcript as a JSON file
            with open(transcript_file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            print(f"   Done. Transcript saved to {transcript_file_path}")

        except Exception as e:
            print(f"   An error occurred while transcribing {filename}: {e}")

    print("\n--- Transcription process complete! ---")