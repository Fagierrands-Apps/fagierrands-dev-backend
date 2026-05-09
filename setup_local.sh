#!/bin/bash
# Local Development Setup Script

echo "🚀 Setting up Fagi Errands Backend for Local Development"
echo "=========================================================="

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install it first:"
    echo "   sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.local..."
    cp .env.local .env
    echo "⚠️  Please update .env with your actual credentials (TextPie, etc.)"
else
    echo "✅ .env file already exists"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create local database
echo "🗄️  Setting up local database..."
sudo -u postgres psql -c "CREATE DATABASE fagierrands_local;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER postgres WITH PASSWORD 'postgres';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fagierrands_local TO postgres;" 2>/dev/null

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Create superuser (optional)
echo ""
echo "👤 Do you want to create a superuser? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "The server will be available at: http://localhost:8000"
echo "Admin panel: http://localhost:8000/admin"
echo "API docs: http://localhost:8000/swagger/"
