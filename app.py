from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer

from auth import verify_token
from rag import retrieve

from langchain_openai import AzureChatOpenAI

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

security = HTTPBearer()

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("CHAT_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0
)

@app.post("/chat")
def chat(question:str, credentials = Depends(security)):

    token = credentials.credentials
    user = verify_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    docs = retrieve(question, user)

    if not docs:
        return {"answer": "No relevant documents found."}

    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"Answer the question based on the following context:\n\n{context}\n\nQuestion: {question}\nAnswer:"

    #response = llm.generate([prompt])
    response = llm.invoke(prompt)

    return {
        "user": user["username"],
        "department" : user["department"],
        "answer": response.content
    }

    answer = response.generations[0][0].text

    return {"answer": answer}