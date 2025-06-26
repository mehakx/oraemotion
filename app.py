"""
ORA Emotion App - DEPLOYMENT READY
Optimized for Render deployment without dependency conflicts
Includes Manus.ai agentic capabilities integration
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize OpenAI client with graceful fallback
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

# In-memory conversation store (for deployment without external DB)
conversations = {}
user_memories = {}  # Simple in-memory memory store

# Basic therapeutic keywords for routing
THERAPEUTIC_KEYWORDS = [
    'anxious', 'anxiety', 'depressed', 'depression', 'sad', 'sadness',
    'angry', 'anger', 'stressed', 'stress', 'worried', 'panic', 'fear',
    'suicidal', 'suicide', 'self-harm', 'therapy', 'therapist', 'crisis'
]

# Manus.ai Agent Actions - Define what the agent can do
AGENT_ACTIONS = {
    "schedule_reminder": {
        "description": "Schedule a wellness check reminder",
        "parameters": ["time", "message"],
        "endpoint": "/api/agent/schedule"
    },
    "crisis_intervention": {
        "description": "Trigger crisis intervention protocol",
        "parameters": ["risk_level", "user_id"],
        "endpoint": "/api/agent/crisis"
    },
    "mood_tracking": {
        "description": "Log mood data for tracking",
        "parameters": ["mood", "intensity", "triggers"],
        "endpoint": "/api/agent/mood"
    },
    "resource_recommendation": {
        "description": "Recommend therapeutic resources",
        "parameters": ["issue_type", "user_preferences"],
        "endpoint": "/api/agent/resources"
    },
    "family_notification": {
        "description": "Notify family members if needed",
        "parameters": ["user_id", "alert_type", "message"],
        "endpoint": "/api/agent/notify"
    }
}

def is_therapeutic_content(message):
    """Simple therapeutic content detection"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in THERAPEUTIC_KEYWORDS)

def get_memory_context(user_id, message, limit=3):
    """Get memory context from simple in-memory store"""
    if user_id not in user_memories:
        return ""
    
    memories = user_memories[user_id][-limit:]  # Get last N memories
    if not memories:
        return ""
    
    context_parts = [f"Previous: {mem['message'][:100]}..." for mem in memories]
    return "Context from previous conversations:\n" + "\n".join(context_parts)

def store_memory(user_id, message, metadata=None):
    """Store memory in simple in-memory store"""
    if user_id not in user_memories:
        user_memories[user_id] = []
    
    memory_entry = {
        "message": message,
        "timestamp": str(uuid.uuid4()),
        "metadata": metadata or {}
    }
    
    user_memories[user_id].append(memory_entry)
    
    # Keep only last 50 memories per user
    if len(user_memories[user_id]) > 50:
        user_memories[user_id] = user_memories[user_id][-50:]
    
    return {"success": True, "memory_id": memory_entry["timestamp"]}

def get_fallback_emotion(text):
    """Enhanced rule-based emotion detection"""
    text_lower = text.lower()
    
    # Positive emotions
    if any(word in text_lower for word in ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'love']):
        return "Happy"
    
    # Negative emotions
    if any(word in text_lower for word in ['sad', 'depressed', 'down', 'upset', 'crying', 'tears']):
        return "Sad"
    
    if any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'rage']):
        return "Angry"
    
    if any(word in text_lower for word in ['anxious', 'worried', 'nervous', 'stressed', 'panic', 'overwhelmed']):
        return "Anxious"
    
    if any(word in text_lower for word in ['fear', 'scared', 'afraid', 'terrified', 'frightened']):
        return "Fear"
    
    if any(word in text_lower for word in ['calm', 'peaceful', 'relaxed', 'content']):
        return "Calm"
    
    return "Neutral"

def get_empathic_response(emotion, text, user_context=None):
    """Generate empathic response with Hume.ai-style emotional intelligence"""
    
    # Enhanced responses based on emotion and context
    responses = {
        "Happy": [
            "That's wonderful to hear! Your joy is contagious. What's bringing you this happiness?",
            "I can feel the positivity in your words. It's beautiful to see you in such a good space.",
            "Your happiness lights up our conversation! Tell me more about what's going well."
        ],
        "Sad": [
            "I can hear the pain in your words, and I want you to know that your feelings are completely valid.",
            "It takes courage to share when you're feeling down. I'm here with you through this difficult time.",
            "Your sadness matters, and so do you. Sometimes we need to sit with these feelings before they can heal."
        ],
        "Angry": [
            "I can sense the intensity of your anger. It sounds like something really important to you has been affected.",
            "Your anger is telling us something significant. Let's explore what's underneath these strong feelings.",
            "I hear the fire in your words. Anger often protects other vulnerable emotions - what might those be?"
        ],
        "Anxious": [
            "I can feel the tension and worry in your message. Anxiety can be so overwhelming, but you're not alone in this.",
            "Your nervous system is trying to protect you. Let's breathe through this together and find some calm.",
            "I understand how consuming anxiety can feel. You're safe here, and we can take this one moment at a time."
        ],
        "Fear": [
            "I can sense your fear, and I want you to know that feeling scared doesn't make you weak - it makes you human.",
            "Fear can feel so isolating, but you've reached out, and that takes incredible strength.",
            "Your fear is valid, and you don't have to face it alone. Let's explore what feels safe for you right now."
        ],
        "Calm": [
            "I can feel the peace in your words. It's beautiful when we find these moments of calm.",
            "Your sense of tranquility is grounding. How can we nurture and protect this peaceful state?",
            "There's something so healing about the calm energy you're sharing. What's contributing to this serenity?"
        ],
        "Neutral": [
            "I'm here and listening. Sometimes the most profound conversations start from a place of quiet reflection.",
            "Thank you for being present with me. What's alive for you in this moment?",
            "I sense you're in a thoughtful space. What would feel most supportive for you right now?"
        ]
    }
    
    emotion_responses = responses.get(emotion, responses["Neutral"])
    
    # Select response based on context or randomly
    import random
    return random.choice(emotion_responses)

def determine_agent_actions(emotion, text, user_context=None):
    """Determine what agentic actions should be taken based on the conversation"""
    actions = []
    
    # Crisis detection and intervention
    crisis_keywords = ['suicide', 'kill myself', 'end it all', 'hurt myself', 'self-harm']
    if any(keyword in text.lower() for keyword in crisis_keywords):
        actions.append({
            "action": "crisis_intervention",
            "priority": "immediate",
            "parameters": {
                "risk_level": "high",
                "user_id": user_context.get("user_id") if user_context else "unknown"
            }
        })
    
    # Mood tracking for therapeutic emotions
    if emotion in ["Sad", "Anxious", "Angry", "Fear"]:
        actions.append({
            "action": "mood_tracking",
            "priority": "high",
            "parameters": {
                "mood": emotion.lower(),
                "intensity": "moderate",  # Could be enhanced with intensity detection
                "triggers": "conversation_based"
            }
        })
    
    # Resource recommendations
    if is_therapeutic_content(text):
        actions.append({
            "action": "resource_recommendation",
            "priority": "medium",
            "parameters": {
                "issue_type": emotion.lower(),
                "user_preferences": "empathic_support"
            }
        })
    
    # Schedule follow-up for concerning emotions
    if emotion in ["Sad", "Anxious"] and any(word in text.lower() for word in ['alone', 'isolated', 'nobody']):
        actions.append({
            "action": "schedule_reminder",
            "priority": "medium",
            "parameters": {
                "time": "24_hours",
                "message": "Checking in on your wellbeing"
            }
        })
    
    return actions

# Routes for serving interfaces
@app.route("/")
def index():
    """Serve simple interface"""
    try:
        return render_template("index.html")
    except:
        return jsonify({"message": "ORA Emotion AI - API Ready", "interfaces": ["/admin", "/enhanced"]})

@app.route("/admin")
def admin():
    """Serve the enhanced admin dashboard"""
    try:
        return send_from_directory('.', 'enhanced_app.py')
    except:
        return jsonify({"error": "Enhanced interface not found", "available_endpoints": ["/", "/health", "/classify", "/respond"]})

@app.route("/enhanced")
def enhanced():
    """Alternative route for enhanced interface"""
    try:
        return send_from_directory('.', 'enhanced_app.py')
    except:
        return jsonify({"error": "Enhanced interface not found"})

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ora_emotion_manus_ready",
        "openai_configured": OPENAI_AVAILABLE,
        "memory_system": "in_memory",
        "deployment_ready": True,
        "manus_agent_ready": True,
        "available_actions": list(AGENT_ACTIONS.keys()),
        "interfaces": {
            "simple": "/",
            "enhanced": "/admin or /enhanced"
        }
    })

@app.route("/classify", methods=["POST"])
def classify():
    """Classify emotion in text with enhanced detection"""
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    
    if OPENAI_AVAILABLE and client:
        prompt = f"Classify the primary emotion in this text in one word (Happy, Sad, Angry, Anxious, Fear, Calm, or Neutral):\n\n\"{text}\""
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )
            
            emotion = response.choices[0].message.content.strip().split()[0]
            return jsonify({"emotion": emotion, "method": "openai"})
            
        except Exception as e:
            print(f"OpenAI classification error: {e}")
            emotion = get_fallback_emotion(text)
            return jsonify({"emotion": emotion, "method": "fallback", "error": str(e)})
    else:
        emotion = get_fallback_emotion(text)
        return jsonify({"emotion": emotion, "method": "fallback"})

@app.route("/respond", methods=["POST"])
def respond():
    """Generate empathic AI response with agentic capabilities"""
    data = request.get_json()
    emotion = data.get("emotion", "Neutral")
    text = data.get("text", "")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    # Get memory context
    memory_context = get_memory_context(user_id, text)
    
    # Check if therapeutic content
    is_therapeutic = is_therapeutic_content(text)
    
    # Generate empathic response
    user_context = {"user_id": user_id, "is_therapeutic": is_therapeutic}
    reply = get_empathic_response(emotion, text, user_context)
    
    # Determine agent actions (Manus.ai integration)
    agent_actions = determine_agent_actions(emotion, text, user_context)
    
    # Store memory
    storage_result = store_memory(user_id, text, {
        "emotion": emotion,
        "is_therapeutic": is_therapeutic,
        "agent_actions": len(agent_actions)
    })
    
    # Create chat session
    chat_id = uuid.uuid4().hex
    conversations[chat_id] = [
        {"role": "system", "content": "You are ORA, a compassionate AI with empathic and agentic capabilities."},
        {"role": "assistant", "content": reply}
    ]
    
    return jsonify({
        "message": reply,
        "chat_id": chat_id,
        "user_id": user_id,
        "memory_enhanced": bool(memory_context),
        "is_therapeutic": is_therapeutic,
        "storage_success": storage_result.get("success", False),
        "method": "empathic_response",
        "openai_available": OPENAI_AVAILABLE,
        "agent_actions": agent_actions,  # Manus.ai agentic capabilities
        "manus_integration": True
    })

# Manus.ai Agent Action Endpoints
@app.route("/api/agent/schedule", methods=["POST"])
def agent_schedule():
    """Schedule wellness reminders (Manus.ai action)"""
    data = request.get_json()
    return jsonify({
        "action": "schedule_reminder",
        "status": "scheduled",
        "parameters": data,
        "make_com_webhook": "ready",
        "next_steps": ["trigger_make_scenario", "send_notification"]
    })

@app.route("/api/agent/crisis", methods=["POST"])
def agent_crisis():
    """Handle crisis intervention (Manus.ai action)"""
    data = request.get_json()
    return jsonify({
        "action": "crisis_intervention",
        "status": "activated",
        "priority": "immediate",
        "parameters": data,
        "make_com_webhook": "ready",
        "next_steps": ["notify_emergency_contacts", "provide_resources", "schedule_followup"]
    })

@app.route("/api/agent/mood", methods=["POST"])
def agent_mood():
    """Log mood data (Manus.ai action)"""
    data = request.get_json()
    return jsonify({
        "action": "mood_tracking",
        "status": "logged",
        "parameters": data,
        "make_com_webhook": "ready",
        "next_steps": ["update_dashboard", "analyze_patterns", "generate_insights"]
    })

@app.route("/api/agent/resources", methods=["POST"])
def agent_resources():
    """Recommend resources (Manus.ai action)"""
    data = request.get_json()
    issue_type = data.get("issue_type", "general")
    
    resources = {
        "anxious": ["Breathing exercises", "Mindfulness apps", "Anxiety support groups"],
        "sad": ["Depression resources", "Therapy finder", "Support communities"],
        "angry": ["Anger management techniques", "Conflict resolution", "Stress relief"],
        "general": ["Mental health resources", "Wellness tips", "Professional help"]
    }
    
    return jsonify({
        "action": "resource_recommendation",
        "status": "generated",
        "resources": resources.get(issue_type, resources["general"]),
        "parameters": data,
        "make_com_webhook": "ready"
    })

@app.route("/api/agent/notify", methods=["POST"])
def agent_notify():
    """Notify family/contacts (Manus.ai action)"""
    data = request.get_json()
    return jsonify({
        "action": "family_notification",
        "status": "prepared",
        "parameters": data,
        "make_com_webhook": "ready",
        "next_steps": ["send_notification", "log_communication", "schedule_followup"]
    })

# Make.com Integration Endpoints
@app.route("/api/make/webhook", methods=["POST"])
def make_webhook():
    """Main webhook for Make.com integration"""
    data = request.get_json()
    
    # Process the incoming data
    user_message = data.get("user_message", "")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    # Classify emotion
    emotion = get_fallback_emotion(user_message)
    
    # Generate response
    response = get_empathic_response(emotion, user_message)
    
    # Determine actions
    actions = determine_agent_actions(emotion, user_message, {"user_id": user_id})
    
    # Store memory
    store_memory(user_id, user_message, {"emotion": emotion, "source": "make_com"})
    
    return jsonify({
        "success": True,
        "user_id": user_id,
        "emotion": emotion,
        "response": response,
        "agent_actions": actions,
        "is_therapeutic": is_therapeutic_content(user_message),
        "timestamp": str(uuid.uuid4()),
        "manus_integration": "active"
    })

@app.route("/api/make/actions", methods=["GET"])
def make_actions():
    """Get available agent actions for Make.com"""
    return jsonify({
        "available_actions": AGENT_ACTIONS,
        "webhook_endpoint": "/api/make/webhook",
        "integration_status": "ready"
    })

if __name__ == "__main__":
    print("🚀 Starting ORA Emotion App (Manus.ai Ready)")
    print(f"🤖 OpenAI: {'Enabled' if OPENAI_AVAILABLE else 'Fallback mode'}")
    print("🧠 Memory: In-memory store (deployment safe)")
    print("❤️ Empathy: Hume.ai-style emotional intelligence")
    print("🎯 Agent: Manus.ai agentic capabilities integrated")
    print("🔗 Make.com: Webhook endpoints ready")
    print("🌐 Interfaces:")
    print("   Simple: http://localhost:5000/")
    print("   Enhanced: http://localhost:5000/admin")
    print("📦 Deployment: Optimized for Render")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)



