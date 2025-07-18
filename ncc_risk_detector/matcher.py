from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def find_similarities(nccs, contract_segments, top_k=3, threshold=0.5):
    ncc_texts = [ncc["Title"] + ". " + ncc["Description"] + " " + ncc["Root Cause"] for ncc in nccs]
    ncc_embeddings = model.encode(ncc_texts, convert_to_tensor=True)
    contract_embeddings = model.encode(contract_segments, convert_to_tensor=True)

    similarity_matrix = cosine_similarity(contract_embeddings, ncc_embeddings)
    results = []

    for i, row in enumerate(similarity_matrix):
        top_indices = np.argsort(row)[::-1][:top_k]
        matches = []
        for idx in top_indices:
            score = row[idx]
            if score >= threshold:
                matches.append({
                    "ncc_id": nccs[idx]["ID"],
                    "ncc_title": nccs[idx]["Title"],
                    "similarity": float(score)
                })
        if matches:
            results.append({
                "contract_segment": contract_segments[i],
                "matches": matches
            })

    return results
