from retriever import query_chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import os 
from dotenv import load_dotenv

load_dotenv()

def Handle_query(query, revalent_docs):
    context = "\n\n".join([doc.page_content for doc in revalent_docs])
    promt = f""" based on the following document , please answer this  question {query} documents:
    {context}
    please provide a clear helpful answer using only the information from these documents . if you can't find the answer in
    documents . say "i don't have anough information based on the documentation please try other question
    """
    llm  = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        )
    messages = [
        SystemMessage(content = "You are  a helpful assistance"),
        HumanMessage(content = promt),
        ]
    result = llm.invoke(messages).content
    return result



query = "What time is check-in?"
result = query_chroma(
   query,
    "/Users/lait-zet/Desktop/Hotel-AI-assistant-RaG/backend/chroma_db"
)

finale_answer = Handle_query(query, result)

print(finale_answer)