import os

from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings

load_dotenv()

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("EMBEDDING_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# Load existing vector database
db = Chroma(
    persist_directory="./db",
    embedding_function=embeddings
)

print("load data from data base",db.get())  # Print the collection to verify the database is loaded correctly


def retrieve(query, user):

    docs = db.similarity_search(
        query=query,
        k=3,
        filter={
            "department": user["department"]
        }
    )
    print("similar documents:", docs)
    return docs