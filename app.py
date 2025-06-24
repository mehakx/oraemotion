"""
ORA Emotion App - FIXED for Deployment
Compatible with OpenAI >=1.33.0 and mem0ai
Graceful fallback if mem0ai fails
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with new API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Try to import mem0ai - graceful fallback if it fails
MEM0_AVAILABLE = False
try:
    from mem0 import Memory
    
    # Initialize mem0ai with simple config
    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "ora_memories",
                "embedding_model_dims": 1536,
                "host": "localhost",
                "port": 6333
            }
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
            }
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-small",
            }
        }
    }
    
    memory = Memory.from_config(config)
    MEM0_AVAILABLE = True
    print("✅ Mem0ai initialized successfully")
    
except Exception as e:
    print(f"⚠️ Mem0ai not available, running in basic mode: {e}")
    memory = None
    MEM0_AVAILABLE = False

# In-memory conversation store
conversations = {}

# Basic therapeutic keywords for routing
THERAPEUTIC_KEYWORDS = [
    'anxious', 'anxiety', 'depressed', 'depression', 'sad', 'sadness',
    'angry', 'anger', 'stressed', 'stress', 'worried', 'panic', 'fear',
    'suicidal', 'suicide', 'self-harm', 'therapy', 'therapist', 'crisis'
]

def is_therapeutic_content(message):
    """Simple therapeutic content detection"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in THERAPEUTIC_KEYWORDS)

def get_memory_context(user_id, message, limit=3):
    """Get memory context if available"""
    if not MEM0_AVAILABLE or not memory:
        return ""
    
    try:
        memories = memory.search(query=message, user_id=user_id, limit=limit)
        if not memories:
            return ""
        
        context_parts = []
        for mem in memories:
            content = mem.get("memory", "")
            if content:
                context_parts.append(f"Previous: {content}")
        
        if context_parts:
            return "Context from previous conversations:\n" + "\n".join(context_parts[:limit])
        return ""
    except Exception as e:
        print(f"Memory context error: {e}")
        return ""

def store_memory(user_id, message, metadata=None):
    """Store memory if available"""
    if not MEM0_AVAILABLE or not memory:
        return {"success": False, "reason": "mem0ai_not_available"}
    
    try:
        result = memory.add(
            messages=[{"role": "user", "content": message}],
            user_id=user_id,
            metadata=metadata or {}
        )
        return {"success": True, "memory_id": result.get("id")}
    except Exception as e:
        print(f"Memory storage error: {e}")
        return {"success": False, "error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ora_emotion_fixed",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "mem0ai_available": MEM0_AVAILABLE,
        "deployment_ready": True,
        "openai_version": ">=1.33.0"
    })

@app.route("/classify", methods=["POST"])
def classify():
    """Classify emotion in text"""
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text"}), 400
    
    prompt = f"Classify the primary emotion in this text in one word (e.g. Happy, Sad, Angry, Neutral):\n\n\"{text}\""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=5
        )
        
        emotion = response.choices[0].message.content.strip().split()[0]
        return jsonify({"emotion": emotion})
        
    except Exception as e:
        return jsonify({"error": str(e), "emotion": "neutral"}), 500

@app.route("/respond", methods=["POST"])
def respond():
    """Generate AI response with optional memory enhancement"""
    data = request.get_json()
    emotion = data.get("emotion", "Neutral")
    text = data.get("text", "")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    # Get memory context if available
    memory_context = get_memory_context(user_id, text)
    
    # Check if therapeutic content
    is_therapeutic = is_therapeutic_content(text)
    
    try:
        # Build prompt with optional memory context
        base_prompt = (
            f"You are a compassionate assistant. The user is feeling {emotion}. "
            f"They said: \"{text}\". Reply in one or two sentences showing empathy."
        )
        
        if memory_context:
            prompt = f"{memory_context}\n\n{base_prompt}"
        else:
            prompt = base_prompt
        
        # Add therapeutic guidance if needed
        if is_therapeutic:
            prompt += "\n\nNote: This appears to be therapeutic content. Respond with extra care and empathy."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=60
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Store memory if available
        storage_result = store_memory(user_id, text, {
            "emotion": emotion,
            "is_therapeutic": is_therapeutic
        })
        
        # Create chat session
        chat_id = uuid.uuid4().hex
        conversations[chat_id] = [
            {"role": "system", "content": "You are a compassionate assistant."},
            {"role": "assistant", "content": reply}
        ]
        
        return jsonify({
            "message": reply,
            "chat_id": chat_id,
            "user_id": user_id,
            "memory_enhanced": bool(memory_context),
            "is_therapeutic": is_therapeutic,
            "mem0ai_available": MEM0_AVAILABLE,
            "storage_success": storage_result.get("success", False)
        })
        
    except Exception as e:
        return jsonify({
            "message": "I'm here to support you. Could you tell me more about how you're feeling?",
            "error": str(e),
            "chat_id": uuid.uuid4().hex,
            "user_id": user_id
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Continue conversation"""
    data = request.get_json()
    chat_id = data.get("chat_id")
    user_msg = data.get("message", "").strip()
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    if not chat_id or chat_id not in conversations:
        return jsonify({"error": "Invalid chat_id"}), 400
    
    # Get memory context if available
    memory_context = get_memory_context(user_id, user_msg)
    
    try:
        # Build conversation with optional memory context
        conversation_messages = conversations[chat_id].copy()
        
        if memory_context:
            conversation_messages.insert(0, {
                "role": "system",
                "content": f"Previous context: {memory_context}"
            })
        
        conversation_messages.append({"role": "user", "content": user_msg})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
            temperature=0.7,
            max_tokens=60
        )
        
        assistant_msg = response.choices[0].message.content.strip()
        conversations[chat_id].append({"role": "user", "content": user_msg})
        conversations[chat_id].append({"role": "assistant", "content": assistant_msg})
        
        # Store conversation if mem0ai available
        storage_result = store_memory(user_id, user_msg, {"chat_id": chat_id})
        
        return jsonify({
            "reply": assistant_msg,
            "memory_enhanced": bool(memory_context),
            "storage_success": storage_result.get("success", False)
        })
        
    except Exception as e:
        return jsonify({
            "reply": "I'm here to help. Could you rephrase that?",
            "error": str(e)
        }), 500

# Make.com compatible endpoint
@app.route("/api/make/memory-enhanced", methods=["POST"])
def make_memory_enhanced():
    """Make.com endpoint with optional memory enhancement"""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("user_message")
    
    if not user_id or not user_message:
        return jsonify({"error": "user_id and user_message required"}), 400
    
    # Get context and store memory if available
    context = get_memory_context(user_id, user_message, 5)
    storage_result = store_memory(user_id, user_message, data.get("metadata", {}))
    
    return jsonify({
        "success": True,
        "memory_context": context,
        "has_memories": bool(context),
        "storage_result": storage_result,
        "mem0ai_available": MEM0_AVAILABLE,
        "is_therapeutic": is_therapeutic_content(user_message)
    })

# Basic API endpoints
@app.route("/api/memory/status", methods=["GET"])
def memory_status():
    """Check memory system status"""
    return jsonify({
        "mem0ai_available": MEM0_AVAILABLE,
        "service": "ora_emotion_fixed",
        "openai_version": ">=1.33.0"
    })

if __name__ == "__main__":
    print("🚀 Starting ORA Emotion App (Fixed Version)")
    print(f"🧠 Memory: {'Mem0ai enabled' if MEM0_AVAILABLE else 'Basic mode (no mem0ai)'}")
    print("✅ OpenAI: Compatible version (>=1.33.0)")
    print("📦 Deployment: Ready for Render/Heroku")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)


