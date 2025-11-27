import json
import os
import time
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# Google API Key check
if "GOOGLE_API_KEY" not in os.environ:
    print("ERROR: GOOGLE_API_KEY not found in .env file")

app = FastAPI(title="Van Gogh Museum Knowledge API (Gemini Powered)")

# CONFIGURATION
DATA_FILE = "van_gogh_data.json"
VECTOR_DB_PATH = "./chroma_db"
COLLECTION_NAME = "van_gogh_collection"

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Initialize Vector Store (ChromaDB - Local)
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=VECTOR_DB_PATH
)

# HELPER FUNCTIONS

def load_data():
    """Reads the JSON file and prepares Documents for the vector store."""
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return []
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = []
    for item in data:
        page_content = f"Category: {item['category']}\nInfo: {item['content']}"
        metadata = {"id": item["id"], "category": item["category"]}
        doc = Document(page_content=page_content, metadata=metadata)
        documents.append(doc)
    
    return documents

def initialize_db():
    """Loads data into Vector DB carefully to avoid Rate Limits."""
    existing_docs = vector_store.get()
    
    if len(existing_docs['ids']) == 0:
        print("Vector DB is empty. Starting batch data ingestion (Rate Limit Safe)...")
        docs = load_data()
        
        if docs:
            # BATCH PROCESSING
            batch_size = 5 
            total_docs = len(docs)
            
            for i in range(0, total_docs, batch_size):
                batch = docs[i : i + batch_size]
                try:
                    print(f"Processing batch: {i} to {i+batch_size}...")
                    vector_store.add_documents(documents=batch)
                    
                    # Pause to avoid '429 Resource Exhausted' errors
                    if i + batch_size < total_docs: 
                        print("Pausing for API Rate Limit (10 seconds)...")
                        time.sleep(10)
                        
                except Exception as e:
                    print(f"ERROR (Batch {i}): {e}")
                    print("Waiting 5 seconds before retrying...")
                    time.sleep(5)

            print(f"Success! Total {total_docs} records loaded into Vector DB.")
        else:
            print("No data found to add.")
    else:
        print("Vector DB already contains data. Skipping initialization.")


# Run initialization on startup
initialize_db()

# --- API ENDPOINTS ---

class SearchRequest(BaseModel):
    query: str
    top_k: int = 3

@app.get("/")
def home():
    return {"message": "Van Gogh Museum AI API is running"}

@app.post("/search")
def search_knowledge(request: SearchRequest):
    """
    Endpoint used by the AI Agent.
    Performs semantic search in the Vector DB and returns relevant chunks.
    """
    try:
        print(f"Searching for: {request.query}")
        results = vector_store.similarity_search_with_score(request.query, k=request.top_k)
        
        response_data = []
        for doc, score in results:
            response_data.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": round(score, 4) 
            })
            
        return {"results": response_data}

    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))