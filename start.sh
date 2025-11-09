#!/bin/bash

# Constructoken Hackathon - Quick Start Script
# This script helps you get the application up and running quickly

set -e  # Exit on error

echo "🏗️  Constructoken Hackathon - Quick Start"
echo "========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.9+"; exit 1; }

# Check PostgreSQL
echo "📋 Checking PostgreSQL..."
which psql > /dev/null 2>&1 || { echo "⚠️  PostgreSQL not found. Please install PostgreSQL 12+"; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found"
    echo "📝 Creating .env from env.hackathon.template (pre-configured wallets)..."
    cp env.hackathon.template .env
    echo ""
    echo "✅ Wallets del Interledger Test Wallet ya configuradas:"
    echo "   - US Wallet (USD): pancho"
    echo "   - Finsus Wallet (MXN): destinatario"
    echo "   - Merchant Wallet (MXN): merchant"
    echo ""
    echo "⚙️  SOLO NECESITAS ACTUALIZAR:"
    echo "   DATABASE_URL en el archivo .env con tu PostgreSQL local"
    echo ""
    echo "📖 Ver configuración completa en: SETUP_TESTNET.md"
    echo "📖 Guía rápida: INSTRUCCIONES_RAPIDAS.md"
    echo ""
    echo "Press Enter when ready to continue, or Ctrl+C to exit and configure DATABASE_URL"
    read
fi

# Check database connection
echo "🗄️  Checking database connection..."
python3 -c "from app.config import settings; print(f'Database URL: {settings.DATABASE_URL}')" || {
    echo "❌ Error loading configuration. Please check your .env file"
    exit 1
}

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from app.database import init_db; init_db()" || {
    echo "⚠️  Database initialization failed. Please ensure PostgreSQL is running and credentials are correct"
    echo "   Create database: createdb constructoken_hackathon"
    exit 1
}

# Load mock data for testing
echo "📊 Loading test data (mockup)..."
python3 << 'PYTHON_SCRIPT'
from app.database import SessionLocal
from app.models import Migrant, Project, ProjectStage
from datetime import datetime
import sys

try:
    db = SessionLocal()
    
    # Check if test data already exists
    existing_migrant = db.query(Migrant).filter(Migrant.email == "pancho.test@example.com").first()
    
    if existing_migrant:
        print("✅ Test data already exists, skipping...")
    else:
        # Create test migrant (Pancho)
        migrant = Migrant(
            full_name="Pancho Rodriguez",
            email="pancho.test@example.com",
            phone="+1-555-0100",
            us_wallet_address="https://ilp.interledger-test.dev/pancho",
            finsus_wallet_address="https://ilp.interledger-test.dev/destinatario"
        )
        db.add(migrant)
        db.flush()
        
        # Create test project
        project = Project(
            migrant_id=migrant.id,
            name="Casa Familiar en Guadalajara",
            description="Construcción de casa para la familia Rodriguez",
            total_budget_mxn=500000.00,
            status="planning"
        )
        db.add(project)
        db.flush()
        
        # Create project stages
        stages = [
            {
                "name": "Cimientos y Estructura",
                "description": "Excavación, cimientos y columnas principales",
                "target_amount_mxn": 150000.00,
                "order": 1
            },
            {
                "name": "Muros y Techos",
                "description": "Construcción de muros y losa de techo",
                "target_amount_mxn": 120000.00,
                "order": 2
            },
            {
                "name": "Instalaciones",
                "description": "Instalaciones eléctricas, hidráulicas y sanitarias",
                "target_amount_mxn": 80000.00,
                "order": 3
            },
            {
                "name": "Acabados",
                "description": "Pisos, pintura, puertas y ventanas",
                "target_amount_mxn": 100000.00,
                "order": 4
            },
            {
                "name": "Exteriores",
                "description": "Jardinería, banqueta y acabados exteriores",
                "target_amount_mxn": 50000.00,
                "order": 5
            }
        ]
        
        for stage_data in stages:
            stage = ProjectStage(
                project_id=project.id,
                name=stage_data["name"],
                description=stage_data["description"],
                target_amount_mxn=stage_data["target_amount_mxn"],
                current_amount_mxn=0.0,
                order=stage_data["order"],
                is_funded=False,
                is_purchased=False
            )
            db.add(stage)
        
        db.commit()
        print("✅ Test data loaded successfully!")
        print(f"   - Migrant: {migrant.full_name} (ID: {migrant.id})")
        print(f"   - Project: {project.name} (ID: {project.id})")
        print(f"   - Stages: {len(stages)} stages created")
        
    db.close()
    
except Exception as e:
    print(f"❌ Error loading test data: {e}")
    sys.exit(1)

PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "⚠️  Failed to load test data, but continuing..."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Constructoken API..."
echo ""
echo "   API will be available at: http://localhost:8000"
echo "   Interactive docs (Swagger): http://localhost:8000/docs"
echo "   ReDoc documentation: http://localhost:8000/redoc"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

