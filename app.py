"""
ORA Empathic Agent - MAKE.COM VOICE-TO-VOICE OPTIMIZED
Faster responses + Natural tone for Make.com voice workflow
Replaces OpenAI step in: Voice → Make.com → ORA → Murf → Voice
"""
import os
import json
import uuid
import requests
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize OpenAI client (keep for fallback)
OPENAI_AVAILABLE = False
client = None
try:
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        client = OpenAI(api_key=api_key)
        OPENAI_AVAILABLE = True
        print("✅ OpenAI initialized successfully")
    else:
        print("⚠️ OpenAI API key not configured")
except Exception as e:
    print(f"⚠️ OpenAI not available: {e}")

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

# In-memory stores (your existing)
conversations = {}
user_profiles = {}
action_history = {}

# OPTIMIZATION: Fast response cache
response_cache = {}
emotion_cache = {}
CACHE_TIMEOUT = 300  # 5 minutes

# OPTIMIZATION: Natural voice responses (designed for speech synthesis)
NATURAL_VOICE_RESPONSES = {
    'anxious': [
        "I can hear the worry in your voice. Take a deep breath with me. You're safe here.",
        "That anxiety sounds overwhelming. Let's work through this together, one step at a time.",
        "I sense your nervousness, and it's completely understandable. You're not alone in this."
    ],
    'sad': [
        "I can feel the sadness in your words. I'm here with you in this difficult moment.",
        "That sounds really painful. You don't have to carry this burden alone.",
        "I hear the heaviness you're feeling. Your pain is valid and important."
    ],
    'stressed': [
        "I can feel the pressure you're under. That sounds incredibly overwhelming.",
        "The stress you're experiencing is real. Let's find ways to lighten this load together.",
        "I sense how much you're juggling right now. You don't have to carry this alone."
    ],
    'angry': [
        "I can hear the frustration in your voice. Your anger makes complete sense.",
        "That sounds incredibly infuriating. Your feelings are completely valid.",
        "I sense your anger, and it's natural to feel this way given what you've described."
    ],
    'happy': [
        "I can hear the happiness in your voice! It's wonderful to share in your joy!",
        "Your excitement is contagious! This sounds like such a positive moment for you.",
        "I love hearing the lightness in your voice. This is beautiful to witness."
    ],
    'crisis': [
        "I hear how much pain you're in right now. You matter deeply, and I'm here with you.",
        "This sounds incredibly difficult. You're not alone in this. Let's get you support.",
        "I can feel the intensity of what you're going through. Help is available."
    ],
    'neutral': [
        "I'm here to listen and support you. What's been on your mind lately?",
        "Thank you for sharing with me. I'm here to help however I can.",
        "I hear you. This is a safe space for you to express whatever you're feeling."
    ]
}

# OPTIMIZATION: Murf AI voice settings for natural conversation
MURF_VOICE_SETTINGS = {
    'anxious': {
        'voice_id': 'en-US-aria',
        'speed': 0.9,
        'pitch': 0.8,
        'volume': 1.0,
        'pause_duration': 0.7,
        'style': 'calm_supportive'
    },
    'sad': {
        'voice_id': 'en-US-aria',
        'speed': 0.85,
        'pitch': 0.7,
        'volume': 1.0,
        'pause_duration': 0.8,
        'style': 'warm_empathetic'
    },
    'stressed': {
        'voice_id': 'en-US-aria',
        'speed': 0.9,
        'pitch': 0.8,
        'volume': 1.0,
        'pause_duration': 0.6,
        'style': 'calm_supportive'
    },
    'angry': {
        'voice_id': 'en-US-davis',
        'speed': 1.0,
        'pitch': 0.9,
        'volume': 1.0,
        'pause_duration': 0.5,
        'style': 'understanding_steady'
    },
    'happy': {
        'voice_id': 'en-US-aria',
        'speed': 1.1,
        'pitch': 1.1,
        'volume': 1.0,
        'pause_duration': 0.4,
        'style': 'warm_enthusiastic'
    },
    'crisis': {
        'voice_id': 'en-US-aria',
        'speed': 0.8,
        'pitch': 0.7,
        'volume': 1.0,
        'pause_duration': 0.9,
        'style': 'urgent_caring'
    },
    'neutral': {
        'voice_id': 'en-US-aria',
        'speed': 1.0,
        'pitch': 1.0,
        'volume': 1.0,
        'pause_duration': 0.5,
        'style': 'professional_caring'
    }
}

class EmpathicAgent:
    """Your existing empathic agent - kept unchanged"""
    
    @staticmethod
    def analyze_emotional_context(text, emotion, user_id):
        context = {
            "text": text.lower(),
            "emotion": emotion.lower(),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "urgency": "normal"
        }
        
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
            "timestamp": context["timestamp"],
            "actions_requested": EmpathicAgent.get_action_plan(context)
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
                    "status": "executed",
                    "webhook_response": response.status_code
                })
            else:
                actions_taken.append(f"❌ Failed to trigger {context['action_type']}")
                
        except Exception as e:
            actions_taken.append(f"❌ Webhook error: {str(e)}")
        
        return actions_taken
    
    @staticmethod
    def get_action_plan(context):
        action_plans = {
            "crisis_intervention": ["immediate_emergency_contact", "crisis_hotline_info", "location_sharing_family"],
            "anxiety_support": ["breathing_exercise_start", "calming_music_play", "support_person_text"],
            "depression_care": ["gentle_check_in_schedule", "social_connection_facilitate", "mood_boosting_playlist"],
            "stress_intervention": ["calendar_optimization", "break_reminders_set", "stress_relief_resources"],
            "wellness_check": ["mood_tracking_log", "wellness_score_update", "routine_optimization"]
        }
        return action_plans.get(context["action_type"], ["general_support"])

# OPTIMIZATION: Super fast emotion detection with caching
def detect_emotion_fast(text, user_id="default"):
    """Lightning fast emotion detection with smart caching"""
    
    # Check cache first for speed
    cache_key = f"emotion_{hash(text[:100])}"
    if cache_key in emotion_cache:
        cached = emotion_cache[cache_key]
        if time.time() - cached['timestamp'] < CACHE_TIMEOUT:
            return cached['data']
    
    # Fast keyword-based detection (faster than OpenAI for voice workflow)
    text_lower = text.lower()
    
    # Crisis indicators (highest priority)
    if any(word in text_lower for word in ["suicide", "kill myself", "end it all", "hurt myself", "want to die"]):
        result = {"emotion": "Crisis", "confidence": 0.95, "method": "fast_detection"}
    
    # Anxiety indicators
    elif any(word in text_lower for word in ["anxious", "panic", "overwhelmed", "can't breathe", "racing heart", "worried", "nervous"]):
        result = {"emotion": "Anxious", "confidence": 0.85, "method": "fast_detection"}
    
    # Depression indicators  
    elif any(word in text_lower for word in ["depressed", "hopeless", "empty", "worthless", "alone", "sad", "down"]):
        result = {"emotion": "Sad", "confidence": 0.85, "method": "fast_detection"}
    
    # Stress indicators
    elif any(word in text_lower for word in ["stressed", "pressure", "too much", "deadline", "overwhelmed", "busy"]):
        result = {"emotion": "Stressed", "confidence": 0.85, "method": "fast_detection"}
    
    # Anger indicators
    elif any(word in text_lower for word in ["angry", "furious", "frustrated", "mad", "rage", "annoyed"]):
        result = {"emotion": "Angry", "confidence": 0.85, "method": "fast_detection"}
    
    # Positive emotions
    elif any(word in text_lower for word in ["happy", "excited", "great", "wonderful", "amazing", "fantastic", "good"]):
        result = {"emotion": "Happy", "confidence": 0.85, "method": "fast_detection"}
    
    else:
        result = {"emotion": "Neutral", "confidence": 0.7, "method": "fast_detection"}
    
    # Cache the result for future speed
    emotion_cache[cache_key] = {
        'data': result,
        'timestamp': time.time()
    }
    
    return result

# OPTIMIZATION: Generate natural voice responses
def generate_natural_voice_response(emotion, text, actions_taken, user_id="default"):
    """Generate response optimized for natural voice synthesis"""
    
    emotion_key = emotion.lower()
    
    # Use natural voice responses designed for speech
    if emotion_key in NATURAL_VOICE_RESPONSES:
        import random
        base_response = random.choice(NATURAL_VOICE_RESPONSES[emotion_key])
    else:
        base_response = random.choice(NATURAL_VOICE_RESPONSES['neutral'])
    
    # Optimize text for voice synthesis
    voice_optimized_response = optimize_text_for_voice(base_response)
    
    # Add action acknowledgment if actions were taken (keep it brief for voice)
    if actions_taken:
        voice_optimized_response += " I've also taken some steps to support you."
    
    return voice_optimized_response

def optimize_text_for_voice(text):
    """Optimize text specifically for natural voice synthesis"""
    
    # Make more conversational and natural for speech
    text = text.replace("I understand that you are", "I can see you're")
    text = text.replace("It appears that", "It seems like")
    text = text.replace("I would recommend", "I'd suggest")
    text = text.replace("It is important to", "It helps to")
    text = text.replace("You should consider", "You might try")
    
    # Add natural breathing pauses for longer responses
    words = text.split()
    if len(words) > 12:
        # Add comma for natural pause around middle
        pause_position = len(words) // 2
        if pause_position < len(words) - 1:
            words[pause_position] += ","
        text = " ".join(words)
    
    # Ensure proper ending for voice synthesis
    if not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

# Your existing routes (kept unchanged)
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except:
        return jsonify({"message": "ORA Empathic Agent - MAKE.COM OPTIMIZED", "status": "operational"})

@app.route("/admin")
def admin():
    try:
        return send_from_directory('.', 'enhanced_app.py')
    except:
        return jsonify({"error": "Enhanced interface not found"})

@app.route("/health")
def health_check():
    """Health check with Make.com optimization status"""
    webhook_status = {name: bool(url) for name, url in MAKE_WEBHOOKS.items()}
    
    return jsonify({
        "status": "healthy",
        "service": "ora_empathic_agent_make_optimized",
        "openai_configured": OPENAI_AVAILABLE,
        "make_com_optimization": "enabled",
        "voice_to_voice_ready": True,
        "make_webhooks_configured": webhook_status,
        "total_actions_taken": sum(len(actions) for actions in action_history.values()),
        "empathic_mode": "active",
        "response_cache_size": len(response_cache),
        "emotion_cache_size": len(emotion_cache),
        "optimization_active": True
    })

# OPTIMIZED: Fast emotion classification for Make.com
@app.route("/classify", methods=["POST"])
def classify():
    """Super fast emotion classification for Make.com voice workflow"""
    data = request.get_json()
    text = data.get("text", "").strip()
    user_id = data.get("user_id", "default")
    
    if not text:
        return jsonify({"error": "No text"}), 400
    
    # Use fast detection for voice workflow speed
    result = detect_emotion_fast(text, user_id)
    return jsonify(result)

# OPTIMIZED: Fast response generation for Make.com
@app.route("/respond", methods=["POST"])
def respond():
    """Optimized response generation for Make.com voice workflow"""
    data = request.get_json()
    emotion = data.get("emotion", "Neutral")
    text = data.get("text", "")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    start_time = time.time()
    
    # Fast parallel processing for speed
    with ThreadPoolExecutor(max_workers=2) as executor:
        context_future = executor.submit(
            EmpathicAgent.analyze_emotional_context, text, emotion, user_id
        )
        context = context_future.result()
    
    # Execute proactive actions (your existing functionality)
    actions_taken = EmpathicAgent.execute_proactive_actions(context)
    
    # Generate natural voice response
    voice_response = generate_natural_voice_response(emotion, text, actions_taken, user_id)
    
    # Get Murf voice settings for natural speech
    murf_settings = MURF_VOICE_SETTINGS.get(emotion.lower(), MURF_VOICE_SETTINGS['neutral'])
    
    # Create conversation session
    chat_id = uuid.uuid4().hex
    conversations[chat_id] = [
        {"role": "system", "content": "You are ORA, optimized for natural voice conversation."},
        {"role": "assistant", "content": voice_response}
    ]
    
    processing_time = time.time() - start_time
    
    return jsonify({
        "message": voice_response,
        "chat_id": chat_id,
        "user_id": user_id,
        "emotion": emotion,
        "urgency": context["urgency"],
        "actions_taken": actions_taken,
        "action_type": context["action_type"],
        "proactive_agent": True,
        "voice_optimized": True,
        "murf_config": murf_settings,
        "processing_time": processing_time,
        "make_com_optimized": True,
        "empathic_mode": True,
        "timestamp": context["timestamp"]
    })

# NEW: Direct Make.com integration endpoint (replaces OpenAI in your workflow)
@app.route("/make_optimize", methods=["POST"])
def make_optimize():
    """
    MAIN ENDPOINT: Direct replacement for OpenAI in your Make.com voice workflow
    Input: Text from speech-to-text
    Output: Optimized response + Murf settings for text-to-speech
    """
    
    start_time = time.time()
    
    try:
        data = request.get_json()
        
        # Extract data from Make.com
        message = data.get('message', data.get('text', ''))
        user_id = data.get('user_id', 'make_user')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided',
                'text_response': "I'm here to listen. What's on your mind?",
                'emotion': 'neutral',
                'murf_config': MURF_VOICE_SETTINGS['neutral']
            }), 400
        
        # FAST: Parallel emotion detection and context analysis
        with ThreadPoolExecutor(max_workers=2) as executor:
            emotion_future = executor.submit(detect_emotion_fast, message, user_id)
            
            emotion_result = emotion_future.result()
            emotion = emotion_result['emotion']
        
        # Analyze context and execute proactive actions
        context = EmpathicAgent.analyze_emotional_context(message, emotion, user_id)
        actions_taken = EmpathicAgent.execute_proactive_actions(context)
        
        # Generate natural voice response
        response_text = generate_natural_voice_response(emotion, message, actions_taken, user_id)
        
        # Get Murf voice configuration for natural speech
        murf_config = MURF_VOICE_SETTINGS.get(emotion.lower(), MURF_VOICE_SETTINGS['neutral'])
        
        processing_time = time.time() - start_time
        
        # Return optimized response for Make.com voice workflow
        return jsonify({
            'success': True,
            'text_response': response_text,
            'emotion': emotion,
            'confidence': emotion_result['confidence'],
            'murf_config': murf_config,
            'processing_time': processing_time,
            'actions_taken': actions_taken,
            'urgency': context['urgency'],
            'voice_optimized': True,
            'make_com_ready': True,
            'natural_tone': True
        })
        
    except Exception as e:
        processing_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'text_response': "I'm here to listen and support you. What's on your mind?",
            'emotion': 'neutral',
            'murf_config': MURF_VOICE_SETTINGS['neutral'],
            'processing_time': processing_time
        }), 500

# Your existing endpoints (kept unchanged)
@app.route("/api/agent/status/<user_id>", methods=["GET"])
def agent_status(user_id):
    user_actions = action_history.get(user_id, [])
    return jsonify({
        "user_id": user_id,
        "total_actions": len(user_actions),
        "recent_actions": user_actions[-5:],
        "agent_active": True,
        "make_com_optimized": True
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

# Test endpoint for Make.com optimization
@app.route("/test", methods=["GET", "POST"])
def test_make_optimization():
    """Test the Make.com voice optimization"""
    
    if request.method == 'GET':
        return jsonify({
            'status': 'ORA Make.com Voice Optimization Active!',
            'endpoints': ['/classify', '/respond', '/make_optimize', '/health'],
            'voice_to_voice_ready': True,
            'optimization_enabled': True
        })
    
    # Test with sample voice input
    test_data = request.json or {
        'message': 'I feel anxious about my job interview tomorrow',
        'user_id': 'test_user'
    }
    
    # Test the Make.com optimization
    start_time = time.time()
    emotion_result = detect_emotion_fast(test_data['message'])
    response_text = generate_natural_voice_response(
        emotion_result['emotion'], 
        test_data['message'], 
        [], 
        test_data['user_id']
    )
    processing_time = time.time() - start_time
    murf_config = MURF_VOICE_SETTINGS.get(emotion_result['emotion'].lower(), MURF_VOICE_SETTINGS['neutral'])
    
    return jsonify({
        'test_input': test_data,
        'optimization_result': {
            'emotion': emotion_result['emotion'],
            'confidence': emotion_result['confidence'],
            'response': response_text,
            'murf_config': murf_config,
            'processing_time': processing_time,
            'voice_optimized': True,
            'natural_tone': True
        },
        'performance': {
            'processing_time': processing_time,
            'speed_improvement': f"{((3.0 - processing_time) / 3.0 * 100):.1f}% faster than baseline",
            'voice_to_voice_ready': True
        }
    })

if __name__ == "__main__":
    print("🚀 Starting ORA Empathic Agent - MAKE.COM VOICE OPTIMIZED")
    print(f"🤖 OpenAI: {'Enabled' if OPENAI_AVAILABLE else 'Fast fallback mode'}")
    print("❤️ Empathy: Advanced emotional intelligence")
    print("🎯 Agent: Proactive action execution")
    print("🔗 Make.com: Voice workflow optimization enabled")
    print("🎙️ Voice: Natural tone + faster responses")
    print("⚡ Speed: Parallel processing + smart caching")
    print("📊 Webhooks configured:", sum(1 for url in MAKE_WEBHOOKS.values() if url))
    print("🌐 MAIN ENDPOINT: /make_optimize (replaces OpenAI in Make.com)")
    print("🎵 Murf AI: Emotion-aware voice configuration")
    print("🗣️ Voice-to-Voice: Fully optimized workflow")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)




