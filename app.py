import os
from flask import Flask, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")

# Environment variables
HUME_API_KEY = os.getenv('HUME_API_KEY')

print("🎯 SIMPLE HUME EVI SYSTEM:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@app.route('/api/hume-key')
def get_hume_key():
    """Provide Hume API key to frontend"""
    return {"hume_api_key": HUME_API_KEY}

@app.route('/health')
def health_check():
    return {"status": "healthy", "hume_api_key": bool(HUME_API_KEY)}

if __name__ == '__main__':
    print("🚀 SIMPLE HUME EVI SYSTEM READY!")
    print("Frontend connects directly to Hume EVI")
    print("Continuous speech-to-speech conversation")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

