from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import json
import numpy as np

model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')



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


text_data = [verse["description1"] + " " + verse["description2"]  for verse in verses]

verse_embeddings = model.encode(text_data)

model.save_pretrained("model/")
np.save("data/verse_embeddings.npy",verse_embeddings)