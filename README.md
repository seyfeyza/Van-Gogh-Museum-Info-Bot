# Van Gogh Museum AI Assistant

An AI-powered assistant designed to answer questions about the **Van Gogh Museum**. This project demonstrates a **Retrieval-Augmented Generation (RAG)** workflow using a hybrid architecture of **Python** (for vector storage/search) and **n8n** (for agentic reasoning).

This system was built as part of the AI Intern Home Assignment to demonstrate the usage of Vector Databases, Embeddings, and AI Agents.

## Table of Contents

- [Van Gogh Museum AI Assistant](#van-gogh-museum-ai-assistant)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Prerequisites](#prerequisites)
  - [Installation \& Setup](#installation--setup)
    - [1. Backend Setup (Python)](#1-backend-setup-python)
    - [2. Frontend Setup (n8n)](#2-frontend-setup-n8n)
    - [How to Run](#how-to-run)
  - [Usage](#usage)
  - [Project Structure](#project-structure)

## Overview

This project is an AI-powered Info Bot specialized for the Van Gogh Museum. By leveraging a Retrieval-Augmented Generation (RAG) architecture, it combines a Python-based Vector Search engine (FastAPI + ChromaDB) with an intelligent Orchestrator (n8n + Gemini).

Unlike standard LLMs that might invent facts, this system grounds every response in a curated dataset of museum operations, artworks, and history. It shows how to effectively bridge a local Vector Database with a Low-Code AI Agent to create accurate, context-aware user experiences.

## Architecture

The system follows a modular microservice architecture:

1.  **Knowledge Base (Python/FastAPI):**
    * **Data Source:** A JSON dataset containing 32 facts about artworks, tickets, and museum rules.
    * **Vector DB:** Uses **ChromaDB** to store embeddings locally.
    * **Embeddings:** Uses **Google Gemini (`models/text-embedding-004`)** for semantic search.
    * **API:** Exposes a `/search` endpoint via **FastAPI** to retrieve relevant context.

2.  **AI Agent (n8n):**
    * **Orchestrator:** Handles the user conversation flow.
    * **Reasoning:** Uses **Google Gemini (`gemini-2.5-flash`)** as the LLM.
    * **Tool Use:** The agent autonomously decides when to call the Python API tool based on the user's query.

## Prerequisites

Before you begin, ensure you have met the following requirements:

* **Python 3.10+** installed on your machine.
* **n8n** installed (Desktop App or via npm/npx).
* A valid **Google Gemini API Key**.

## Installation & Setup

### 1. Backend Setup (Python)

Navigate to the project directory and set up the Python environment:

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
    ```
2. **Activate the virtual environment:**
    - On Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```
3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure API Key:**

    Create a `.env` file in the project root with the following content:
   
     ```bash
     GOOGLE_API_KEY=your_gemini_api_key_here
     ```
### 2. Frontend Setup (n8n)
 1. Open n8n (Desktop app or via browser at http://localhost:5678).

 2. Import the provided workflow.json file (if available in the repo).

 3. Configure the Google Gemini Chat Model node credentials with your API key.

 4. Ensure the HTTP Request Tool node is pointing to: http://localhost:8000/search
### How to Run
1. Start the Python Knowledge Server
Open a terminal in the project root and run the following command. This starts the API and generates the vector database if it doesn't exist.

    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
Wait until you see the message: Application startup complete.

2. Start the n8n Agent
Open your n8n workflow editor.

    Click the "Chat" button at the bottom of the editor.

    Start asking questions!

## Usage

Here is an example of the internal data flow when a user asks a question:

**1. User Input (Chat):**
> "How much are the tickets?"

**2. Internal Process (JSON Request):**
The AI Agent analyzes the intent and calls the Python API with this payload:
```json
{
  "query": "ticket prices",
  "top_k": 3
}
```
**3.Internal Response (from Python API):**
 The Python API queries ChromaDB and returns the most relevant chunks:
```json
{
  "results": [
    {
      "content": "Category: Tickets\nInfo: Tickets for the Van Gogh Museum are only available online...",
      "similarity_score": 0.3421
    },
    {
      "content": "Category: Visitor Info\nInfo: The museum is open daily...",
      "similarity_score": 0.4102
    }
  ]
}
```
**4. Final Output (Chat Response):**
Tickets for the Van Gogh Museum are only available online, and you must book a time slot in advance. The museum does not sell tickets at the door.

## Project Structure
```
.
├── main.py              # FastAPI server & Vector DB Logic
├── van_gogh_data.json   # Knowledge Base Dataset
├── requirements.txt     # Python dependencies
├── .env                 # API Keys (Not included in repo)
├── chroma_db/           # Local Vector Database storage
└── README.md            # Project Documentation
```