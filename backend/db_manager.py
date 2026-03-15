import os
from supabase import create_client, Client
from pinecone import Pinecone
from dotenv import load_dotenv


load_dotenv()

class DatabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    def update_vote(self, entry_id, change):
        """Updates Supabase via RPC and patches Pinecone metadata."""
        try:
            # 1. Update Supabase via RPC
            self.supabase.rpc('increment_vote', {
                'row_id': entry_id, 
                'increment_by': change
            }).execute()
            
            # 2. Fetch the fresh count - Removed .single() to prevent PGRST116
            res = self.supabase.table("deployment_errors_queue") \
                .select("votes") \
                .eq("id", entry_id) \
                .execute()
            
            # 3. Check if we actually got data back
            if res.data and len(res.data) > 0:
                new_count = int(res.data[0].get('votes', 0))
                
                # 4. Partial Metadata Update in Pinecone
                self.index.update(id=str(entry_id), set_metadata={"votes": new_count})
                return True
            else:
                print(f"⚠️ Warning: Row {entry_id} not found in Supabase after update.")
                return False

        except Exception as e:
            print(f"Detailed Voting Error: {e}")
            return False

    def submit_error(self, name, replication, resolution, category):
        """Inserts a new error submission into the Supabase queue."""
        try:
            data = {
                "error_name": name,
                "replication_steps": replication,
                "resolution_steps": resolution,
                "category": category,
                "status": "Pending Review",
                "votes": 0  # Initialize new entries with 0 votes
            }
            self.supabase.table("deployment_errors_queue").insert(data).execute()
            return True
        except Exception as e:
            print(f"Error submitting to Supabase: {e}")
            return False