#  YouTube Playlist Chatbot

This is a powerful AI-powered chatbot that allows you to have a conversation with the content of any YouTube playlist. The application processes all videos in a given playlist, transcribes the audio, and uses a Retrieval-Augmented Generation (RAG) model to answer your questions based on the video content.

![Application Screenshot]<img width="1919" height="1011" alt="image" src="https://github.com/user-attachments/assets/949da485-b060-4b3f-a3ab-f1f81868d2c8" />


##  Features

* **Process Any Playlist**: Simply provide a YouTube playlist URL to build a knowledge base.
* **AI-Powered Chat**: Ask questions in natural language and get answers synthesized from the video content.
* **Source Citing**: The chatbot provides the source video and timestamp for the information it uses to answer your questions.
* **Real-time Status Updates**: The user interface provides live updates during the multi-step backend processing (Downloading, Transcribing, Storing).

##  Tech Stack

* **Backend**: FastAPI
* **Frontend**: HTML, CSS, JavaScript
* **AI Models**:
    * **Transcription**: `openai-whisper`
    * **Embeddings & Q&A**: `google-generativeai` (Gemini)
* **Vector Database**: ChromaDB
* **YouTube Downloader**: `yt-dlp`

##  How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API key:**
    * Create a file named `.env` in the root directory.
    * Add your Google AI API key to it:
        ```
        GOOGLE_API_KEY="YOUR_API_KEY_HERE"
        ```

5.  **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```
    The application will be available at `http://127.0.0.1:8000`.
