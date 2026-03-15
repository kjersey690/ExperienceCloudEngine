from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db_manager import DatabaseManager 
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

app = FastAPI()
db = DatabaseManager()
# Ensure this model matches the one used for your original 115 entries
model = SentenceTransformer('all-MiniLM-L6-v2')

# Allow React (Vite) to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContributionModel(BaseModel):
    name: str
    category: str
    resolution: str

class VoteModel(BaseModel):
    entry_id: str
    change: int

@app.get("/api/search")
async def search(q: str = Query(...)):
    xq = model.encode(q).tolist()
    
    result = db.index.query(
        vector=xq, 
        top_k=6, 
        include_metadata=True
        # filter={"status": {"$eq": "Approved"}}  # <--- COMMENT THIS OUT temporarily
    )
    
    formatted = []
    for match in result['matches']:
        meta = match.get('metadata', {})
        formatted.append({
            "id": match['id'],
            "score": match['score'],
            "metadata": {
                "error_name": meta.get('error_name', "Unknown Error"),
                "category": meta.get('category', "General"),
                # Check both resolution keys used in your db_manager and app.py
                "resolution": meta.get('resolution_steps', meta.get('resolution', "No steps provided."))
            },
            "votes": meta.get('votes', 0)
        })
    return formatted

@app.post("/api/vote")
async def vote(data: VoteModel):
    success = db.update_vote(data.entry_id, data.change)
    if not success:
        raise HTTPException(status_code=400, detail="Database update failed")
    return {"status": "success"}


# 2. Create the missing endpoint
@app.post("/api/contribute")
async def contribute(data: ContributionModel):
    try:
        # Match the signature from your app.py: (name, trace, res, cat)
        success = db.submit_error(
            data.name,         # Position 1: Name
            "",                # Position 2: Trace (Empty)
            data.resolution,   # Position 3: Resolution
            data.category      # Position 4: Category
        )
        
        if success:
            return {"status": "success"}
        raise HTTPException(status_code=500, detail="Database rejected entry")
    except Exception as e:
        print(f"CONTRIBUTION ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)