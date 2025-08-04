import os
import json
import asyncio
import websockets
import base64
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Environment variables
HUME_API_KEY = os.getenv("HUME_API_KEY")

print(f"🎭 HUME EVI PERSONALITY SYSTEM SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")

# Personality Templates for Hume EVI
PERSONALITY_TEMPLATES = {
    "practical": {
        "name": "The Practical Coach",
        "system_prompt": """You are ORA, The Practical Coach - a direct, solution-focused AI companion.

CORE PERSONALITY:
- Direct and action-oriented approach
- Solution-focused mindset
- Clear, practical communication style
- Provide specific, actionable steps
- Efficient and results-driven
- Supportive but straightforward

COMMUNICATION STYLE:
- Get straight to the point without unnecessary elaboration
- Provide clear, numbered steps when giving advice
- Focus on "what can we do about this?" rather than dwelling on problems
- Use phrases like "Here's what I suggest", "Let's tackle this", "The next step is"
- Be encouraging but maintain a practical tone
- Ask "What's the first thing you can do right now?"

RESPONSE GUIDELINES:
- Keep responses concise and actionable (2-3 sentences max)
- Always include at least one specific action item
- Acknowledge the situation briefly, then move to solutions
- End with encouragement or a clear next step
- Avoid lengthy emotional processing - focus on forward movement

EXAMPLE PHRASES:
- "Here's exactly what we can do about this:"
- "Let me give you some clear steps:"
- "The most practical approach is:"
- "What's the first thing you can tackle right now?"

Remember: You are The Practical Coach - be direct, solution-focused, and actionable in every response.""",
        
        "voice_settings": {
            "speed": 1.1,
            "clarity": "high"
        }
    },
    
    "empathetic": {
        "name": "The Empathetic Friend", 
        "system_prompt": """You are ORA, The Empathetic Friend - a warm, understanding AI companion.

CORE PERSONALITY:
- Deeply empathetic and emotionally aware
- Warm, nurturing communication style
- Always acknowledge feelings first before solutions
- Patient and understanding approach
- Create emotional safety and validation
- Gentle and caring presence

COMMUNICATION STYLE:
- Always acknowledge emotions before offering advice
- Use phrases like "I can really hear", "That sounds", "I understand how"
- Validate feelings completely and authentically
- Ask gentle, caring questions to explore emotions
- Show genuine concern and empathy
- Create emotional safety before practical advice

RESPONSE GUIDELINES:
- Start every response by acknowledging their emotional state
- Validate their feelings completely (never dismiss or minimize)
- Use warm, caring language throughout
- Ask gentle questions to understand their experience better
- Offer emotional support before practical solutions
- End with caring reassurance or emotional validation

EXAMPLE PHRASES:
- "I can really hear the [emotion] in what you're sharing"
- "That sounds incredibly difficult to go through"
- "Your feelings about this are completely valid and understandable"
- "I'm here to listen and support you through this"

Remember: You are The Empathetic Friend - prioritize emotional validation, warmth, and understanding in every response.""",
        
        "voice_settings": {
            "speed": 0.9,
            "warmth": "high"
        }
    },
    
    "wise": {
        "name": "The Wise Mentor",
        "system_prompt": """You are ORA, The Wise Mentor - a thoughtful, insightful AI companion.

CORE PERSONALITY:
- Thoughtful and reflective approach
- Ask insightful, open-ended questions
- Help users discover their own answers
- Patient and contemplative communication
- Wise, experienced perspective
- Guide through questioning rather than direct advice

COMMUNICATION STYLE:
- Ask thoughtful, open-ended questions to promote reflection
- Help users think through situations themselves
- Use phrases like "What do you think", "How does that feel", "What might be"
- Encourage self-reflection and inner wisdom
- Share gentle insights and perspectives when appropriate
- Guide discovery rather than giving direct answers

RESPONSE GUIDELINES:
- Acknowledge what they've shared thoughtfully
- Ask one meaningful question to explore deeper
- Offer gentle insights or alternative perspectives
- Encourage their own thinking and self-reflection
- End with a question that promotes self-discovery
- Keep responses contemplative but not overly long

EXAMPLE PHRASES:
- "What do you think might be at the heart of this?"
- "How does that sit with you when you really think about it?"
- "What would it look like if you approached this differently?"
- "What's your intuition telling you about this situation?"

Remember: You are The Wise Mentor - guide through thoughtful questions and help users discover their own wisdom.""",
        
        "voice_settings": {
            "speed": 0.8,
            "reflection": "high"
        }
    }
}

# Store active connections and their personalities
active_connections = {}

class HumeEVIConnection:
    def __init__(self, user_id, personality_type="empathetic", user_name=""):
        self.user_id = user_id
        self.personality_type = personality_type
        self.user_name = user_name
        self.websocket = None
        self.is_connected = False
        self.conversation_history = []
        
    async def connect_to_hume(self):
        """Connect to Hume EVI WebSocket"""
        if not HUME_API_KEY:
            print("❌ No Hume API key found")
            return False
            
        try:
            # Hume EVI WebSocket URL
            url = "wss://api.hume.ai/v0/evi/chat"
            
            # Headers for authentication
            headers = {
                "X-Hume-Api-Key": HUME_API_KEY
            }
            
            # Connect to Hume EVI
            self.websocket = await websockets.connect(url, extra_headers=headers)
            
            # Send initial configuration with personality
            await self.configure_personality()
            
            self.is_connected = True
            print(f"✅ Connected to Hume EVI for user {self.user_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Hume EVI: {e}")
            return False
    
    async def configure_personality(self):
        """Configure Hume EVI with personality settings"""
        personality = PERSONALITY_TEMPLATES.get(self.personality_type, PERSONALITY_TEMPLATES["empathetic"])
        
        # Create configuration message
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
        
        # Add user context if available
        if self.user_name:
            config_message["session_settings"]["context"] = {
                "user_name": self.user_name,
                "personality": personality["name"],
                "timestamp": datetime.now().isoformat()
            }
        
        await self.websocket.send(json.dumps(config_message))
        print(f"🎭 Configured Hume EVI with {personality['name']} personality")
    
    async def send_audio(self, audio_data):
        """Send audio data to Hume EVI"""
        if not self.is_connected or not self.websocket:
            return False
            
        try:
            # Prepare audio message for Hume EVI
            audio_message = {
                "type": "audio_input",
                "data": audio_data  # Base64 encoded audio
            }
            
            await self.websocket.send(json.dumps(audio_message))
            return True
            
        except Exception as e:
            print(f"❌ Error sending audio to Hume EVI: {e}")
            return False
    
    async def listen_for_responses(self, callback):
        """Listen for responses from Hume EVI"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await callback(data)
                
        except Exception as e:
            print(f"❌ Error listening to Hume EVI: {e}")
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from Hume EVI"""
        if self.websocket:
            await self.websocket.close()
        self.is_connected = False
        print(f"🔌 Disconnected Hume EVI for user {self.user_id}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to ORA'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"🔌 Client disconnected: {request.sid}")
    
    # Clean up Hume EVI connection if exists
    if request.sid in active_connections:
        connection = active_connections[request.sid]
        asyncio.run(connection.disconnect())
        del active_connections[request.sid]

@socketio.on('start_conversation')
def handle_start_conversation(data):
    """Initialize Hume EVI connection with personality"""
    try:
        user_id = request.sid
        personality_type = data.get('personality', 'empathetic')
        user_name = data.get('user_name', '')
        
        print(f"🎭 Starting conversation for {user_name} with {personality_type} personality")
        
        # Create Hume EVI connection
        connection = HumeEVIConnection(user_id, personality_type, user_name)
        active_connections[user_id] = connection
        
        # Connect to Hume EVI asynchronously
        async def connect_and_listen():
            success = await connection.connect_to_hume()
            if success:
                # Start listening for responses
                await connection.listen_for_responses(handle_hume_response)
            else:
                socketio.emit('error', {'message': 'Failed to connect to Hume EVI'}, room=user_id)
        
        # Run connection in background
        asyncio.run(connect_and_listen())
        
        emit('conversation_started', {
            'personality': PERSONALITY_TEMPLATES[personality_type]['name'],
            'status': 'Ready to talk'
        })
        
    except Exception as e:
        print(f"❌ Error starting conversation: {e}")
        emit('error', {'message': str(e)})

@socketio.on('send_audio')
def handle_send_audio(data):
    """Send audio data to Hume EVI"""
    try:
        user_id = request.sid
        audio_data = data.get('audio')  # Base64 encoded audio
        
        if user_id not in active_connections:
            emit('error', {'message': 'No active connection'})
            return
        
        connection = active_connections[user_id]
        
        # Send audio to Hume EVI asynchronously
        async def send_audio():
            success = await connection.send_audio(audio_data)
            if not success:
                socketio.emit('error', {'message': 'Failed to send audio'}, room=user_id)
        
        asyncio.run(send_audio())
        
    except Exception as e:
        print(f"❌ Error sending audio: {e}")
        emit('error', {'message': str(e)})

async def handle_hume_response(data):
    """Handle responses from Hume EVI"""
    try:
        message_type = data.get('type')
        
        if message_type == 'audio_output':
            # Audio response from Hume EVI
            audio_data = data.get('data')
            socketio.emit('audio_response', {'audio': audio_data})
            
        elif message_type == 'transcript':
            # Transcript of user speech
            transcript = data.get('text', '')
            socketio.emit('transcript', {'text': transcript})
            
        elif message_type == 'emotion_scores':
            # Emotion detection results
            emotions = data.get('emotions', {})
            socketio.emit('emotions', {'emotions': emotions})
            
        elif message_type == 'error':
            # Error from Hume EVI
            error_message = data.get('message', 'Unknown error')
            socketio.emit('error', {'message': f'Hume EVI error: {error_message}'})
            
    except Exception as e:
        print(f"❌ Error handling Hume response: {e}")

@socketio.on('change_personality')
def handle_change_personality(data):
    """Change personality for existing connection"""
    try:
        user_id = request.sid
        new_personality = data.get('personality', 'empathetic')
        
        if user_id not in active_connections:
            emit('error', {'message': 'No active connection'})
            return
        
        connection = active_connections[user_id]
        connection.personality_type = new_personality
        
        # Reconfigure Hume EVI with new personality
        async def reconfigure():
            await connection.configure_personality()
        
        asyncio.run(reconfigure())
        
        emit('personality_changed', {
            'personality': PERSONALITY_TEMPLATES[new_personality]['name'],
            'status': f'Switched to {PERSONALITY_TEMPLATES[new_personality]["name"]}'
        })
        
    except Exception as e:
        print(f"❌ Error changing personality: {e}")
        emit('error', {'message': str(e)})

@socketio.on('end_conversation')
def handle_end_conversation():
    """End conversation and disconnect from Hume EVI"""
    try:
        user_id = request.sid
        
        if user_id in active_connections:
            connection = active_connections[user_id]
            asyncio.run(connection.disconnect())
            del active_connections[user_id]
        
        emit('conversation_ended', {'status': 'Conversation ended'})
        
    except Exception as e:
        print(f"❌ Error ending conversation: {e}")
        emit('error', {'message': str(e)})

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "hume_api_key": bool(HUME_API_KEY),
        "active_connections": len(active_connections),
        "personalities": list(PERSONALITY_TEMPLATES.keys())
    })

if __name__ == '__main__':
    print(f"\n🎭 HUME EVI PERSONALITY SYSTEM READY!")
    print(f"🎙️ Direct Speech-to-Speech: Hume EVI")
    print(f"🎯 Personalities Available: {list(PERSONALITY_TEMPLATES.keys())}")
    print(f"⚡ WebSocket-based for real-time communication")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


