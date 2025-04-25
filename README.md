# AI_RAG_Excel
RAG implementation using excel, pinecone, langchain and openai

🤖 Pursuit Assistant
An AI-powered chatbot that leverages FastAPI and Streamlit to provide intelligent responses based on Excel data.​

✨ Features
FastAPI Backend: Handles API requests and integrates with LangChain for processing.
Streamlit Frontend: Provides an interactive chat interface for users.
Excel Data Integration: Processes and responds based on data from Excel files.

🚀 Getting Started
Prerequisites
Python 3.9 or higher

pip​

Installation
Clone the repository
Create a virtual environment:
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
Install dependencies:

pip install -r requirements.txt
Set environment variables:


uvicorn backend:app --reload
Access the API documentation at http://127.0.0.1:8000/docs.​

Running the Frontend (Streamlit)
streamlit run app.py
Open http://localhost:8501 in your browser to interact with the chatbot.​

📡 API Endpoints
POST /query
Description: Processes user queries and returns responses based on Excel data.

Request Body:​

json
Copy
Edit
  {
    "query": "Your question here"
  }
Response:​

json
Copy
Edit
  {
    "response": "Chatbot's answer based on Excel data."
  }
  
🗂 Project Structure
├── app.py                 # Streamlit frontend
├── backend.py             # FastAPI backend
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── source_excel.xlsx     # Excel file with one sheet
└── README.md              # Project documentation
