import os
import json
import asyncio
import base64
import logging
from datetime import datetime
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import websockets
import ssl

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

# Environment variables
HUME_API_KEY = os.getenv('HUME_API_KEY')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🎯 HUME EVI PERSONALITY SYSTEM SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")

# Personality Templates
PERSONALITY_TEMPLATES = {
    "practical": {
        "name": "The Practical Coach",
        "system_prompt": """You are ORA, The Practical Coach - a direct, solution-focused AI companion. 
        CORE PERSONALITY: Direct and action-oriented approach - Solution-focused mindset - Clear, practical communication style - Provide specific, actionable steps - Efficient and results-driven - Supportive but straightforward
        COMMUNICATION STYLE: Get straight to the point without unnecessary elaboration - Provide clear, numbered steps when giving advice - Focus on "what can we do about this?" rather than dwelling on problems - Use phrases like "Here's what I suggest", "Let's tackle this", "The next step is" - Be encouraging but maintain a practical tone - Ask "What's the first thing you can tackle right now?"
        RESPONSE GUIDELINES: Keep responses concise and actionable (2-3 sentences max) - Always include at least one specific action item - Acknowledge the situation briefly, then move to solutions - End with encouragement or a clear next step - Avoid lengthy emotional processing - focus on forward movement
        EXAMPLE PHRASES: "Here's exactly what we can do about this." - "Let me give you some clear steps." - "The most practical approach is..." - "What's the first thing you can tackle right now?"
        Remember: You are The Practical Coach - be direct, solution-focused, and actionable in every response.""",
        "voice_settings": {"speed": 1.1, "clarity": "high"}
    },
    "empathetic": {
        "name": "The Empathetic Friend", 
        "system_prompt": """You are ORA, The Empathetic Friend - a warm, understanding AI companion.
        CORE PERSONALITY: Deeply empathetic and emotionally aware - Warm, nurturing communication style - Always acknowledge feelings first before solutions - Patient and understanding approach - Create emotional safety and validation - Gentle and caring presence
        COMMUNICATION STYLE: Always acknowledge emotions before offering advice - Use phrases like "I can really hear", "That sounds", "I understand how" - Validate feelings completely and authentically - Ask gentle, caring questions to explore emotions - Show genuine concern and empathy - Create emotional safety before practical advice
        RESPONSE GUIDELINES: Start every response by acknowledging their emotional state - Validate their feelings completely (never dismiss or minimize) - Use warm, caring language throughout - Ask gentle questions to understand their experience better - Offer emotional support before practical solutions - End with caring reassurance or emotional validation
        EXAMPLE PHRASES: "I can really hear the [emotion] in what you're sharing" - "That sounds incredibly difficult to go through" - "Your feelings about this are completely valid and understandable" - "I'm here to listen and support you through this"
        Remember: You are The Empathetic Friend - prioritize emotional validation, warmth, and understanding in every response.""",
        "voice_settings": {"speed": 0.9, "warmth": "high"}
    },
    "wise": {
        "name": "The Wise Mentor",
        "system_prompt": """You are ORA, The Wise Mentor - a thoughtful, insightful AI companion.
        CORE PERSONALITY: Thoughtful and reflective approach - Ask insightful, open-ended questions - Help users discover their own answers - Patient and contemplative communication - Wise, experienced perspective - Guide through questioning rather than direct advice
        COMMUNICATION STYLE: Ask thoughtful, open-ended questions to promote reflection - Help users think through situations themselves - Use phrases like "What do you think", "How does that feel", "What might be" - Encourage self-reflection and inner wisdom - Share gentle insights and perspectives when appropriate - Guide discovery rather than giving direct answers
        RESPONSE GUIDELINES: Acknowledge what they've shared thoughtfully - Ask one meaningful question to explore deeper - Offer gentle insights or alternative perspectives - Encourage their own thinking and self-reflection - End with a question that promotes self-discovery - Keep responses contemplative but not overly long
        EXAMPLE PHRASES: "What do you think might be at the heart of this?" - "How does that sit with you when you really think about it?" - "What would it look like if you approached this differently?" - "What's your intuition telling you about this situation?"
        Remember: You are The Wise Mentor - guide through thoughtful questions and help users discover their own wisdom.""",
        "voice_settings": {"speed": 0.8, "reflection": "high"}
    }
}

# Store active connections and their personalities
active_connections = {}
user_personalities = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@app.route('/health')
def health_check():
    return {"status": "healthy", "hume_api_key": bool(HUME_API_KEY)}

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to ORA'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}")
    if request.sid in active_connections:
        del active_connections[request.sid]
    if request.sid in user_personalities:
        del user_personalities[request.sid]

@socketio.on('start_conversation')
def handle_start_conversation(data):
    try:
        personality_type = data.get('personality', 'empathetic')
        user_name = data.get('user_name', 'User')
        
        print(f"🎭 Starting conversation for {user_name} with {personality_type} personality")
        
        # Store user personality
        user_personalities[request.sid] = {
            'personality_type': personality_type,
            'user_name': user_name,
            'personality': PERSONALITY_TEMPLATES.get(personality_type, PERSONALITY_TEMPLATES['empathetic'])
        }
        
        # Start Hume EVI connection
        asyncio.create_task(start_hume_connection(request.sid, personality_type))
        
        emit('conversation_started', {
            'status': f'Ready to talk! You are speaking with {PERSONALITY_TEMPLATES[personality_type]["name"]}',
            'personality': personality_type
        })
        
    except Exception as e:
        print(f"❌ Error starting conversation: {e}")
        emit('error', {'message': f'Error starting conversation: {str(e)}'})

@socketio.on('send_audio')
def handle_send_audio(data):
    try:
        if request.sid not in user_personalities:
            emit('error', {'message': 'No active conversation. Please start a conversation first.'})
            return
            
        audio_data = data.get('audio')
        if not audio_data:
            emit('error', {'message': 'No audio data received'})
            return
            
        print(f"🎤 Received audio from {request.sid}")
        
        # Send audio to Hume EVI
        asyncio.create_task(send_audio_to_hume(request.sid, audio_data))
        
    except Exception as e:
        print(f"❌ Error handling audio: {e}")
        emit('error', {'message': f'Error processing audio: {str(e)}'})

@socketio.on('change_personality')
def handle_change_personality(data):
    try:
        personality_type = data.get('personality', 'empathetic')
        
        if request.sid in user_personalities:
            user_personalities[request.sid]['personality_type'] = personality_type
            user_personalities[request.sid]['personality'] = PERSONALITY_TEMPLATES.get(personality_type, PERSONALITY_TEMPLATES['empathetic'])
            
            print(f"🎭 Changed personality to {personality_type} for {request.sid}")
            
            # Restart Hume connection with new personality
            asyncio.create_task(start_hume_connection(request.sid, personality_type))
            
            emit('personality_changed', {
                'status': f'Switched to {PERSONALITY_TEMPLATES[personality_type]["name"]}',
                'personality': personality_type
            })
        else:
            emit('error', {'message': 'No active conversation to change personality'})
            
    except Exception as e:
        print(f"❌ Error changing personality: {e}")
        emit('error', {'message': f'Error changing personality: {str(e)}'})

async def start_hume_connection(session_id, personality_type):
    """Start Hume EVI WebSocket connection"""
    try:
        if not HUME_API_KEY:
            socketio.emit('error', {'message': 'No Hume API key found'}, room=session_id)
            return False
            
        personality = PERSONALITY_TEMPLATES.get(personality_type, PERSONALITY_TEMPLATES['empathetic'])
        
        # Hume EVI WebSocket URL
        hume_url = f"wss://api.hume.ai/v0/evi/chat?api_key={HUME_API_KEY}"
        
        # Headers for authentication
        headers = {
            "X-Hume-Api-Key": HUME_API_KEY
        }
        
        print(f"🔗 Connecting to Hume EVI for {session_id}")
        
        # Create SSL context
        ssl_context = ssl.create_default_context()
        
        async with websockets.connect(hume_url, extra_headers=headers, ssl=ssl_context) as websocket:
            # Store connection
            active_connections[session_id] = websocket
            
            # Send initial configuration with personality
            config_message = {
                "type": "session_settings",
                "session_settings": {
                    "system_prompt": personality["system_prompt"],
                    "language": "en",
                    "voice": {
                        "provider": "hume_ai",
                        "name": "default"
                    }
                }
            }
            
            await websocket.send(json.dumps(config_message))
            print(f"✅ Connected to Hume EVI for {session_id}")
            
            # Listen for responses
            await listen_for_hume_responses(websocket, session_id)
            
    except Exception as e:
        print(f"❌ Failed to connect to Hume EVI: {e}")
        socketio.emit('error', {'message': f'Failed to connect to Hume EVI: {str(e)}'}, room=session_id)
        return False

async def send_audio_to_hume(session_id, audio_data):
    """Send audio data to Hume EVI"""
    try:
        if session_id not in active_connections:
            socketio.emit('error', {'message': 'No active Hume connection'}, room=session_id)
            return
            
        websocket = active_connections[session_id]
        
        # Prepare audio message for Hume EVI
        audio_message = {
            "type": "audio_input",
            "data": audio_data
        }
        
        await websocket.send(json.dumps(audio_message))
        print(f"🎤 Sent audio to Hume EVI for {session_id}")
        
    except Exception as e:
        print(f"❌ Error sending audio to Hume: {e}")
        socketio.emit('error', {'message': f'Error sending audio to Hume: {str(e)}'}, room=session_id)

async def listen_for_hume_responses(websocket, session_id):
    """Listen for responses from Hume EVI"""
    try:
        async for message in websocket:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "audio_output":
                # Send audio response back to client
                audio_data = data.get("data")
                if audio_data:
                    socketio.emit('audio_response', {'audio': audio_data}, room=session_id)
                    print(f"🔊 Sent audio response to {session_id}")
                    
            elif message_type == "user_message":
                # Send transcript to client
                transcript = data.get("message", {}).get("content", "")
                if transcript:
                    socketio.emit('transcript', {'text': transcript}, room=session_id)
                    print(f"📝 Transcript: {transcript}")
                    
            elif message_type == "assistant_message":
                # Assistant response received
                response = data.get("message", {}).get("content", "")
                print(f"🤖 Assistant response: {response}")
                
            elif message_type == "emotion_scores":
                # Emotion detection results
                emotions = data.get("emotions", [])
                if emotions:
                    socketio.emit('emotions', {'emotions': emotions}, room=session_id)
                    print(f"😊 Emotions detected: {emotions}")
                    
            elif message_type == "error":
                # Handle Hume errors
                error_message = data.get("message", "Unknown error")
                socketio.emit('error', {'message': f'Hume error: {error_message}'}, room=session_id)
                print(f"❌ Hume error: {error_message}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 Hume connection closed for {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        print(f"❌ Error listening to Hume responses: {e}")
        socketio.emit('error', {'message': f'Error with Hume connection: {str(e)}'}, room=session_id)

if __name__ == '__main__':
    print("🚀 HUME EVI PERSONALITY SYSTEM READY!")
    print("Direct Speech-to-Speech: Hume EVI")
    print(f"Personalities Available: {list(PERSONALITY_TEMPLATES.keys())}")
    print("WebSocket-based for real-time communication")
    
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)



