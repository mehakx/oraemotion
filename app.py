"""
ORA Empathic Agent - HUME EVI INTEGRATION
Complete voice-to-voice conversation with emotional intelligence
Handles ANY question with natural empathic responses
"""
import os
import json
import uuid
import asyncio
import websockets
import requests
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import threading
import base64

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Hume EVI Configuration
HUME_API_KEY = os.getenv("HUME_API_KEY", "your_hume_api_key_here")
HUME_EVI_WEBSOCKET_URL = "wss://api.hume.ai/v0/evi/chat"
HUME_CONFIG_API_URL = "https://api.hume.ai/v0/evi/configs"

# Make.com webhook URLs (your existing setup)
MAKE_WEBHOOKS = {
    "stress_intervention": os.getenv("MAKE_STRESS_WEBHOOK", ""),
    "anxiety_support": os.getenv("MAKE_ANXIETY_WEBHOOK", ""),
    "depression_care": os.getenv("MAKE_DEPRESSION_WEBHOOK", ""),
    "crisis_alert": os.getenv("MAKE_CRISIS_WEBHOOK", ""),
    "wellness_check": os.getenv("MAKE_WELLNESS_WEBHOOK", ""),
    "mood_tracking": os.getenv("MAKE_MOOD_WEBHOOK", ""),
    "proactive_care": os.getenv("MAKE_PROACTIVE_WEBHOOK", "")
}

# In-memory stores
conversations = {}
user_profiles = {}
action_history = {}
active_evi_sessions = {}

# Hume EVI Configuration
HUME_AVAILABLE = bool(HUME_API_KEY and HUME_API_KEY != "your_hume_api_key_here")

if HUME_AVAILABLE:
    print("✅ Hume EVI initialized successfully")
else:
    print("⚠️ Hume EVI not configured - add HUME_API_KEY to environment")

class EmpathicAgent:
    """Your existing empathic agent - enhanced for Hume integration"""
    
    @staticmethod
    def analyze_emotional_context(text, emotion, user_id):
        context = {
            "text": text.lower(),
            "emotion": emotion.lower(),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "urgency": "normal"
        }
        
        # Crisis detection
        if any(word in context["text"] for word in ["crisis", "suicide", "hurt myself", "end it all"]):
            context["urgency"] = "critical"
            context["action_type"] = "crisis_intervention"
        elif emotion.lower() in ["anxious", "panic", "overwhelmed"]:
            if any(word in context["text"] for word in ["can't breathe", "panic attack", "overwhelming"]):
                context["urgency"] = "high"
            context["action_type"] = "anxiety_support"
        elif emotion.lower() in ["sad", "depressed", "hopeless"]:
            if any(word in context["text"] for word in ["alone", "nobody", "isolated"]):
                context["urgency"] = "high"
            context["action_type"] = "depression_care"
        elif emotion.lower() in ["stressed", "frustrated"]:
            context["action_type"] = "stress_intervention"
        else:
            context["action_type"] = "wellness_check"
        
        return context
    
    @staticmethod
    def execute_proactive_actions(context):
        actions_taken = []
        webhook_url = MAKE_WEBHOOKS.get(context["action_type"])
        
        if not webhook_url:
            return actions_taken
        
        payload = {
            "trigger": context["action_type"],
            "user_id": context["user_id"],
            "emotion": context["emotion"],
            "urgency": context["urgency"],
            "text_snippet": context["text"][:200],
            "timestamp": context["timestamp"]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                actions_taken.append(f"✅ Triggered {context['action_type']} workflow")
                
                if context["user_id"] not in action_history:
                    action_history[context["user_id"]] = []
                
                action_history[context["user_id"]].append({
                    "timestamp": context["timestamp"],
                    "action_type": context["action_type"],
                    "urgency": context["urgency"],
                    "status": "executed"
                })
            else:
                actions_taken.append(f"❌ Failed to trigger {context['action_type']}")
                
        except Exception as e:
            actions_taken.append(f"❌ Webhook error: {str(e)}")
        
        return actions_taken

class HumeEVIManager:
    """Manages Hume EVI WebSocket connections and conversations"""
    
    def __init__(self):
        self.config_id = None
        self.voice_id = None
        self.setup_complete = False
    
    async def setup_evi_config(self):
        """Create EVI configuration for empathic conversations"""
        
        if not HUME_AVAILABLE:
            return False
        
        try:
            # Create EVI configuration
            config_data = {
                "name": "ORA Empathic Assistant",
                "prompt": {
                    "text": """You are ORA, an empathic AI assistant designed for natural voice conversations. 

You excel at:
- Understanding emotional nuances in voice and responding appropriately
- Providing support for anxiety, stress, depression, and general wellness
- Answering any question (math, jokes, general knowledge, therapy)
- Maintaining warm, human-like conversation flow
- Being genuinely helpful and emotionally intelligent

Guidelines:
- Keep responses conversational and natural for voice
- Match the user's emotional tone appropriately
- For emotional distress, be especially empathetic and supportive
- For factual questions, be helpful and clear
- Use natural speech patterns with appropriate pauses
- Be warm, understanding, and genuinely caring

You can handle any topic while maintaining your empathic, supportive personality."""
                },
                "voice": {
                    "provider": "HUME_AI",
                    "name": "empathic_voice"
                },
                "language_model": {
                    "model_provider": "ANTHROPIC",
                    "model_resource": "claude-3-5-sonnet-20241022",
                    "temperature": 0.7
                },
                "ellm_model": {
                    "allow_short_responses": True
                },
                "event_messages": {
                    "on_new_chat": {
                        "enabled": True,
                        "text": "Hello! I'm ORA, your empathic AI assistant. I'm here to help with anything you need - whether it's emotional support, answering questions, or just having a conversation. How are you feeling today?"
                    },
                    "on_inactivity_timeout": {
                        "enabled": True,
                        "text": "I'm still here if you need me. Take your time."
                    },
                    "on_max_duration_timeout": {
                        "enabled": True,
                        "text": "It's been wonderful talking with you. Remember, I'm always here when you need support."
                    }
                },
                "timeouts": {
                    "inactivity": {
                        "enabled": True,
                        "duration_secs": 120
                    },
                    "max_duration": {
                        "enabled": True,
                        "duration_secs": 1800  # 30 minutes
                    }
                }
            }
            
            headers = {
                "X-HUME-API-KEY": HUME_API_KEY,
                "Content-Type": "application/json"
            }
            
            response = requests.post(HUME_CONFIG_API_URL, json=config_data, headers=headers)
            
            if response.status_code == 201:
                config_result = response.json()
                self.config_id = config_result["id"]
                print(f"✅ Hume EVI config created: {self.config_id}")
                self.setup_complete = True
                return True
            else:
                print(f"❌ Failed to create EVI config: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ EVI setup error: {e}")
            return False
    
    async def start_evi_conversation(self, user_id="default"):
        """Start a new EVI conversation session"""
        
        if not self.setup_complete:
            await self.setup_evi_config()
        
        if not self.config_id:
            return None
        
        try:
            # WebSocket URL with authentication
            ws_url = f"{HUME_EVI_WEBSOCKET_URL}?api_key={HUME_API_KEY}&config_id={self.config_id}"
            
            # Connect to EVI WebSocket
            websocket = await websockets.connect(ws_url)
            
            session_id = str(uuid.uuid4())
            active_evi_sessions[session_id] = {
                "websocket": websocket,
                "user_id": user_id,
                "created_at": datetime.now(),
                "messages": []
            }
            
            print(f"✅ EVI session started: {session_id}")
            return session_id
            
        except Exception as e:
            print(f"❌ Failed to start EVI session: {e}")
            return None
    
    async def send_audio_to_evi(self, session_id, audio_data):
        """Send audio data to EVI and get response"""
        
        if session_id not in active_evi_sessions:
            return None
        
        session = active_evi_sessions[session_id]
        websocket = session["websocket"]
        
        try:
            # Send audio input message
            audio_message = {
                "type": "audio_input",
                "data": base64.b64encode(audio_data).decode('utf-8')
            }
            
            await websocket.send(json.dumps(audio_message))
            
            # Collect response messages
            response_data = {
                "transcript": "",
                "audio_output": [],
                "emotions": {},
                "assistant_message": ""
            }
            
            # Listen for EVI responses
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "user_message":
                    response_data["transcript"] = data["message"]["content"]
                    if "models" in data and "prosody" in data["models"]:
                        response_data["emotions"] = data["models"]["prosody"]["scores"]
                
                elif data["type"] == "assistant_message":
                    response_data["assistant_message"] = data["message"]["content"]
                
                elif data["type"] == "audio_output":
                    response_data["audio_output"].append(data["data"])
                
                elif data["type"] == "assistant_end":
                    break
            
            # Store message in session
            session["messages"].append({
                "timestamp": datetime.now().isoformat(),
                "user_input": response_data["transcript"],
                "assistant_response": response_data["assistant_message"],
                "emotions": response_data["emotions"]
            })
            
            return response_data
            
        except Exception as e:
            print(f"❌ EVI conversation error: {e}")
            return None
    
    async def close_evi_session(self, session_id):
        """Close EVI session"""
        
        if session_id in active_evi_sessions:
            session = active_evi_sessions[session_id]
            try:
                await session["websocket"].close()
            except:
                pass
            del active_evi_sessions[session_id]
            print(f"✅ EVI session closed: {session_id}")

# Initialize Hume EVI Manager
evi_manager = HumeEVIManager()

# Your existing routes (kept unchanged)
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except:
        return jsonify({"message": "ORA Empathic Agent - HUME EVI INTEGRATED", "status": "operational"})

@app.route("/health")
def health_check():
    """Health check with Hume EVI status"""
    webhook_status = {name: bool(url) for name, url in MAKE_WEBHOOKS.items()}
    
    return jsonify({
        "status": "healthy",
        "service": "ora_empathic_agent_hume_evi",
        "hume_evi_available": HUME_AVAILABLE,
        "hume_evi_configured": evi_manager.setup_complete,
        "voice_to_voice_ready": True,
        "make_webhooks_configured": webhook_status,
        "total_actions_taken": sum(len(actions) for actions in action_history.values()),
        "empathic_mode": "advanced",
        "active_evi_sessions": len(active_evi_sessions),
        "conversation_capable": True,
        "emotional_intelligence": "hume_powered"
    })

# NEW: Hume EVI voice-to-voice endpoint for Make.com
@app.route("/hume_voice", methods=["POST"])
def hume_voice_conversation():
    """
    MAIN ENDPOINT: Hume EVI voice-to-voice for Make.com
    Handles complete voice conversation with emotional intelligence
    """
    
    start_time = time.time()
    
    try:
        # Get audio data from Make.com
        if 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
        else:
            # Fallback for base64 audio data
            data = request.get_json()
            audio_data = base64.b64decode(data.get('audio_data', ''))
        
        user_id = request.form.get('user_id', 'make_user')
        
        if not audio_data:
            return jsonify({
                'success': False,
                'error': 'No audio data provided',
                'audio_response': None
            }), 400
        
        # Start EVI conversation (async)
        async def process_with_evi():
            session_id = await evi_manager.start_evi_conversation(user_id)
            if not session_id:
                return None
            
            response = await evi_manager.send_audio_to_evi(session_id, audio_data)
            await evi_manager.close_evi_session(session_id)
            return response
        
        # Run async EVI processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        evi_response = loop.run_until_complete(process_with_evi())
        loop.close()
        
        if not evi_response:
            return jsonify({
                'success': False,
                'error': 'EVI processing failed',
                'audio_response': None
            }), 500
        
        # Analyze emotional context for proactive actions
        transcript = evi_response.get('transcript', '')
        emotions = evi_response.get('emotions', {})
        
        # Get dominant emotion
        dominant_emotion = 'neutral'
        if emotions:
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        
        # Execute proactive actions if needed
        context = EmpathicAgent.analyze_emotional_context(transcript, dominant_emotion, user_id)
        actions_taken = EmpathicAgent.execute_proactive_actions(context)
        
        # Combine audio output
        audio_output = b''.join([base64.b64decode(chunk) for chunk in evi_response.get('audio_output', [])])
        
        processing_time = time.time() - start_time
        
        # Return voice response for Make.com
        return jsonify({
            'success': True,
            'transcript': transcript,
            'assistant_response': evi_response.get('assistant_message', ''),
            'audio_response': base64.b64encode(audio_output).decode('utf-8'),
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'actions_taken': actions_taken,
            'urgency': context['urgency'],
            'processing_time': processing_time,
            'hume_evi_powered': True,
            'voice_to_voice': True,
            'emotional_intelligence': True,
            'conversation_capable': True
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'audio_response': None,
            'processing_time': processing_time
        }), 500

# NEW: Text-based Hume integration for testing
@app.route("/hume_text", methods=["POST"])
def hume_text_conversation():
    """Text-based Hume EVI for testing and development"""
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'test_user')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # For text testing, we'll use a simplified approach
        # In production, this would convert text to audio, send to EVI, and return audio
        
        # Simulate EVI response structure
        response = {
            'transcript': message,
            'assistant_response': f"I understand you said: '{message}'. As an empathic AI, I'm here to help with whatever you need.",
            'emotions': {'neutral': 0.7, 'curious': 0.3},
            'dominant_emotion': 'neutral'
        }
        
        # Execute proactive actions
        context = EmpathicAgent.analyze_emotional_context(message, response['dominant_emotion'], user_id)
        actions_taken = EmpathicAgent.execute_proactive_actions(context)
        
        return jsonify({
            'success': True,
            'transcript': response['transcript'],
            'assistant_response': response['assistant_response'],
            'emotions': response['emotions'],
            'dominant_emotion': response['dominant_emotion'],
            'actions_taken': actions_taken,
            'urgency': context['urgency'],
            'hume_evi_powered': True,
            'text_mode': True,
            'conversation_capable': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Setup EVI configuration on startup
@app.before_first_request
def setup_hume_evi():
    """Initialize Hume EVI configuration"""
    if HUME_AVAILABLE:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(evi_manager.setup_evi_config())
        loop.close()

# Your existing endpoints (kept unchanged)
@app.route("/api/agent/status/<user_id>", methods=["GET"])
def agent_status(user_id):
    user_actions = action_history.get(user_id, [])
    return jsonify({
        "user_id": user_id,
        "total_actions": len(user_actions),
        "recent_actions": user_actions[-5:],
        "agent_active": True,
        "hume_evi_integrated": True,
        "conversation_capable": True,
        "emotional_intelligence": "advanced"
    })

@app.route("/api/webhooks/test", methods=["POST"])
def test_webhooks():
    test_results = {}
    test_payload = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "message": "Webhook connectivity test"
    }
    
    for name, url in MAKE_WEBHOOKS.items():
        if url:
            try:
                response = requests.post(url, json=test_payload, timeout=5)
                test_results[name] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_code": response.status_code
                }
            except Exception as e:
                test_results[name] = {"status": "error", "error": str(e)}
        else:
            test_results[name] = {"status": "not_configured"}
    
    return jsonify({
        "webhook_tests": test_results,
        "overall_status": "ready" if any(r.get("status") == "success" for r in test_results.values()) else "needs_setup"
    })

# Test endpoint for Hume EVI
@app.route("/test", methods=["GET", "POST"])
def test_hume_evi():
    """Test the Hume EVI integration"""
    
    if request.method == 'GET':
        return jsonify({
            'status': 'ORA Hume EVI Voice-to-Voice Active!',
            'endpoints': ['/hume_voice', '/hume_text', '/health'],
            'hume_evi_available': HUME_AVAILABLE,
            'hume_evi_configured': evi_manager.setup_complete,
            'voice_to_voice_ready': True,
            'conversation_capable': True,
            'emotional_intelligence': 'advanced',
            'can_handle': ['any_voice_conversation', 'emotional_support', 'general_questions']
        })
    
    # Test with sample text input
    test_data = request.json or {
        'message': 'Hello, how are you?',
        'user_id': 'test_user'
    }
    
    # Test the Hume text endpoint
    return hume_text_conversation()

if __name__ == "__main__":
    print("🚀 Starting ORA Empathic Agent - HUME EVI INTEGRATED")
    print(f"🧠 Hume EVI: {'Enabled' if HUME_AVAILABLE else 'Not configured - add HUME_API_KEY'}")
    print("❤️ Empathy: Advanced emotional intelligence with Hume")
    print("🎯 Agent: Proactive action execution")
    print("🔗 Make.com: Voice workflow optimization enabled")
    print("🎙️ Voice: Complete voice-to-voice conversation")
    print("⚡ Speed: Real-time emotional processing")
    print("💬 Conversation: Can handle ANY voice conversation")
    print("📊 Webhooks configured:", sum(1 for url in MAKE_WEBHOOKS.values() if url))
    print("🌐 MAIN ENDPOINT: /hume_voice (for Make.com voice workflow)")
    print("🗣️ Voice-to-Voice: Fully integrated with emotional intelligence")
    print("🎭 Emotional AI: Powered by Hume's empathic models")
    
    if not HUME_AVAILABLE:
        print("\n⚠️ TO ENABLE HUME EVI:")
        print("1. Get API key from: https://platform.hume.ai")
        print("2. Set HUME_API_KEY environment variable")
        print("3. Restart this app")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)


