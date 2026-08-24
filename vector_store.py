import os
import hashlib
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


DOCUMENT_FOLDER = "documents"
VECTOR_DB_PATH =   "db/chroma_db"


# Load environment variables
load_dotenv()

# Azure Embedding Model
# embeddings = AzureOpenAIEmbeddings(
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT"),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
# )

# 1 Embedding Model

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("embedding model",embeddings)
#------------------------------
# 2 . ChromaDb
#---------------------------

vector_db = Chroma(
    persist_directory=VECTOR_DB_PATH,
    embedding_function=embeddings
)

print("vector db",vector_db)
#---------------------------------
#3 . TEXT Splitter
#-------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 250,
    chunk_overlap =50
)

print("text splitter",text_splitter)
#--------------------------
# 4. Generate file hash
#Create a unique fingerprint of a file so we can detect whether the file has changed.
# while chunk := f.read(8192): — the walrus operator := assigns the result of f.read(8192) to chunk and also evaluates it in the while condition. If f.read returns an empty bytes object (b'') at EOF (which is falsy), the loop stops.
# #-------------------------
def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


#------------------------------
#5. Check whether document already exists
#----------------------------

def get_existing_document_hash(file_path):
    try:

        result = vector_db.get(
            where = {
                "source":file_path
            }
        )
        metadatas = result.get("metadatas",[])

        if not metadatas:
            return None

        #All chunks of the same document have
        #the same file hash
        return metadatas[0].get("file_hash")

    except Exception:

        return None


#------------------------------
#6. index one document
#------------------------------

def index_document(file_path):
    print(f"\n checking : {file_path}")
    current_hash = calculate_file_hash(file_path)
    print(f"Current file hash: {current_hash}")
    existing_hash = get_existing_document_hash(file_path)
    print(f"Existing file hash: {existing_hash}")

    #------------------
    #Document has not changed
    #---------------------
    if existing_hash == current_hash:
        print("Document unchanged.")
        print("Skipping embedding/indexing.")

        return 

    #------------------
    #New Document
    #---------------
    if existing_hash is None:

        print("New Document found.")
        print("Creating emeddings..")

    #-------------------
    # Exsiting document changed
    #---------------------

    else:
        print("Document changed. ")
        print("Deleting old vectors...")

        vector_db.delete(
            where = {
                "source": file_path
            }
        )
        print("Creating new embeddings...")
        #--------------------
        #Load Document
        #-------------------

    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")

    print("loading document from file", file_path)
    print("loader", loader)
    documents = loader.load()
    print("loaded documents", documents)

    #-------------------
    #split document into chunks
    #-------------------
    
    chunks = text_splitter.split_documents(documents)
    print(f"chunks value: {chunks}")
    print(f"Document split into {len(chunks)} chunks.")

    #--------------------
    #add metadata
    #-------------------
    
    department = get_department(file_path)

    for chunk in chunks:

        chunk.metadata["source"] = file_path

        chunk.metadata["file_hash"] = current_hash
        chunk.metadata["department"] = department

        #---------------
        # Add to ChromaDB
        #----------------

        vector_db.add_documents(chunks)
        print(
            f"Indexed {len(chunks)} chunk successfully."
        )



#--------------------------
#7. Detect deleted documents
#---------------------------

def remove_deleted_documents():
    print("\n checking deleted documents...")
    result = vector_db.get()
    metadatas = result.get("metadatas",[])
    sources = set()

    for metadata in metadatas:
        if metadata and "source" in metadata:
            sources.add(metadata["source"])

    for source in sources:
        if not os.path.exists(source):

            print(
                f"Document deleted : {source}"
            )

            vector_db.delete(
                where = {
                    "source" : source
                }
            )

#-------------------------
#8 . Index all document
#-----------------------

def index_documents():
    os.makedirs(
        DOCUMENT_FOLDER,
        exist_ok=True
    )
    print("\n checking documents in folder:", DOCUMENT_FOLDER)
    print("\n checking documents in folder:", os.listdir(DOCUMENT_FOLDER))
    

    print("\n starting incremental indexing...")

    for filename in os.listdir(DOCUMENT_FOLDER):

        file_path = os.path.join(
            DOCUMENT_FOLDER,
            filename
        )
        print(f"\n checking file: {file_path}")
        if os.path.isfile(file_path):
            index_document(file_path)
            
    remove_deleted_documents()

    print("\n Incremental indexing compelted")


def get_department(file_path):

    filename = os.path.basename(file_path).lower()

    if filename == "hr.pdf":
        return "HR"

    if filename == "finance.pdf":
        return "Finance"

    if filename == "salary.pdf":
        return "Salary"

    if filename == "legal.pdf":
        return "Legal"

    return "Unknown"

#index_document("documents/legal.txt")
# get_department("documents/legal.txt")
# index_document("documents/hr.txt")
# get_department("documents/hr.txt")
# print("calling index_docuemnts() folder")
#index_documents()
# Create documents with metadata 
# Previous one when not using large docs

# documents = [

#     Document(
#         page_content="Employees get 20 annual leaves.",
#         metadata={"department": "HR"}
#     ),

#     Document(
#         page_content="Work from home is allowed twice a week.",
#         metadata={"department": "HR"}
#     ),

#     Document(
#         page_content="Salary policy for Finance department.",
#         metadata={"department": "Finance"}
#     ),

#     Document(
#         page_content="Annual budget report.",
#         metadata={"department": "Finance"}
#     ),

#     Document(
#         page_content="Contract policy.",
#         metadata={"department": "Legal"}
#     ),

# ]

# # Create Chroma Vector DB
# db = Chroma.from_documents(
#     documents=documents,
#     embedding=embeddings,
#     persist_directory="./db"
# )

# print("✅ Vector Database Created Successfully!")

# print("retrieving data from vector database")
# collection = db.get(
#     include=["metadatas", "documents","embeddings"]
# )
# print("Metadata______")
# print(collection["metadatas"])
# print("Documents______")
# print(collection["documents"])
# print("Embeddings______")
# print(collection["embeddings"])
#print("Metadata, Documents, Embeddings from vector database")
#print(collection)

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