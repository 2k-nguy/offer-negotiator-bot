from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
from neogiator_bot import NeogiatorBot, NegotiationStrategy
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize bot
bot = None
try:
    bot = NeogiatorBot()
except ValueError:
    print("Warning: OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_context', methods=['POST'])
def create_context():
    """Create a new negotiation context"""
    if not bot:
        return jsonify({"error": "Bot not initialized. Please set OPENAI_API_KEY."}), 500
    
    data = request.json
    required_fields = ['company_name', 'position', 'user_profile']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        context_id = bot.create_negotiation_context(
            company_name=data['company_name'],
            position=data['position'],
            user_profile=data['user_profile'],
            target_salary=data.get('target_salary'),
            target_benefits=data.get('target_benefits', []),
            deal_breakers=data.get('deal_breakers', [])
        )
        
        session['current_context'] = context_id
        return jsonify({"context_id": context_id, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_response', methods=['POST'])
def generate_response():
    """Generate a negotiation response"""
    if not bot:
        return jsonify({"error": "Bot not initialized"}), 500
    
    data = request.json
    context_id = data.get('context_id') or session.get('current_context')
    
    if not context_id:
        return jsonify({"error": "No active negotiation context"}), 400
    
    try:
        response = bot.generate_response(
            context_id=context_id,
            incoming_message=data['message'],
            offer_details=data.get('offer_details')
        )
        
        return jsonify({"response": response, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/negotiation_status', methods=['GET'])
def get_negotiation_status():
    """Get current negotiation status"""
    if not bot:
        return jsonify({"error": "Bot not initialized"}), 500
    
    context_id = request.args.get('context_id') or session.get('current_context')
    
    if not context_id:
        return jsonify({"error": "No active negotiation context"}), 400
    
    try:
        status = bot.get_negotiation_status(context_id)
        return jsonify(status)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update_strategy', methods=['POST'])
def update_strategy():
    """Update negotiation strategy"""
    if not bot:
        return jsonify({"error": "Bot not initialized"}), 500
    
    data = request.json
    context_id = data.get('context_id') or session.get('current_context')
    strategy = data.get('strategy')
    
    if not context_id or not strategy:
        return jsonify({"error": "Missing context_id or strategy"}), 400
    
    try:
        strategy_enum = NegotiationStrategy(strategy)
        bot.update_strategy(context_id, strategy_enum)
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get available negotiation strategies"""
    strategies = [
        {"value": strategy.value, "name": strategy.value.replace('_', ' ').title()}
        for strategy in NegotiationStrategy
    ]
    return jsonify(strategies)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
