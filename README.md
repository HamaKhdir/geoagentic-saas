# 🌍 GeoAgentic Copilot (Natural Language Spatial Intelligence SaaS)

GeoAgentic Copilot is an enterprise-grade AI-powered Geospatial Intelligence platform built with **LangGraph**, **Azure OpenAI (`gpt-5-mini`)**, and **PostGIS**. It enables users to perform natural language spatial queries, dynamic geocoding, and real-time interactive mapping.

---

## 🌟 Key Features

- **Natural Language Spatial Intent Extraction:** Powered by Azure OpenAI to dynamically extract intent, distance radius, categories, and locations.
- **Dynamic Spatial Engine:** Executes optimized spatial queries (`ST_DWithin`, `ST_Distance`) on PostgreSQL/PostGIS.
- **Global Dynamic Geocoding:** Automatically translates location names (e.g., "London Eye", "Brentwood Station") to exact lat/lon coordinates via OpenStreetMap Nominatim.
- **Fallback General AI Chat:** Seamlessly handles non-spatial queries using general LLM capabilities.
- **Interactive Map Visualization:** Frontend React + Leaflet setup for real-time spatial marker rendering and auto-panning.
- **Full Dockerized Setup:** One-command deployment with Docker Compose.

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI, Python 3.11
- **Orchestration & AI:** LangGraph, LangChain, Azure OpenAI (`gpt-5-mini`)
- **Database:** PostgreSQL with PostGIS extensions
- **Frontend:** React, Tailwind CSS, Leaflet Maps
- **Containerization:** Docker & Docker Compose

---

## 🚀 Quick Start & Installation

### Prerequisite
Ensure you have **Docker** and **Docker Compose** installed on your system.

### 1. Clone the Repository
```bash
git clone [https://github.com/HamaKhdir/geoagentic-saas.git](https://github.com/HamaKhdir/geoagentic-saas.git)
```bash
cd geoagentic-saas
```
### 2. Configure Environment Variables
Copy the template environment file and replace it with your actual Azure OpenAI keys:

```bash
cp .env.example .env
```
Edit `.env` and configure your keys:

```env
OPENAI_ENDPOINT=https://<your-azure-endpoint>.openai.azure.com
OPENAI_API_KEY=<your-azure-api-key>
OPENAI_CHAT_DEPLOYMENT=gpt-5-mini
```
### 3. Launch with Docker Compose
Run the entire stack (PostGIS, FastAPI Backend, and Frontend):

```bash
docker-compose up --build -d
```
Access the application at:

• Frontend App: `http://localhost:3000`

• Backend API Docs: `http://localhost:8000/docs`

🧪 Example Queries to Try

**1. Spatial Radius Query:**

"Show me all hospitals within 5 km of Brentwood station."

**2. Location-Based Search:**

"Find any pharmacies or clinics near London Eye."

**3. General Knowledge Fallback:**

"What is the difference between vector search and spatial query?"

🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.