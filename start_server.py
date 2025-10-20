#!/usr/bin/env python3
"""
Simple startup script for the Business Proposal Generator
"""

import os
from app import app, db, seed_funding_sources, FundingSource

print("🚀 Starting AI-Powered Business Proposal Generator & Funding Finder")
print("=" * 60)

# Initialize database
with app.app_context():
    print("📊 Creating database tables...")
    db.create_all()
    
    print("🌱 Checking and seeding funding sources...")
    try:
        if not FundingSource.query.first():
            seed_funding_sources()
            print("✅ Funding sources seeded successfully!")
        else:
            print("ℹ️  Funding sources already exist")
    except Exception as e:
        print(f"⚠️  Warning: Could not seed funding sources: {e}")

print("\n🌐 Starting Flask server...")
print("📍 Backend API: http://localhost:5000")
print("🔗 Health Check: http://localhost:5000/api/health")
print("🔗 API Endpoints:")
print("   - POST /api/register (User registration)")
print("   - POST /api/login (User login)")
print("   - POST /api/generate-business-plan (Generate business plan)")
print("   - POST /api/upload-proposal (Upload document)")
print("\n" + "=" * 60)
print("Press Ctrl+C to stop the server")
print("=" * 60)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False  # Disable reloader to avoid issues
    )
