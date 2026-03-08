import pinecone
from sentence_transformers import SentenceTransformer
from colorama import Fore, Style, init

# Initialize colorama for cross-platform terminal colors
init(autoreset=True)

class DeploymentErrorEngine:
    def __init__(self, api_key, index_name):
        self.pc = pinecone.Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_top_resolutions(self, error_message):
        # 1. Vectorize the user's input error
        query_vector = self.model.encode(error_message).tolist()

        # 2. Query Pinecone for top 5 matches
        results = self.index.query(
            vector=query_vector, 
            top_k=5, 
            include_metadata=True
        )
        return results['matches']

    def display_results(self, matches):
        print(f"\n{Style.BRIGHT}--- AI Deployment Resolution Engine ---")
        
        for i, match in enumerate(matches, 1):
            score = match['score']
            resolution = match['metadata']['resolution']
            
            # --- Color Coding Logic ---
            if score >= 0.80:
                color = Fore.GREEN
                status = "HIGH CONFIDENCE"
            elif 0.50 <= score < 0.80:
                color = Fore.YELLOW
                status = "MEDIUM CONFIDENCE"
            else:
                color = Fore.RED
                status = "LOW CONFIDENCE"

            # Print formatted output
            print(f"\n{color}{Style.BRIGHT}[{i}] {status} - Match Score: {score:.2%}")
            print(f"{Fore.WHITE}Suggested Fix: {resolution}")