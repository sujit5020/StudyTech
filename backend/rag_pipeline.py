import os
import fitz
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def create_vector_store(text, chunk_size=500):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    embeddings = model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return chunks, index

def retrieve_relevant_chunks(question, chunks, index, top_k=3):
    question_embedding = model.encode([question])
    distances, indices = index.search(np.array(question_embedding), top_k)
    return [chunks[i] for i in indices[0]]

def answer_question_with_rag(file_path, question):
    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            return "No readable text found in the PDF."

        chunks, index = create_vector_store(text)
        relevant_chunks = retrieve_relevant_chunks(question, chunks, index)

        context = "\n\n".join(relevant_chunks)

        prompt = f"""Answer the following question using the provided context.\n
Context:
{context}

Question:
{question}

Answer:"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert tutor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error in RAG pipeline: {str(e)}"
