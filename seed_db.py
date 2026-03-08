import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from baseline_data import EXP_CLOUD_ERRORS

# 1. Load Credentials
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 2. Initialize AI Model & Pinecone
# This model will generate the 384-dimension vectors
model = SentenceTransformer('all-MiniLM-L6-v2')
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("experience-cloud-errors")

def seed():
    print("🚀 Starting the seeding process...")
    processed_data = []

    for i, item in enumerate(EXP_CLOUD_ERRORS):
        # Generate the vector (embedding) for the error message
        vector = model.encode(item['error']).tolist()
        
        # Prepare the metadata (what we want to get back during a search)
        metadata = {
            "resolution": item['resolution'],
            "category": item['category'],
            "original_error": item['error']
        }
        
        # Pinecone format: (ID, Vector, Metadata)
        processed_data.append((f"baseline_{i}", vector, metadata))

    # 3. Upsert to Pinecone
    # Batching is good practice, even for 20 items
    index.upsert(vectors=processed_data)
    print(f"✅ Successfully seeded {len(processed_data)} errors into the engine!")

if __name__ == "__main__":
    seed()