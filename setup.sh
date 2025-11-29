#!/bin/bash
# setup.sh - Complete setup script for Library Desk Agent

echo "🚀 Setting up Library Desk Agent..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.12"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Error: Python $required_version or higher required. You have 
$python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Step 1: Setup Database
echo ""
echo "📚 Setting up database..."
cd db
if [ -f "library.db" ]; then
    echo "⚠️  Database exists. Removing old database..."
    rm library.db
fi

sqlite3 library.db < schema.sql
sqlite3 library.db < seed.sql
echo "✅ Database created and seeded"

# Step 2: Setup Backend
echo ""
echo "🔧 Setting up backend..."
cd ../server

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Step 3: Setup Environment Variables
echo ""
cd ..
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Step 4: Setup Frontend (optional)
echo ""
read -p "Do you want to set up the frontend? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "app" ]; then
        echo "🎨 Setting up frontend..."
        cd app
        npm install
        echo "✅ Frontend setup complete"
        cd ..
    else
        echo "⚠️  Frontend directory not found. Skipping..."
    fi
fi

echo ""
echo "✨ Setup complete! Next steps:"
echo ""
echo "1. Edit .env and add your GOOGLE_API_KEY"
echo "2. Run the agent:"
echo "   cd server"
echo "   source venv/bin/activate"
echo "   python agent.py"
echo ""
echo "Or use the run script: ./run.sh"

# ============================================
# run.sh - Quick run script
# ============================================
# Save this as a separate file called run.sh

cat > run.sh << 'RUNSCRIPT'
#!/bin/bash
# run.sh - Quick start script for Library Desk Agent

echo "🚀 Starting Library Desk Agent..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please run ./setup.sh first or create .env from .env.example"
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=your_google" .env && ! grep -q 
"GOOGLE_API_KEY=$" .env; then
    echo "✅ API key configured"
else
    echo "❌ Error: GOOGLE_API_KEY not configured in .env"
    echo "Please edit .env and add your Google Gemini API key"
    exit 1
fi

# Navigate to server and run
cd server

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate venv and run
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""
python agent.py
RUNSCRIPT

chmod +x run.sh
echo "✅ Created run.sh"
