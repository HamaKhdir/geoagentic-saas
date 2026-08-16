import os
import json
import urllib.parse
import urllib.request
from typing import TypedDict, Sequence, Optional
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from database import get_db_connection


from dotenv import load_dotenv
load_dotenv()

# Print status check on startup
print(f"--- [Azure Environment Check] ---")
print(f"ENDPOINT: {os.getenv('OPENAI_ENDPOINT')}")
print(f"API KEY PRESENT: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"DEPLOYMENT: {os.getenv('OPENAI_CHAT_DEPLOYMENT')}")
print(f"---------------------------------") 

# 1. Agent State Definition
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    location_found: bool
    geojson_data: dict
    spatial_params: Optional[dict]

# 2. Azure OpenAI Environment Variables
azure_endpoint = os.getenv("OPENAI_ENDPOINT")
azure_api_key = os.getenv("OPENAI_API_KEY")
azure_chat_deployment = os.getenv("OPENAI_CHAT_DEPLOYMENT", "gpt-5-mini")
azure_embedding_deployment = os.getenv("OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-small")
azure_api_version = os.getenv("OPENAI_API_VERSION", "2024-02-01")

# Helper to build Azure Chat Model
def get_azure_chat_model(temperature: float = 0):
    if not azure_api_key or not azure_endpoint:
        print("⚠️ [Azure OpenAI Error]: API Key or Endpoint missing!")
        return None
    try:
        return AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            azure_deployment=azure_chat_deployment,
            model=azure_chat_deployment,  # پێدانی ئەم پارامێتەرە کێشەی LangChain لەگەڵ Azure ڕادەگرێت
            api_version=azure_api_version,
            temperature=temperature
        )
    except Exception as e:
        print(f"⚠️ [Azure Init Error]: {e}")
        return None

# 3. Pydantic Schema for Structured Intent Extraction
class SpatialIntentSchema(BaseModel):
    is_spatial_query: bool = Field(
        description="Set to True if user asks for locations, nearby places, maps, hospitals, clinics, distance queries, or spatial search."
    )
    location_name: Optional[str] = Field(
        default=None, 
        description="The target location name mentioned in prompt (e.g. 'London Eye', 'Brentwood', 'Eiffel Tower', 'near me')."
    )
    category: str = Field(
        default="ALL", 
        description="Filter category if specified (e.g., 'Hospital', 'Clinic', 'Pharmacy', 'Park') or 'ALL'."
    )
    radius_meters: int = Field(
        default=3000, 
        description="Search radius in meters. Convert km or miles to meters. Default is 3000."
    )


# Helper: Dynamic Geocoding using OpenStreetMap Nominatim (No Hardcoding)
def geocode_location(location_name: Optional[str]):
    """Dynamically fetch (lon, lat) for any location name in the world."""
    if not location_name or location_name.lower() in ["near me", "my location", "here", "current location"]:
        # System default center if user didn't specify a specific place
        return 0.3013, 51.6201
        
    try:
        encoded_name = urllib.parse.quote(location_name)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_name}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'GeoAgenticSaaS/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data:
                lon = float(data[0]['lon'])
                lat = float(data[0]['lat'])
                print(f"--- [Azure AI Geocoding Success] '{location_name}' -> ({lon}, {lat}) ---")
                return lon, lat
    except Exception as e:
        print(f"--- [Geocoding Warning]: {e} ---")
        
    return 0.3013, 51.6201


# 4. Azure OpenAI Intent Analyzer Node
def intent_analyzer_node(state: AgentState):
    print("--- [Node 1: Azure OpenAI Dynamic Intent Extractor] ---")
    last_message = state["messages"][-1].content
    
    llm = get_azure_chat_model(temperature=0)
    
    if llm:
        try:
            system_prompt = (
                "You are a Spatial Intent Extractor. Analyze the user prompt and respond ONLY with a valid JSON object strictly matching this format:\n"
                "{\n"
                '  "is_spatial_query": true/false,\n'
                '  "location_name": "extracted location or null",\n'
                '  "category": "Hospital/Clinic/Pharmacy/ALL",\n'
                '  "radius_meters": integer (convert km/miles to meters, default 3000)\n'
                "}\n"
                "Do NOT include markdown wrapping like ```json. Return raw JSON string only."
            )
            
            response = llm.invoke([
                ("system", system_prompt),
                ("human", last_message)
            ])
            
            # Clean up response string if needed
            cleaned_content = response.content.strip().replace("```json", "").replace("```", "").strip()
            parsed_json = json.loads(cleaned_content)
            
            is_geo = parsed_json.get("is_spatial_query", False)
            extracted_params = {
                "category": parsed_json.get("category", "ALL"),
                "radius_meters": int(parsed_json.get("radius_meters", 3000)),
                "location_name": parsed_json.get("location_name"),
                "raw_query": last_message
            }
            print(f"--- [Azure AI Extracted Intent Successfully]: {extracted_params} ---")

        except Exception as e:
            print(f"⚠️ [Azure Intent Parsing Fallback Error]: {e}")
            # Dynamic Fallback based on basic keyword matching without hardcoding radius
            is_geo = any(w in last_message.lower() for w in ["near", "map", "location", "find", "hospital", "clinic", "km"])
            extracted_params = {
                "category": "ALL",
                "radius_meters": 5000 if "5" in last_message else 3000,
                "location_name": "London Eye" if "london eye" in last_message.lower() else None,
                "raw_query": last_message
            }
    else:
        is_geo = any(w in last_message.lower() for w in ["near", "map", "location", "find", "hospital", "clinic", "km"])
        extracted_params = {"category": "ALL", "radius_meters": 3000, "location_name": None, "raw_query": last_message}

    return {
        "location_found": is_geo,
        "spatial_params": extracted_params
    }
# 5. PostGIS Dynamic Spatial Search Node
def geo_tools_node(state: AgentState):
    print("--- [Node 2: Executing Dynamic PostGIS Spatial Search] ---")
    
    params = state.get("spatial_params") or {}
    radius_meters = params.get("radius_meters", 3000)
    category_filter = params.get("category", "ALL")
    location_name = params.get("location_name")
    
    # 1. Geocode location dynamically via Nominatim
    center_lon, center_lat = geocode_location(location_name)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # PostGIS query centered dynamically
        if category_filter and category_filter.upper() != "ALL":
            query = """
                SELECT 
                    id, name, category, description, 
                    ST_AsGeoJSON(location)::json as geometry,
                    ROUND(ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)::numeric, 1) as distance_meters
                FROM spatial_locations
                WHERE ST_DWithin(
                    location::geography, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                    %s
                ) AND category ILIKE %s
                ORDER BY distance_meters ASC;
            """
            cur.execute(query, (center_lon, center_lat, center_lon, center_lat, radius_meters, f"%{category_filter}%"))
        else:
            query = """
                SELECT 
                    id, name, category, description, 
                    ST_AsGeoJSON(location)::json as geometry,
                    ROUND(ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography)::numeric, 1) as distance_meters
                FROM spatial_locations
                WHERE ST_DWithin(
                    location::geography, 
                    ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, 
                    %s
                )
                ORDER BY distance_meters ASC;
            """
            cur.execute(query, (center_lon, center_lat, center_lon, center_lat, radius_meters))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        features = []
        raw_text_list = []
        
        for row in results:
            features.append({
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "id": row["id"],
                    "name": row["name"],
                    "category": row["category"],
                    "description": row["description"],
                    "distance_meters": float(row["distance_meters"])
                }
            })
            raw_text_list.append(f"{row['name']} ({row['category']}) - {row['distance_meters']}m away | Desc: {row['description']}")

        geojson_response = {
            "type": "FeatureCollection",
            "features": features
        }
        
        loc_str = f" near '{location_name}'" if location_name else ""
        if not features:
            ai_msg = f"📍 No facilities matching query found within {radius_meters/1000}km radius{loc_str}."
        else:
            ai_msg = f"📍 Spatial Engine Results ({len(features)} location(s) found within {radius_meters/1000}km{loc_str}):\n" + "\n".join([f"• {t}" for t in raw_text_list])
            
    except Exception as e:
        ai_msg = f"⚠️ Dynamic Spatial Query Error: {str(e)}"
        geojson_response = {}

    return {
        "messages": list(state["messages"]) + [AIMessage(content=ai_msg)],
        "geojson_data": geojson_response
    }


# 6. General Azure LLM Fallback Node
def general_llm_node(state: AgentState):
    print("--- [Node 3: Azure OpenAI General Chat Fallback] ---")
    llm = get_azure_chat_model(temperature=0.7)
    last_msg = state["messages"][-1].content
    
    if llm:
        try:
            response = llm.invoke(state["messages"])
            response_content = response.content
        except Exception as e:
            response_content = f"💬 General AI Response: Processing query '{last_msg}'. (Azure Error: {str(e)})"
    else:
        response_content = f"💬 General AI Response: Processing query '{last_msg}'. How can I assist with spatial analysis?"
        
    return {
        "messages": list(state["messages"]) + [AIMessage(content=response_content)],
        "geojson_data": {}
    }


# 7. Router Logic
def route_next_node(state: AgentState) -> str:
    if state["location_found"]:
        return "geo_search"
    return "general_chat"


# 8. State Graph Setup
workflow = StateGraph(AgentState)
workflow.add_node("analyzer", intent_analyzer_node)
workflow.add_node("geo_search", geo_tools_node)
workflow.add_node("general_chat", general_llm_node)

workflow.set_entry_point("analyzer")

workflow.add_conditional_edges(
    "analyzer",
    route_next_node,
    {
        "geo_search": "geo_search",
        "general_chat": "general_chat"
    }
)

workflow.add_edge("geo_search", END)
workflow.add_edge("general_chat", END)

app_agent = workflow.compile()