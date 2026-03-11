import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def submit_error(self, name, replication, resolution, category):
        """Inserts a new error submission into the queue."""
        try:
            data = {
                "error_name": name,
                "replication_steps": replication,
                "resolution_steps": resolution,
                "category": category,
                "status": "Pending Review"
            }
            self.supabase.table("deployment_errors_queue").insert(data).execute()
            return True
        except Exception as e:
            print(f"Error submitting to Supabase: {e}")
            return False