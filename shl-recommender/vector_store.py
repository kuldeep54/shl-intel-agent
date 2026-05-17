import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

import os

def build_index(catalog_path="catalog.json", index_path="index.faiss"):
    with open(catalog_path) as f:
        catalog = json.load(f)

    if os.path.exists(index_path):
        print(f"Loading pre-computed FAISS index from {index_path}...")
        index = faiss.read_index(index_path)
        return index, catalog, np.array([])

    print("Pre-computed FAISS index not found. Building on the fly...")
    texts = [
        f"{item['name']} {item['description']} {item['test_type']}"
        for item in catalog
    ]

    if not texts:
        # Fallback for empty catalog, model dimension is 384
        return faiss.IndexFlatL2(384), catalog, np.array([])

    embeddings = model.encode(texts, convert_to_numpy=True)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Save the index for faster subsequent runs
    try:
        faiss.write_index(index, index_path)
        print(f"Cached FAISS index to {index_path}")
    except Exception as e:
        print(f"Failed to cache index: {e}")

    return index, catalog, embeddings

def search(query: str, index, catalog, top_k=10):
    query_vec = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(catalog):
            results.append(catalog[i])
    return results
