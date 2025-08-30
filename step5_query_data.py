# step5_query_data.py
import os
import chromadb
import google.generativeai as genai

def query_rag_model(query: str, db_path: str, n_results: int = 5):
    """
    Queries the ChromaDB to find relevant documents and then uses Google's
    generative model to answer the question based on the context.
    """
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not found.")
        genai.configure(api_key=api_key)
        
        db_client = chromadb.PersistentClient(path=db_path)
        collection = db_client.get_collection(name="youtube_transcripts_google")
    except Exception as e:
        return f"Error initializing clients: {e}", []

    try:
        query_embedding = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="RETRIEVAL_QUERY"
        )['embedding']

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
    except Exception as e:
        return f"Error querying the database: {e}", []
    
    if not documents:
        return "I could not find any relevant information in the playlist to answer your question.", []

    context = "\n---\n".join(documents)
    prompt = f"""
    You are a helpful assistant who answers questions based on the provided context from YouTube video transcripts.
    Answer the user's question based *only* on the information given in the context below.
    If the information is not in the context, say that you cannot find the answer in the provided videos.
    Do not make up information.

    CONTEXT:
    {context}

    QUESTION:
    {query}

    ANSWER:
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        answer = response.text
        
        sources = [f"{meta['source']} (at {int(meta['start_time'])}s)" for meta in metadatas]
        unique_sources = sorted(list(set(sources)))
        
        return answer, unique_sources
    except Exception as e:
        return f"Error generating answer from the model: {e}", []