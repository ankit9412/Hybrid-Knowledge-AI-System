#!/usr/bin/env python3
"""
Quick setup verification for Hybrid AI Travel Assistant
"""
import os
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required keys."""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    load_dotenv()
    
    required_keys = ['DEEPSEEK_API_KEY', 'PINECONE_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            missing_keys.append(key)
        else:
            print(f"✅ {key} found")
    
    if missing_keys:
        print(f"❌ Missing keys in .env: {missing_keys}")
        return False
    
    return True

def test_imports():
    """Test if required packages are installed."""
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers imported")
    except ImportError:
        print("❌ sentence-transformers not installed")
        return False
    
    try:
        from pinecone import Pinecone
        print("✅ pinecone imported")
    except ImportError:
        print("❌ pinecone not installed")
        return False
    
    try:
        import requests
        print("✅ requests imported")
    except ImportError:
        print("❌ requests not installed")
        return False
    
    return True

def test_embedding_model():
    """Test if embedding model can be loaded."""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_embedding = model.encode(["test"])
        print(f"✅ Embedding model loaded (dimension: {len(test_embedding[0])})")
        return True
    except Exception as e:
        print(f"❌ Embedding model failed: {e}")
        return False

def main():
    print("🔍 Verifying Hybrid AI Travel Assistant Setup")
    print("=" * 50)
    
    checks = [
        ("Environment file", check_env_file),
        ("Package imports", test_imports),
        ("Embedding model", test_embedding_model)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! You're ready to go!")
        print("\n📋 Next steps:")
        print("1. Run: python pinecone_upload.py")
        print("2. Run: python load_to_neo4j.py (optional)")
        print("3. Run: python hybrid_chat.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()