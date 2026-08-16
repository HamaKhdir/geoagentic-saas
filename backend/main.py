from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db
from agent.graph import app_agent
from langchain_core.messages import HumanMessage

app = FastAPI(title="GeoAgentic SaaS Engine")

# 1. Enable CORS Middleware for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits requests from React Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_db():
    init_db()

class ChatQuery(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(query: ChatQuery):
    inputs = {"messages": [HumanMessage(content=query.message)]}
    result = app_agent.invoke(inputs)
    
    last_message = result["messages"][-1].content
    geojson = result.get("geojson_data", {})
    
    return {
        "response": last_message,
        "is_geo_query": result.get("location_found", False),
        "geojson": geojson
    }

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "GeoAgentic Engine"}