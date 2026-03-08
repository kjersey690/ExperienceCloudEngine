import os
import hashlib
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from baseline_data import EXP_CLOUD_ERRORS

load_dotenv()

def recovery_run():
    print("🔍 Initializing Recovery...")
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "experience-cloud-errors"
    index = pc.Index(index_name)
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 1. Check Connection
    print(f"📡 Checking index: {index_name}...")
    stats = index.describe_index_stats()
    print(f"Current count before start: {stats['total_vector_count']}")

    # 2. Process Data
    upsert_data = []
    unique_items = {item['resolution'].strip().lower(): item for item in EXP_CLOUD_ERRORS}

    for res_text, item in unique_items.items():
        vector = model.encode(item['error']).tolist()
        uid = hashlib.md5(res_text.encode()).hexdigest()
        metadata = {
            "resolution": item['resolution'],
            "category": item['category'],
            "original_error": item['error']
        }
        upsert_data.append((uid, vector, metadata))

    # 3. Explicit Upsert
    if upsert_data:
        print(f"📤 Attempting to upload {len(upsert_data)} vectors...")
        # We wrap this in a try/except to catch network errors
        try:
            res = index.upsert(vectors=upsert_data)
            print(f"🛰️ Pinecone Response: {res}")
        except Exception as e:
            print(f"❌ UPLOAD FAILED: {e}")
            return

    # 4. Wait for Consistency (Serverless indices can take a few seconds to update stats)
    print("⏳ Waiting 5 seconds for index to refresh...")
    time.sleep(5)
    
    new_stats = index.describe_index_stats()
    print(f"📊 New Vector Count: {new_stats['total_vector_count']}")

if __name__ == "__main__":
    recovery_run()