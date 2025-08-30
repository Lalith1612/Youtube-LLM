# step2_download_audio.py
import os
import subprocess
from pytube import Playlist

def download_audio_from_playlist(playlist_url: str, save_path: str):
    """
    Downloads audio from all videos in a YouTube playlist using yt-dlp.
    This is much more reliable than using pytube's downloader.

    Args:
        playlist_url: The URL of the YouTube playlist.
        save_path: The folder where audio files will be saved.
    """
    # Create the save directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print(f"Created directory: {save_path}")

    try:
        playlist = Playlist(playlist_url)
        print(f"Fetching playlist: '{playlist.title}'")
        print(f"Found {len(playlist.video_urls)} videos in the playlist.")
    except Exception as e:
        print(f"Could not fetch playlist details with pytube. Error: {e}")
        print("This might be a network issue or the playlist is private.")
        return

    for video_url in playlist.video_urls:
        print(f"-> Starting download for: {video_url}")
        try:
            # Construct the yt-dlp command
            command = [
                'yt-dlp',
                '--extract-audio',          # Extract audio
                '--audio-format', 'mp3',    # Convert to mp3
                # Save in the specific playlist's audio folder
                '--output', os.path.join(save_path, '%(title)s.%(ext)s'),
                '--quiet',                  # Suppress console output for cleaner logs
                video_url
            ]
            
            # Execute the command
            subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"   Successfully downloaded audio for {video_url}")

        except subprocess.CalledProcessError as e:
            # This error means yt-dlp returned a non-zero exit code (i.e., an error)
            print(f"   ERROR downloading {video_url}. yt-dlp failed.")
            print(f"   Error details: {e.stderr}") # Print the error output from yt-dlp
        except Exception as e:
            print(f"   An unexpected error occurred with video {video_url}: {e}")

    print("\n--- Audio download process complete! ---")