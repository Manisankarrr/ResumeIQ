import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model directly locally at module level (downloads once lazily into ~/.cache (~80MB))
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embeds raw string variables precisely utilizing purely local compute resources with SentenceTransformers.
    """
    if not texts:
        return []
        
    # Generating purely nested lists converting our vectors locally.
    embeddings = _model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

def build_faiss_index(embeddings: list[list[float]]) -> faiss.IndexFlatIP:
    """
    Converts embedding lists to fp32 arrays, spins up an optimal Inner Product faiss index natively.
    all-MiniLM-L6-v2 dimensionality defaults rigidly strictly exactly to 384 dimensions.
    """
    if not embeddings:
        return faiss.IndexFlatIP(384)
        
    vectors = np.array(embeddings, dtype=np.float32)
    
    dimension = 384
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)
    
    return index

def search_index(index: faiss.IndexFlatIP, query_embedding: list[float], k: int) -> list[tuple[int, float]]:
    """
    Casts your vector 1D queries explicitly to proper 1x384 dimensional matrix structures avoiding numpy errors,
    searches FAISS structures returning precisely strictly mapped index positional tuples (idx, score).
    """
    if index.ntotal == 0 or not query_embedding:
        return []
        
    query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, 384)
    
    # Executing deep IP dot product tracking matches
    scores, indices = index.search(query_vector, k)
    
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx != -1:
            results.append((int(idx), float(score)))
            
    results.sort(key=lambda x: x[1], reverse=True)
            
    return results
