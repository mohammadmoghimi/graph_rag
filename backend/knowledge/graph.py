import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()  # This will look for a .env file in the same directory

def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    # Optional: Add debug prints to verify the values are loaded
    print(f"Connecting to Neo4j at {uri}")
    
    return GraphDatabase.driver(
        uri,
        auth=(username, password)
    )