import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hama_dev:SecretPassword123!@db:5432/geoagentic_db")

def get_db_connection():
    """Establish connection to PostGIS database."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    """Initialize PostGIS schema safely."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Enable PostGIS extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        
        # 2. Safely attempt pgvector extension if supported by DB image
        try:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        except Exception as vec_err:
            conn.rollback()
            print(f"--- [Notice]: pgvector extension bypassed: {vec_err} ---")

        # 3. Create spatial locations table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS spatial_locations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                location GEOMETRY(Point, 4326),
                description TEXT
            );
        """)
        conn.commit()
        
        # 4. Seed initial dataset if table is empty
        cur.execute("SELECT COUNT(*) FROM spatial_locations;")
        count = cur.fetchone()["count"]
        
        if count == 0:
            cur.execute("""
                INSERT INTO spatial_locations (name, category, location, description) VALUES
                ('Brentwood Community Hospital', 'Hospital', ST_SetSRID(ST_MakePoint(0.3061, 51.6214), 4326), 'Main emergency healthcare facility with fracture unit and primary care in Brentwood'),
                ('Nuffield Health Brentwood Hospital', 'Hospital', ST_SetSRID(ST_MakePoint(0.3150, 51.6280), 4326), 'Private surgical hospital offering specialist surgeries and orthopedic diagnostic services'),
                ('Shenfield Medical Centre', 'Clinic', ST_SetSRID(ST_MakePoint(0.3310, 51.6310), 4326), 'Local GP practice providing primary care, vaccinations, and routine medical checkups');
            """)
            conn.commit()
            print("--- [Database Initialized]: PostGIS schema ready ---")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"--- [Database Error]: Initialization failed: {e} ---")