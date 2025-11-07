#!/bin/bash

echo "🚀 AI TICKET PROCESSOR - SETUP"
echo "================================"
echo ""

# Check Python version
echo "📦 Checking Python version..."
python3 --version

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create logs directory
echo ""
echo "📁 Creating logs directory..."
mkdir -p logs

# Copy environment template
echo ""
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env created - PLEASE UPDATE WITH YOUR API KEYS!"
else
    echo "✅ .env already exists"
fi

echo ""
echo "================================"
echo "✨ SETUP COMPLETE!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: python fetch_tickets.py (test Zendesk)"
echo "3. Run: python analyze_ticket.py (test OpenAI)"
echo "4. Run: python ai_ticket_processor.py --limit 5"
echo ""
