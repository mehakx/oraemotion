import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration
HUME_API_KEY = os.environ.get('HUME_API_KEY')

@app.route('/')
def index():
    """Serve the main voice interface"""
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    """Serve the onboarding page"""
    return render_template('onboarding.html')

@app.route('/api/hume-key')
def get_hume_key():
    """Provide Hume API key to frontend"""
    if not HUME_API_KEY:
        return jsonify({'error': 'Hume API key not configured'}), 500
    
    return jsonify({'api_key': HUME_API_KEY})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'hume_api_key_configured': bool(HUME_API_KEY)
    })

if __name__ == '__main__':
    print("🚀 SIMPLE HUME EVI SYSTEM STARTING...")
    print(f"HUME_API_KEY configured: {bool(HUME_API_KEY)}")
    print("✅ Ready to serve Hume EVI with official SDK!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)



