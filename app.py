#!/usr/bin/env python3
"""
Flask Web Application for Hybrid AI Travel Assistant
Professional web interface with REST API endpoints
"""
from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
import uuid

# Import our hybrid chat functionality
from hybrid_chat import get_vector_context, get_graph_context, build_prompt, deepseek_chat
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Store conversations in memory (in production, use a database)
conversations = {}

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    """Check system health status."""
    try:
        # Test vector search
        vector_results = get_vector_context("test", top_k=1)
        vector_healthy = len(vector_results) > 0
        
        # Test graph search (optional)
        graph_results = get_graph_context("test")
        graph_healthy = True  # Always healthy since it's optional
        
        # Test DeepSeek API (with fallback)
        test_prompt = [{"role": "user", "content": "Hello"}]
        ai_response = deepseek_chat(test_prompt)
        ai_healthy = "Error calling DeepSeek API" not in ai_response
        
        status = "healthy" if (vector_healthy and ai_healthy) else "limited"
        
        return jsonify({
            "status": status,
            "services": {
                "vector_search": vector_healthy,
                "graph_search": graph_healthy,
                "ai_chat": ai_healthy
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return AI responses."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Get or create session ID
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            conversations[session_id] = []
        
        # Add user message to conversation
        conversations[session_id].append({
            "type": "user",
            "message": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Get context from vector search
        print(f"🔍 Processing query: {user_message}")
        vector_matches = get_vector_context(user_message, top_k=5)
        
        # Get context from graph search
        graph_facts = get_graph_context(user_message)
        
        # Build prompt and get AI response
        prompt = build_prompt(user_message, vector_matches, graph_facts)
        ai_response = deepseek_chat(prompt)
        
        # Add assistant response to conversation
        conversations[session_id].append({
            "type": "assistant",
            "message": ai_response,
            "sources": {
                "vector_results": len(vector_matches),
                "graph_results": len(graph_facts)
            },
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "response": ai_response,
            "sources": {
                "vector_results": len(vector_matches),
                "graph_results": len(graph_facts)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            "error": "I'm having trouble processing your request. Please try again.",
            "details": str(e) if app.debug else None
        }), 500

@app.route('/api/conversation')
def get_conversation():
    """Get conversation history for the current session."""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        return jsonify(conversations[session_id])
    return jsonify([])

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear the current conversation."""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        del conversations[session_id]
    session.pop('session_id', None)
    return jsonify({"status": "cleared"})

@app.route('/api/stats')
def get_stats():
    """Get system statistics."""
    try:
        total_conversations = len(conversations)
        total_messages = sum(len(conv) for conv in conversations.values())
        
        return jsonify({
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "active_sessions": len([s for s in conversations.keys()]),
            "system_status": "operational"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting Vietnam Travel Assistant Web Interface")
    print("=" * 60)
    print(f"📊 Vector Database: Pinecone")
    print(f"🕸️  Knowledge Graph: Neo4j (optional)")
    print(f"🤖 AI Model: DeepSeek with fallbacks")
    print(f"🌐 Web Interface: Flask + Professional UI")
    print("=" * 60)
    
    # Check if running in development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        threaded=True
    )