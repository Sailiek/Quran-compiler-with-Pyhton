from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np

app = Flask(__name__)

model = SentenceTransformer('model/')
verse_embeddings = np.load("data/verse_embeddings.npy")
with open('quran_ar_eng.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
verses = []

for chapter in data:
    for verse in chapter["verses"]:
        verse_data = {
            "chapter": chapter["id"],
            "verse": verse["id"],
            "arabic_text": verse["text"],
            "english_text": verse["translation"],
            "description1": verse["tafsir"],
            "description2": verse["tafsirV2"]
        }
        verses.append(verse_data)

def search_verses(query: str, max_results: int = 5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, verse_embeddings)
    ranked_indices = similarities.argsort()[0][::-1][:max_results]
    results = []
    for idx in ranked_indices:
        verse = verses[idx]
        results.append({
            "chapter": verse["chapter"],
            "verse": verse["verse"],
            "arabic_text": verse["arabic_text"],
            "english_text": verse["english_text"],
            "description1": verse["description1"],
            "description2": verse["description2"],
            "similarity_score": float(similarities[0][idx])
        })
    return results

def get_description(query):
    for verse in verses:
        if verse["english_text"].strip().lower() == query.strip().lower():
            return verse["description1"]
    return None

@app.route("/analyze_verse", methods=["POST"])
def analyze_verse():
    data = request.json
    query = data.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    description = get_description(query)
    if not description:
        return jsonify({"results": []}), 200

    similar_verses = search_verses(description, max_results=4)
    return jsonify({"results": similar_verses})

if __name__ == "__main__":
    app.run(debug=True)
