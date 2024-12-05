from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import json
import numpy as np

model = SentenceTransformer('model/')
verse_embeddings = np.load("data/verse_embeddings.npy")

app = Flask(__name__)
with open('data.json', 'r', encoding='utf-8') as file:
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

def search_verses(query: str, max_results: int) -> List[Dict]:
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

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()

    query = data.get('query')
    max_results = data.get('max_results', 5)  

    results = search_verses(query, max_results)

    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True)