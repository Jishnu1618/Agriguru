import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.embedding_utils import embed_questions, build_faiss_index, search

# Your API key and URL (replace RESOURCE_ID with actual ID)
API_KEY = "579b464db66ec23bdd000001fc9a03836ef4fc46e756e42046b7710f83"
RESOURCE_ID = "cef25fe2-9231-4128-8aec-2c948fedd43f"  # ← Put correct resource ID here
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json&limit=1000"

def fetch_transcript_data():
    response = requests.get(API_URL)
    data = response.json()
    
    # Extract Q&A based on CSV field names
    qna_pairs = [(item["QueryText"], item["KccAns"]) for item in data["records"] if "QueryText" in item and "KccAns" in item]
    return qna_pairs

# Preprocess and build index
qna_data = fetch_transcript_data()
questions = [q for q, a in qna_data]
answers = [a for q, a in qna_data]

question_vectors = embed_questions(questions)
faiss_index = build_faiss_index(question_vectors)

def get_top_answers(query, k=3):
    results = search(query, questions, faiss_index, k)
    return [{"question": questions[i], "answer": answers[i]} for _, i in results]
def chat_interface():
    while True:
        query = input("Ask a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        results = get_top_answers(query)
        print("\nTop Answers:")
        for i, res in enumerate(results, 1):
            print(f"{i}. Q: {res['question']}")
            print(f"   A: {res['answer']}\n")


