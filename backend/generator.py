from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from backend.config import LLM_MODEL, GOOGLE_API_KEY

class HotelGenerator:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0,
        )

    def generate_answer(self, query: str, context_docs: list):
        """Generates an answer based on the provided documents."""
        if not context_docs:
            return {
                "answer": "I'm sorry, I don't have enough information to answer that question accurately. Could you please rephrase or ask about something else?",
                "sources": []
            }

        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""You are a professional hotel assistant. Answer the following question using ONLY the provided information. 
        If the answer is not in the documents, state that you don't have enough information.
        
        QUESTION: {query}
        
        DOCUMENTS:
        {context_text}
        
        Provide a polite, helpful, and concise answer.
        """

        messages = [
            SystemMessage(content="You are a polite and professional hotel concierge assistant."),
            HumanMessage(content=prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            answer = response.content
        except Exception as e:
            answer = f"I'm sorry, I encountered an error while processing your request: {str(e)}"

        # Extract unique sources
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in context_docs]))
        
        return {
            "answer": answer,
            "sources": sources
        }

# Singleton instance for the application
generator = None

def get_generator():
    global generator
    if generator is None:
        generator = HotelGenerator()
    return generator