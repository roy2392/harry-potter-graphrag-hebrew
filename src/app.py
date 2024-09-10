from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from graphrag.index.run import run_pipeline  # Import GraphRAG pipeline

app = FastAPI()

# Define request body schema
class QueryRequest(BaseModel):
    text: str

@app.post("/query")
async def query_model(request: QueryRequest):
    # Assuming your GraphRAG pipeline is already defined and ready to be called
    try:
        result = await run_pipeline(input_data=request.text)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "GraphRAG model is running!"}