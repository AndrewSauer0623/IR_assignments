import openai
from structures import Doc, Response
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

def answer_docs_with_llm(docs: List[Doc],
                         model_name: str = "gpt-4",
                         max_tokens: int = 500, query: str = "") -> List[Response]:
    responses: List[Response] = []

    client = openai.OpenAI()  # new client

    for doc in docs:
        prompt = (
            f"You are an expert biomedical assistant.\n"
            f"Answer this: {query} using ONLY the following document content.\n"
            f"Document ID: {doc.id}\n"
            f"Document Text:\n{doc.text}\n\n"
            f"Question: {doc.title}\n"
            f"Answer (use ONLY this document content, do NOT hallucinate):"
        )
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a biomedical literature assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0
            )
            llm_output = response.choices[0].message.content.strip()
            responses.append(Response(docid=doc.id, answer=llm_output))

        except Exception as e:
            responses.append(Response(docid=doc.id, answer=f"ERROR: {str(e)}"))

    return responses
