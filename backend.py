import os
import logging
import sys

import json
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = "us-east-1"

app = FastAPI()

# Load column mapping
with open("column_mapping.json", "r") as f:
    column_mapping = json.load(f)

# Initialize Pinecone
pc = Pinecone(
    api_key=PINECONE_API_KEY
)

# Initialize embedding model
embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Initialize LLM
llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo")

# Function to create documents from Excel
def create_documents_from_excel(file_path: str):
    df = pd.read_excel(file_path, sheet_name="Intake")
    df = df.fillna("This value is not available in the intake form")
    documents = []

    for _, row in df.iterrows():
        content_lines = []
        metadata = {}

        for col, val in row.items():
            label = column_mapping.get(col, col)
            value = str(val).strip() or "This value is not available in the intake form"
            content_lines.append(f"{label}: {value}")
            metadata[col] = value

        full_text = "\n".join(content_lines)
        documents.append(Document(page_content=full_text, metadata=metadata))

    return documents

# Initialize vector store and QA chain
retriever = None
qa_chain = None

@app.on_event("startup")
async def index_and_initialize():
    global retriever, qa_chain

    file_path = "source_excel.xlsx"  # Replace with your actual Excel file path
    index_name = os.getenv("PINECONE_INDEX")

    # Check if the index exists; if not, create it
    if index_name not in [index.name for index in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=1536,  # Make sure this matches your embedding model
            metric='cosine',
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Create documents from Excel
    doc_chunks = create_documents_from_excel(file_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(doc_chunks)

    # Initialize Pinecone vector store in manageable batches
    batch_size = 100  # Adjust this number based on your needs
    for i in range(0, len(split_docs), batch_size):
        batch = split_docs[i:i + batch_size]
        vectorstore = PineconeVectorStore.from_documents(
            documents=batch,
            embedding=embedding_model,
            index_name=index_name
        )

    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    print("✅ Indexing and QA chain setup complete.")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Backend is up and running."}

# Query endpoint
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def ask_question(request: QueryRequest):
    global qa_chain
    response = qa_chain.run(request.query)
    return {"response": response}
# Create a logger
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# Create a stream handler to output logs to the console
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)