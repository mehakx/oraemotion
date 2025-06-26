"""
ORA Empathic Agent - Manus.ai Style Implementation
Automatically executes real-world actions based on emotional context
Working Make.com integration for proactive agent capabilities
"""
import os
import json
import uuid
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Initialize OpenAI client
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

# Make.com webhook URLs (you'll need to set these up)
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

# Empathic Agent Functions - These trigger real Make.com workflows
class EmpathicAgent:
    
    @staticmethod
    def analyze_emotional_context(text, emotion, user_id):
        """Analyze context to determine what actions to take - Manus style"""
        
        context = {
            "text": text.lower(),
            "emotion": emotion.lower(),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "urgency": "normal"
        }
        
        # Determine urgency and action type
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
        """Execute real-world actions through Make.com - like Manus would"""
        
        actions_taken = []
        webhook_url = MAKE_WEBHOOKS.get(context["action_type"])
        
        if not webhook_url:
            print(f"⚠️ No webhook configured for {context['action_type']}")
            return actions_taken
        
        # Prepare action payload for Make.com
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
            # Send to Make.com webhook
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                actions_taken.append(f"✅ Triggered {context['action_type']} workflow")
                
                # Log the action
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
            print(f"❌ Webhook error: {e}")
            actions_taken.append(f"❌ Webhook error: {str(e)}")
        
        return actions_taken
    
    @staticmethod
    def get_action_plan(context):
        """Define specific actions for each emotional context - Manus style automation"""
        
        action_plans = {
            "crisis_intervention": [
                "immediate_emergency_contact",
                "crisis_hotline_info",
                "location_sharing_family",
                "emergency_calendar_clear",
                "crisis_resource_delivery",
                "professional_alert"
            ],
            
            "anxiety_support": [
                "breathing_exercise_start",
                "calming_music_play",
                "calendar_clear_next_hour", 
                "support_person_text",
                "anxiety_resources_send",
                "environment_adjust_lights",
                "meditation_app_open"
            ],
            
            "depression_care": [
                "gentle_check_in_schedule",
                "social_connection_facilitate",
                "mood_boosting_playlist",
                "therapy_session_suggest",
                "family_gentle_alert",
                "self_care_reminders",
                "positive_content_curate"
            ],
            
            "stress_intervention": [
                "calendar_optimization",
                "break_reminders_set",
                "stress_relief_resources",
                "workload_analysis",
                "relaxation_techniques",
                "environment_optimization"
            ],
            
            "wellness_check": [
                "mood_tracking_log",
                "wellness_score_update",
                "routine_optimization",
                "health_reminders"
            ]
        }
        
        return action_plans.get(context["action_type"], ["general_support"])
    
    @staticmethod
    def generate_empathic_response(emotion, text, actions_taken):
        """Generate empathic response that acknowledges actions taken"""
        
        # Base empathic responses
        empathic_responses = {
            "anxious": [
                "I can feel the anxiety in your words, and I want you to know you're not alone in this.",
                "Your nervous system is trying to protect you. Let's work through this together.",
                "I sense the tension you're carrying. You're safe here with me."
            ],
            "sad": [
                "I hear the pain in your voice, and I want you to know that your feelings are completely valid.",
                "There's a heaviness in what you're sharing. I'm here to sit with you through this.",
                "Your sadness matters, and so do you. Let's take this one moment at a time."
            ],
            "stressed": [
                "I can feel the pressure you're under. That sounds incredibly overwhelming.",
                "The stress you're experiencing is real and valid. Let's find ways to lighten this load.",
                "I sense how much you're juggling right now. You don't have to carry this alone."
            ],
            "angry": [
                "I can hear the intensity of your feelings. Something important to you has been affected.",
                "Your anger is telling us something significant. Let's explore what's underneath this.",
                "I feel the fire in your words. Your emotions are valid and deserve to be heard."
            ]
        }
        
        import random
        base_response = random.choice(empathic_responses.get(emotion.lower(), empathic_responses["sad"]))
        
        # Add action acknowledgment
        if actions_taken:
            action_text = f"\n\nI've also taken some immediate steps to support you: {', '.join(actions_taken)}"
            return base_response + action_text
        
        return base_response

def get_fallback_emotion(text):
    """Enhanced emotion detection"""
    text_lower = text.lower()
    
    # Crisis indicators
    if any(word in text_lower for word in ["suicide", "kill myself", "end it all", "hurt myself"]):
        return "Crisis"
    
    # Anxiety indicators
    if any(word in text_lower for word in ["anxious", "panic", "overwhelmed", "can't breathe", "racing heart"]):
        return "Anxious"
    
    # Depression indicators  
    if any(word in text_lower for word in ["depressed", "hopeless", "empty", "worthless", "alone"]):
        return "Sad"
    
    # Stress indicators
    if any(word in text_lower for word in ["stressed", "pressure", "too much", "overwhelmed", "deadline"]):
        return "Stressed"
    
    # Anger indicators
    if any(word in text_lower for word in ["angry", "furious", "frustrated", "mad", "rage"]):
        return "Angry"
    
    # Positive emotions
    if any(word in text_lower for word in ["happy", "excited", "great", "wonderful", "amazing"]):
        return "Happy"
    
    return "Neutral"

# Routes
@app.route("/")
def index():
    try:
        return render_template("index.html")
    except:
        return jsonify({"message": "ORA Empathic Agent - Ready", "status": "operational"})

@app.route("/admin")
def admin():
    try:
        return send_from_directory('.', 'enhanced_app.py')
    except:
        return jsonify({"error": "Enhanced interface not found"})

@app.route("/health")
def health_check():
    """Health check with agent status"""
    webhook_status = {name: bool(url) for name, url in MAKE_WEBHOOKS.items()}
    
    return jsonify({
        "status": "healthy",
        "service": "ora_empathic_agent",
        "openai_configured": OPENAI_AVAILABLE,
        "agent_capabilities": "manus_style_proactive",
        "make_webhooks_configured": webhook_status,
        "total_actions_taken": sum(len(actions) for actions in action_history.values()),
        "empathic_mode": "active"
    })

@app.route("/classify", methods=["POST"])
def classify():
    """Classify emotion with enhanced detection"""
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    
    if OPENAI_AVAILABLE and client:
        prompt = f"""Classify the primary emotion in this text. Consider crisis indicators, anxiety levels, and emotional intensity.

Text: "{text}"

Respond with one word: Crisis, Anxious, Sad, Stressed, Angry, Happy, or Neutral"""
        
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
            emotion = get_fallback_emotion(text)
            return jsonify({"emotion": emotion, "method": "fallback"})
    else:
        emotion = get_fallback_emotion(text)
        return jsonify({"emotion": emotion, "method": "fallback"})

@app.route("/respond", methods=["POST"])
def respond():
    """Generate empathic response AND execute proactive actions"""
    data = request.get_json()
    emotion = data.get("emotion", "Neutral")
    text = data.get("text", "")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    # Analyze emotional context (Manus-style)
    context = EmpathicAgent.analyze_emotional_context(text, emotion, user_id)
    
    # Execute proactive actions through Make.com
    actions_taken = EmpathicAgent.execute_proactive_actions(context)
    
    # Generate empathic response that acknowledges actions
    empathic_response = EmpathicAgent.generate_empathic_response(emotion, text, actions_taken)
    
    # Create conversation session
    chat_id = uuid.uuid4().hex
    conversations[chat_id] = [
        {"role": "system", "content": "You are ORA, an empathic AI agent with proactive capabilities."},
        {"role": "assistant", "content": empathic_response}
    ]
    
    return jsonify({
        "message": empathic_response,
        "chat_id": chat_id,
        "user_id": user_id,
        "emotion": emotion,
        "urgency": context["urgency"],
        "actions_taken": actions_taken,
        "action_type": context["action_type"],
        "proactive_agent": True,
        "manus_style": True,
        "empathic_mode": True,
        "timestamp": context["timestamp"]
    })

@app.route("/api/agent/status/<user_id>", methods=["GET"])
def agent_status(user_id):
    """Get agent action history for user"""
    user_actions = action_history.get(user_id, [])
    
    return jsonify({
        "user_id": user_id,
        "total_actions": len(user_actions),
        "recent_actions": user_actions[-5:],  # Last 5 actions
        "agent_active": True
    })

@app.route("/api/webhooks/test", methods=["POST"])
def test_webhooks():
    """Test all Make.com webhooks"""
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

if __name__ == "__main__":
    print("🚀 Starting ORA Empathic Agent (Manus Style)")
    print(f"🤖 OpenAI: {'Enabled' if OPENAI_AVAILABLE else 'Fallback mode'}")
    print("❤️ Empathy: Advanced emotional intelligence")
    print("🎯 Agent: Proactive action execution")
    print("🔗 Make.com: Webhook integration ready")
    print("📊 Webhooks configured:", sum(1 for url in MAKE_WEBHOOKS.values() if url))
    print("🌐 Ready for empathic proactive assistance")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)



