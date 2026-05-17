import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def precompute():
    print("Loading SentenceTransformer model ('all-MiniLM-L6-v2')...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    catalog_path = "catalog.json"
    print(f"Reading catalog from '{catalog_path}'...")
    with open(catalog_path) as f:
        catalog = json.load(f)
        
    texts = [
        f"{item['name']} {item['description']} {item['test_type']}"
        for item in catalog
    ]
    
    print(f"Encoding {len(texts)} catalog items. This might take a moment on CPU...")
    embeddings = model.encode(texts, convert_to_numpy=True)
    
    print("Building FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    # Save the index to disk
    index_path = "index.faiss"
    faiss.write_index(index, index_path)
    print(f"Success! FAISS index saved to '{index_path}'.")

if __name__ == "__main__":
    precompute()
