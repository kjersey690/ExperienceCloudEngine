import os
import hashlib
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from baseline_data import EXP_CLOUD_ERRORS

load_dotenv()

def get_unique_id(text):
    """Creates a unique MD5 hash for a string."""
    return hashlib.md5(text.strip().lower().encode()).hexdigest()

def recovery_run():
    # 1. Init
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "experience-cloud-errors"
    index = pc.Index(index_name)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 2. THE NUCLEAR OPTION: Clear existing data
    print(f"🧹 Clearing all existing vectors from {index_name}...")
    index.delete(delete_all=True)

    # 3. Seed with Unique Logic
    print("🌱 Re-seeding with unique ID protection...")
    upsert_data = []
    
    # We use a dictionary to pre-filter duplicates in the list itself
    unique_items = {}
    for item in EXP_CLOUD_ERRORS:
        # Key by the resolution to ensure we only have one of each fix
        res_key = item['resolution'].strip().lower()
        if res_key not in unique_items:
            unique_items[res_key] = item

    for res_text, item in unique_items.items():
        vector = model.encode(item['error']).tolist()
        # The ID is now a hash of the resolution
        uid = get_unique_id(res_text) 
        
        metadata = {
            "resolution": item['resolution'],
            "category": item['category'],
            "original_error": item['error']
        }
        
        upsert_data.append((uid, vector, metadata))

    # 4. Push to Pinecone
    index.upsert(vectors=upsert_data)
    print(f"✅ Recovery Complete. {len(upsert_data)} unique resolutions indexed.")

if __name__ == "__main__":
    recovery_run()