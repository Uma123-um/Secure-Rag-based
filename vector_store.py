import os
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings

# Load environment variables
load_dotenv()

# Azure Embedding Model
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# Create documents with metadata
documents = [

    Document(
        page_content="Employees get 20 annual leaves.",
        metadata={"department": "HR"}
    ),

    Document(
        page_content="Work from home is allowed twice a week.",
        metadata={"department": "HR"}
    ),

    Document(
        page_content="Salary policy for Finance department.",
        metadata={"department": "Finance"}
    ),

    Document(
        page_content="Annual budget report.",
        metadata={"department": "Finance"}
    ),

    Document(
        page_content="Contract policy.",
        metadata={"department": "Legal"}
    ),

]

# Create Chroma Vector DB
db = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="./db"
)

print("✅ Vector Database Created Successfully!")

print("retrieving data from vector database")
collection = db.get()
print(collection)

# "What is happening here?
# Step 1
# load_dotenv()

# Loads the values from .env.

# Step 2
# AzureOpenAIEmbeddings(...)

# This connects to your Azure embedding model.

# Internally:

# Document
#       │
#       ▼
# Azure OpenAI
# (text-embedding-3-small)
#       │
#       ▼
# 1536 floating point numbers

# Example:

# [0.12,
# 0.83,
# -0.55,
# 0.31,
# ...
# 1536 values]

# This is called an embedding vector.

# Step 3
# Document(...)

# Each document contains:

# Text
# +
# Metadata

# Example:

# Employees get 20 annual leaves.

# Metadata

# department = HR
# Step 4
# Chroma.from_documents(...)

# This performs four things automatically:

# Document
#     │
# Split
#     │
# Embedding
#     │
# Store Vector
#     │
# Store Metadata

# Everything is saved into

# db/
# Run it

# Execute:

# python vector_store.py

# Expected output:

# ✅ Vector Database Created Successfully!
# You should now see
# secure-rag/

# db/

# documents/

# app.py

# auth.py

# rag.py

# vector_store.py

# Inside db/

# chroma.sqlite3

# along with some Chroma data files.

# Verify the vector database

# If you see something like:

# db/

# ├── chroma.sqlite3
# ├── ...

# then everything worked correctly.

# Interview explanation

# If the interviewer asks:

# "What happens when you run vector_store.py?"

# You can answer:

# "vector_store.py loads the documents, sends each document to the Azure OpenAI embedding model (text-embedding-3-small) to generate vector embeddings, stores those embeddings in ChromaDB, and saves metadata like the department. During retrieval, this metadata enables secure filtering so users only access documents they're authorized to see."d