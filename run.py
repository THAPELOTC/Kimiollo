#!/usr/bin/env python3
"""
Startup script for the AI-Powered Business Proposal Generator & Funding Finder
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db, seed_funding_sources, FundingSource
    
    print("🚀 Starting AI-Powered Business Proposal Generator & Funding Finder")
    print("=" * 60)
    
    # Initialize database and seed data
    with app.app_context():
        print("📊 Initializing database...")
        db.create_all()
        
        print("🌱 Seeding funding sources...")
        if not FundingSource.query.first():
            seed_funding_sources()
            print("✅ Funding sources seeded successfully!")
        else:
            print("ℹ️  Funding sources already exist")
    
    print("\n🌐 Starting Flask server...")
    print("📍 Backend will be available at: http://localhost:5000")
    print("🔗 API Health Check: http://localhost:5000/api/health")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Please install required dependencies:")
    print("pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error starting application: {e}")
    sys.exit(1)
