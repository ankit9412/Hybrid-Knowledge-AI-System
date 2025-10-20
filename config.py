# config.py - Configuration using environment variables for security
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DeepSeek API Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-east1-gcp"
PINECONE_INDEX_NAME = "vietnam-travel"
PINECONE_VECTOR_DIM = 384  # Using sentence-transformers model dimension

# Neo4j Configuration (no password required)
NEO4J_URI = os.getenv('NEO4J_URI', "bolt://localhost:7687")
NEO4J_USER = os.getenv('NEO4J_USER', "neo4j")
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', "")  # Empty password
USE_NEO4J = True  # Set to False if you don't want to use Neo4j

# For embedding generation (using sentence-transformers - completely local)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Local fallback storage (if Pinecone fails)
LOCAL_VECTOR_FILE = "local_vectors.json"