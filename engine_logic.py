import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

class ResolutionEngine:
    def __init__(self, api_key: str, index_name: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        # Standardize on this model for 384 dimensions
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query_text):
        query_vector = self.model.encode(query_text).tolist()
        
        raw_results = self.index.query(
            vector=query_vector, 
            top_k=15, 
            include_metadata=True
        )

        unique_results = []
        seen_resolutions = set()

        for match in raw_results['matches']:
            res_text = match['metadata'].get('resolution', "").strip().lower()
            if res_text not in seen_resolutions:
                unique_results.append(match)
                seen_resolutions.add(res_text)
            
            if len(unique_results) == 5:
                break
                
        return unique_results