from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
from utils import process_context_data, serialize_search_result
from settings import load_settings_from_yaml
from global_search import setup_global_search
from local_search import setup_local_search

_ = load_dotenv()
settings = load_settings_from_yaml("settings.yml")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://noworneverev.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

global_search_engine = setup_global_search()
local_search_engine = setup_local_search()

@app.get("/search/global")
async def global_search(query: str = Query(..., description="Search query for global context")):
    try:
        result = await global_search_engine.asearch(query)
        logging.info(f"Raw global search result: {result}")
        if isinstance(result.response, dict):
            response_content = result.response.get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            response_content = str(result.response)
        response_dict = {
            "response": response_content,
            "context_data": process_context_data(result.context_data),
            "context_text": result.context_text,
            "completion_time": result.completion_time,
            "llm_calls": result.llm_calls,
            "prompt_tokens": result.prompt_tokens,
            "reduce_context_data": process_context_data(result.reduce_context_data),
            "reduce_context_text": result.reduce_context_text,
            "map_responses": [serialize_search_result(r) for r in result.map_responses],
        }
        return JSONResponse(content=response_dict)
    except Exception as e:
        logging.error(f"Error in global search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search/local")
async def local_search(query: str = Query(..., description="Search query for local context")):
    try:
        result = await local_search_engine.asearch(query)
        if isinstance(result.response, dict):
            response_content = result.response.get('choices', [{}])[0].get('message', {}).get('content', '')
        else:
            response_content = str(result.response)
        response_content = translate_to_hebrew(response_content)
        response_dict = {
            "response": response_content,
            "context_data": process_context_data(result.context_data),
            "context_text": result.context_text,
            "completion_time": result.completion_time,
            "llm_calls": result.llm_calls,
            "prompt_tokens": result.prompt_tokens,
        }
        return JSONResponse(content=response_dict)
    except Exception as e:
        logging.error(f"Error in local search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def status():
    return JSONResponse(content={"status": "Server is up and running"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)