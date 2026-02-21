import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

RAG_SYSTEM_PROMPT = """You are a precise document assistant. Answer the user's question using ONLY the retrieved document excerpts provided.

Rules:
- Answer concisely (2-4 sentences max)
- Quote specific numbers, dates, or terms directly from the documents when relevant
- If the documents don't contain enough information, say: "The uploaded documents don't contain specific information about that."
- Do NOT make up information or use outside knowledge
- Cite which document(s) your answer came from by name"""


class LLMService:
    MODEL = "llama-3.3-70b-versatile"  # Groq's best free model for RAG

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "")
        self.client = None
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            print(f"✓ Groq RAG generation ready ({self.MODEL})")
        else:
            print("⚠️  GROQ_API_KEY not set — RAG answers disabled, returning sources only")

    def generate_rag_answer(self, query: str, retrieved_docs: list) -> str:
        """
        RAG generation step: Groq/Llama reads retrieved document chunks
        and synthesizes a direct, grounded answer.
        """
        if not self.client or not retrieved_docs:
            return ""

        # Build context from retrieved chunks
        context_blocks = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_blocks.append(
                f"[{i}] {doc['file_name']} ({doc['document_type'].upper()}):\n\"{doc['content']}\""
            )
        context = "\n\n".join(context_blocks)

        try:
            completion = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Question: {query}\n\nRetrieved Documents:\n{context}"},
                ],
                temperature=0.1,   # Low temp for factual accuracy
                max_tokens=512,
            )
            answer = completion.choices[0].message.content.strip()
            print(f"🤖 RAG answer generated ({len(answer)} chars)")
            return answer

        except Exception as e:
            print(f"⚠️  Groq RAG generation failed: {e}")
            return ""


# Singleton — imported by main.py as gemini_service for backwards compat
gemini_service = LLMService()
