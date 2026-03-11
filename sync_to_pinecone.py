import os
import hashlib
from supabase import create_client
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Initialize Clients
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("experience-cloud-errors")
model = SentenceTransformer('all-MiniLM-L6-v2')

def promote_approved_entries():
    # 1. Fetch only Approved and Unsynced entries
    response = supabase.table("deployment_errors_queue") \
        .select("*") \
        .eq("status", "Approved") \
        .eq("is_synced", False) \
        .execute()

    entries = response.data

    if not entries:
        print("☕ No new approved entries to promote.")
        return

    print(f"🚀 Promoting {len(entries)} entries to Pinecone...")

    for entry in entries:
        # 2. Prepare Data
        res_text = entry['resolution_steps']
        vector = model.encode(entry['error_name']).tolist()
        
        # Use our MD5 Hashing logic to prevent duplicates
        uid = hashlib.md5(res_text.strip().lower().encode()).hexdigest()
        
        metadata = {
            "resolution": res_text,
            "category": entry['category'],
            "original_error": entry['error_name']
        }

        # 3. Upsert to Pinecone
        index.upsert(vectors=[(uid, vector, metadata)])

        # 4. Mark as Synced in Supabase so we don't do it again
        supabase.table("deployment_errors_queue") \
            .update({"is_synced": True}) \
            .eq("id", entry['id']) \
            .execute()

    print("✅ Promotion complete. AI Engine is now updated with team-vetted data.")

if __name__ == "__main__":
    promote_approved_entries()
