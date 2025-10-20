# hybrid_chat.py
import json
import requests
import os
from typing import List
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from neo4j import GraphDatabase
import config

# -----------------------------
# Config
# -----------------------------
TOP_K = 5
INDEX_NAME = config.PINECONE_INDEX_NAME

# -----------------------------
# Initialize clients
# -----------------------------
model = SentenceTransformer(config.EMBEDDING_MODEL)

# Check API keys
if not config.PINECONE_API_KEY:
    print("❌ PINECONE_API_KEY not found in .env file")
    exit(1)

if not config.DEEPSEEK_API_KEY:
    print("❌ DEEPSEEK_API_KEY not found in .env file")
    exit(1)

pc = Pinecone(api_key=config.PINECONE_API_KEY)

# Connect to Pinecone index
if INDEX_NAME not in pc.list_indexes().names():
    print(f"Creating managed index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=config.PINECONE_VECTOR_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)

# Connect to Neo4j (with optional password)
try:
    if config.NEO4J_PASSWORD:
        driver = GraphDatabase.driver(
            config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
    else:
        # Try without password first
        driver = GraphDatabase.driver(config.NEO4J_URI)
    
    # Test connection
    with driver.session() as session:
        session.run("RETURN 1")
    print("✅ Neo4j connected successfully")
    NEO4J_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Neo4j not available: {e}")
    print("   Continuing with vector search only...")
    driver = None
    NEO4J_AVAILABLE = False

# -----------------------------
# DeepSeek API Integration
# -----------------------------
def deepseek_chat(prompt):
    """Call DeepSeek Chat API with fallback."""
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "alibaba/tongyi-deepresearch-30b-a3b:free",
        "messages": prompt if isinstance(prompt, list) else [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️  DeepSeek API error: {str(e)}")
        print("   Using fallback response generation...")
        return generate_fallback_response(prompt)

def generate_fallback_response(prompt):
    """Generate an intelligent fallback response using vector search data when DeepSeek API is unavailable."""
    if isinstance(prompt, list) and len(prompt) > 1:
        user_content = prompt[1]["content"]
        # Extract the original query from the prompt
        lines = user_content.split('\n')
        user_query = ""
        for line in lines:
            if line.startswith("USER QUESTION:"):
                user_query = line.replace("USER QUESTION:", "").strip()
                break
        
        # Extract search results from the prompt
        search_results = []
        in_detailed_section = False
        for line in lines:
            if "=== DETAILED INFORMATION ===" in line:
                in_detailed_section = True
                continue
            elif "=== SUMMARY ===" in line:
                in_detailed_section = False
                continue
            elif in_detailed_section and line.strip() and not line.startswith("="):
                search_results.append(line.strip())
    else:
        user_query = str(prompt)
        search_results = []
    
    # If we have search results, use them to create a response
    if search_results and len([r for r in search_results if r and not r.startswith("No")]) > 0:
        response = f"🇻🇳 **Vietnam Travel Recommendations for: {user_query}**\n\n"
        
        # Process the search results to extract detailed information
        places_found = []
        locations_by_type = {}
        
        for result in search_results[:8]:  # Process more results
            if result and not result.startswith("No") and "." in result:
                lines = result.split('\n')
                name = ""
                place_type = ""
                location = ""
                tags = []
                description = ""
                
                for line in lines:
                    line = line.strip()
                    if line and "." in line and "(" in line and ")" in line:
                        # Extract name and type
                        parts = line.split("(")
                        if len(parts) >= 2:
                            name = parts[0].strip().split(".")[-1].strip()
                            place_type = parts[1].split(")")[0] if ")" in parts[1] else "Location"
                    elif line.startswith("Location:"):
                        location = line.replace("Location:", "").strip()
                    elif line.startswith("Tags:"):
                        tags_str = line.replace("Tags:", "").strip()
                        if tags_str and tags_str != "N/A":
                            tags = [t.strip().strip("'\"[]") for t in tags_str.split(",")]
                    elif line.startswith("Description:"):
                        description = line.replace("Description:", "").strip()
                
                if name and place_type:
                    if place_type not in locations_by_type:
                        locations_by_type[place_type] = []
                    
                    entry = {
                        "name": name,
                        "location": location,
                        "tags": tags,
                        "description": description[:150] + "..." if len(description) > 150 else description
                    }
                    locations_by_type[place_type].append(entry)
        
        # Format the response by type
        if locations_by_type:
            for place_type, places in locations_by_type.items():
                if places:
                    response += f"## {place_type}s\n"
                    for place in places[:3]:  # Limit to top 3 per type
                        response += f"• **{place['name']}**"
                        if place['location']:
                            response += f" - {place['location']}"
                        if place['tags']:
                            response += f" ({', '.join(place['tags'][:3])})"
                        response += "\n"
                        if place['description']:
                            response += f"  {place['description']}\n"
                    response += "\n"
            
            total_found = sum(len(places) for places in locations_by_type.values())
            response += f"💡 **Found {total_found} relevant options** in our Vietnam travel database.\n\n"
            
            # Add practical advice based on query type
            if "hotel" in user_query.lower() or "accommodation" in user_query.lower():
                response += "💰 **Booking Tips**: Book in advance during peak season (Dec-Mar). Consider location relative to attractions you want to visit."
            elif "food" in user_query.lower() or "restaurant" in user_query.lower():
                response += "🍜 **Food Tips**: Try local street food for authentic experiences. Peak dining hours are 11:30-13:30 and 17:30-20:00."
            elif "attraction" in user_query.lower() or "sightseeing" in user_query.lower():
                response += "🎫 **Visiting Tips**: Early morning visits (7-9 AM) offer cooler weather and fewer crowds. Many attractions offer combo tickets."
            elif "activity" in user_query.lower():
                response += "⏰ **Activity Tips**: Book tours in advance, especially during peak season. Weather can affect outdoor activities."
            
        else:
            response += "I found several relevant options in our database. "
            
        return response
    
    # Fallback to keyword-based responses if no search results
    query_lower = user_query.lower() if user_query else ""
    
    if "zoo" in query_lower:
        return """🦁 Vietnam Zoos and Wildlife Parks:

**Saigon Zoo and Botanical Gardens** (Ho Chi Minh City)
- One of the oldest zoos in the world (established 1864)
- Over 2,000 animals and 1,800 plant species
- Location: District 1, Ho Chi Minh City
- Hours: 7:00 AM - 6:00 PM daily
- Admission: ~50,000 VND ($2 USD)

**Hanoi Zoo** (Thu Le Park)
- Located in central Hanoi
- Features local and exotic animals
- Family-friendly with playgrounds
- Admission: ~30,000 VND ($1.30 USD)

**Vinpearl Safari** (Phu Quoc)
- Modern safari park with over 3,000 animals
- Drive-through safari experience
- Conservation focus
- Part of Vinpearl resort complex

**Best Time to Visit**: Early morning or late afternoon to avoid heat and see more active animals."""

    elif "museum" in query_lower:
        return """🏛️ Vietnam Museums:

**War Remnants Museum** (Ho Chi Minh City)
- Most visited museum in Vietnam
- Vietnam War history and artifacts
- Admission: 40,000 VND ($1.70 USD)

**Vietnam Museum of Ethnology** (Hanoi)
- 54 ethnic groups of Vietnam
- Traditional houses and cultural displays
- Admission: 40,000 VND ($1.70 USD)

**Imperial City** (Hue)
- UNESCO World Heritage site
- Former royal palace complex
- Admission: 200,000 VND ($8.50 USD)

**Cu Chi Tunnels** (Ho Chi Minh City)
- Underground tunnel network from war
- Half-day tours available
- Admission: 110,000 VND ($4.70 USD)"""

    elif "romantic" in query_lower or "couple" in query_lower:
        return """🌹 Romantic Vietnam Destinations:

**Ha Long Bay**: Luxury cruise with private balcony, sunset views, candlelit dinners on deck.

**Hoi An**: Lantern-lit ancient streets, couples cooking classes, riverside dining.

**Sapa**: Mountain romance with terraced rice fields, cozy lodges, scenic train journeys.

**Da Lat**: "City of Eternal Spring" with flower gardens, lakes, and cool mountain air.

**Best Time**: February-May for perfect weather
**Budget**: $200-500 per couple for mid-range experience"""

    elif "food" in query_lower or "culinary" in query_lower:
        return """🍜 Vietnam Culinary Experiences:

**Hanoi**: Street food tours in Old Quarter, pho ga, egg coffee at hidden cafes.

**Ho Chi Minh City**: Cooking classes, Ben Thanh Market tours, rooftop dining.

**Hoi An**: Traditional cooking classes, cao lau noodles, white rose dumplings.

**Must-Try Dishes**: Pho, banh mi, fresh spring rolls, Vietnamese coffee
**Food Tours**: $20-50 per person
**Cooking Classes**: $30-80 per person"""

    else:
        return f"""🇻🇳 Vietnam Travel Information for: "{user_query}"

Vietnam offers incredible diversity from bustling cities to serene landscapes. Popular destinations include:

**North**: Hanoi (culture), Ha Long Bay (nature), Sapa (mountains)
**Central**: Hue (history), Hoi An (charm), Da Nang (beaches)  
**South**: Ho Chi Minh City (energy), Mekong Delta (rivers)

**Best Time to Visit**: February-May, September-November
**Visa**: Most nationalities need visa or e-visa
**Currency**: Vietnamese Dong (VND)
**Language**: Vietnamese (English widely spoken in tourist areas)

For specific recommendations about {user_query}, please provide more details about your interests, budget, or travel dates!"""

# -----------------------------
# Helper functions
# -----------------------------
def embed_text(text: str) -> List[float]:
    """Get embedding for a text string using SentenceTransformers."""
    embedding = model.encode([text])
    return embedding[0].tolist()

def get_vector_context(query_text: str, top_k=TOP_K):
    """Query Pinecone index using embedding."""
    vec = embed_text(query_text)
    res = index.query(
        vector=vec,
        top_k=top_k,
        include_metadata=True,
        include_values=False
    )
    print(f"DEBUG: Pinecone returned {len(res['matches'])} results")
    return res["matches"]

def get_graph_context(query_text: str):
    """Fetch graph context from Neo4j based on query."""
    facts = []
    
    if not NEO4J_AVAILABLE or not driver:
        print("DEBUG: Neo4j not available, skipping graph search")
        return facts
    
    try:
        with driver.session() as session:
            # Search for nodes containing query terms
            q = (
                "MATCH (n:Entity)-[r]-(m:Entity) "
                "WHERE toLower(n.name) CONTAINS toLower($query) "
                "OR toLower(n.description) CONTAINS toLower($query) "
                "OR any(tag IN n.tags WHERE toLower(tag) CONTAINS toLower($query)) "
                "RETURN n.id AS source_id, n.name AS source_name, "
                "type(r) AS rel, m.id AS target_id, m.name AS target_name, "
                "m.description AS target_desc "
                "LIMIT 10"
            )
            recs = session.run(q, query=query_text)
            for r in recs:
                facts.append({
                    "source_id": r["source_id"],
                    "source_name": r["source_name"],
                    "rel": r["rel"],
                    "target_id": r["target_id"],
                    "target_name": r["target_name"],
                    "target_desc": (r["target_desc"] or "")[:200]
                })
    except Exception as e:
        print(f"DEBUG: Graph query failed: {e}")
    
    print(f"DEBUG: Graph returned {len(facts)} facts")
    return facts

def build_prompt(user_query, vector_context, graph_context):
    """Build a chat prompt combining vector DB matches and graph facts."""
    system_prompt = """You are an expert Vietnam travel assistant. You have access to a comprehensive database of Vietnam travel information including destinations, activities, hotels, and attractions.

IMPORTANT: Use the provided search results to give specific, detailed, and accurate answers. Always reference the actual places, activities, and information from the search results.

Your responses should be:
1. Specific and detailed using the provided data
2. Include practical information (prices, timing, locations)
3. Well-structured with clear sections
4. Actionable with concrete recommendations
5. Based on the actual search results provided

If the user asks about specific topics like zoos, museums, restaurants, or activities, use the search results to provide detailed information about those specific places."""

    # Format vector context with full details
    vec_info = []
    detailed_info = []
    
    for i, match in enumerate(vector_context):
        meta = match["metadata"]
        score = match.get("score", 0)
        
        name = meta.get('name', 'Unknown')
        place_type = meta.get('type', 'Unknown')
        city = meta.get('city', meta.get('region', ''))
        tags = meta.get('tags', [])
        
        # Get the full text content if available
        full_text = meta.get('description', '')
        if not full_text and 'text' in meta:
            full_text = meta['text']
        
        # Create detailed entry
        detail_entry = f"""
{i+1}. {name} ({place_type})
   Location: {city}
   Tags: {', '.join(tags) if tags else 'N/A'}
   Description: {full_text[:300] if full_text else 'No description available'}
   Relevance Score: {score:.3f}
"""
        detailed_info.append(detail_entry)
        
        # Create summary entry
        summary = f"• {name} ({place_type})"
        if city:
            summary += f" in {city}"
        if tags:
            summary += f" - {', '.join(tags[:3])}"
        vec_info.append(summary)

    # Format graph context
    graph_info = []
    for fact in graph_context:
        relation = f"• {fact['source_name']} → {fact['rel']} → {fact['target_name']}"
        if fact['target_desc']:
            relation += f": {fact['target_desc'][:100]}..."
        graph_info.append(relation)

    # Create comprehensive context
    search_context = f"""
SEARCH RESULTS FOR: "{user_query}"

=== DETAILED INFORMATION ===
{''.join(detailed_info) if detailed_info else "No specific matches found in database"}

=== SUMMARY ===
{chr(10).join(vec_info[:8]) if vec_info else "No relevant matches found"}

=== RELATIONSHIPS ===
{chr(10).join(graph_info[:10]) if graph_info else "No relationships found"}
"""

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""
{search_context}

USER QUESTION: {user_query}

Please provide a comprehensive answer using the search results above. Include specific names, locations, and details from the database. If asking about specific types of places (like zoos, museums, restaurants), list them with details from the search results.
"""}
    ]
    return prompt

# -----------------------------
# Interactive chat
# -----------------------------
def interactive_chat():
    print("🇻🇳 Hybrid Vietnam Travel Assistant (Powered by DeepSeek)")
    print("Ask me anything about traveling in Vietnam! Type 'exit' to quit.\n")
    
    while True:
        query = input("🗣️  Enter your travel question: ").strip()
        if not query or query.lower() in ("exit", "quit"):
            print("👋 Thanks for using the travel assistant!")
            break

        print("\n🔍 Searching for relevant information...")
        
        # Get vector context from Pinecone
        vector_matches = get_vector_context(query, top_k=TOP_K)
        
        # Get graph context from Neo4j
        graph_facts = get_graph_context(query)
        
        # Build prompt and get response from DeepSeek
        prompt = build_prompt(query, vector_matches, graph_facts)
        answer = deepseek_chat(prompt)
        
        print("\n💬 Response:\n")
        print(answer)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    interactive_chat()
