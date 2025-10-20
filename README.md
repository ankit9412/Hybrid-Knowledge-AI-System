# Hybrid Knowledge AI System

A hybrid AI-powered travel assistant that combines vector search, knowledge graphs, and conversational AI to provide personalized Vietnam travel recommendations.

## ✨ Features

- **🔍 Hybrid Search**: Vector similarity search (Pinecone) + Knowledge graphs (Neo4j)
- **🤖 AI Chat**: OpenRouter API with Alibaba Tongyi DeepResearch model
- **🌐 Web Interface**: Modern Flask-based web application
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🎯 Contextual Recommendations**: Personalized travel advice based on comprehensive data

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Pinecone API key
- OpenRouter API key
- Neo4j database (optional)

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/ankit9412/Hybrid-Knowledge-AI-System.git
   cd Hybrid-Knowledge-AI-System
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Load travel data**
   ```bash
   python pinecone_upload.py      # Load to vector database
   python load_to_neo4j.py        # Load to graph database (optional)
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000` to start chatting!

## ⚙️ Configuration

Create a `.env` file:

```env
# Required API Keys
PINECONE_API_KEY=your_pinecone_api_key
DEEPSEEK_API_KEY=your_openrouter_api_key

# Optional Neo4j (works without it)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Database Settings
PINECONE_INDEX_NAME=vietnam-travel
PINECONE_VECTOR_DIM=384
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Vector Search  │    │ Knowledge Graph │
│     (Flask)     │◄──►│   (Pinecone)    │◄──►│    (Neo4j)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   AI Chat API   │
                    │  (OpenRouter)   │
                    └─────────────────┘
```

## 📁 Project Structure

```
vietnam-travel-assistant/
├── app.py                      # Flask web application
├── hybrid_chat.py              # Core chat functionality  
├── config.py                   # Configuration management
├── pinecone_upload.py          # Vector database loader
├── load_to_neo4j.py           # Graph database loader
├── check_dataset.py           # Dataset validation
├── verify_setup.py            # Setup verification
├── vietnam_travel_dataset.json # Travel data (1000+ entries)
├── templates/
│   └── index.html             # Web interface
├── static/
│   ├── css/style.css          # Styling
│   └── js/app.js              # Frontend logic
├── requirements.txt           # Dependencies
└──.env.example              # Environment template
```

## 🎯 Usage Examples

**Ask about destinations:**
- "Best places to visit in Vietnam"
- "Romantic spots in Da Lat"
- "Street food in Ho Chi Minh City"

**Get specific recommendations:**
- "Hotels in Hanoi under $50"
- "Things to do in Hoi An"
- "Best time to visit Sapa"

**Plan activities:**
- "3-day itinerary for Ha Long Bay"
- "Adventure activities in Da Nang"
- "Cultural experiences in Hue"

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/chat` | POST | Send chat message |
| `/api/health` | GET | System health check |
| `/api/conversation` | GET | Get chat history |
| `/api/clear` | POST | Clear conversation |

## 📊 Data Coverage

The system includes comprehensive Vietnam travel data:

- **🏙️ Cities**: Hanoi, Ho Chi Minh City, Da Nang, Hoi An, Hue, Da Lat, Nha Trang, Sapa
- **🏛️ Attractions**: Museums, temples, landmarks, natural sites
- **🏨 Accommodations**: Hotels, hostels, resorts across all price ranges  
- **🍜 Food & Dining**: Restaurants, street food, local specialties
- **🚌 Transportation**: Flights, trains, buses, local transport
- **🎯 Activities**: Tours, adventures, cultural experiences

## 🛠️ Development

### Adding New Data
1. Update `vietnam_travel_dataset.json`
2. Re-run upload scripts:
   ```bash
   python pinecone_upload.py
   python load_to_neo4j.py
   ```

### Testing Setup
```bash
python verify_setup.py    # Verify configuration
python check_dataset.py   # Validate data
```

### Command Line Interface
```bash
python hybrid_chat.py     # Chat in terminal
```

## 🔍 Troubleshooting

**Neo4j Connection Issues**
- System works without Neo4j (vector search only)
- Check if Neo4j is running: `neo4j status`

**API Key Problems**
- Verify keys in `.env` file
- Check API quotas and limits
- Test with `python verify_setup.py`

**Performance Issues**
- Reduce `TOP_K` value in config
- Check internet connection
- Monitor API response times

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Vietnam tourism data sources
- Pinecone for vector search
- OpenRouter for AI API access
- Neo4j for graph database
- Flask community for web framework

---

**Made with ❤️ for Vietnam travelers worldwide**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
