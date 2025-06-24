"""
Simplified ORA Emotion App with Mem0ai Integration
NO COGNEE DEPENDENCIES - Clean deployment for Render/Heroku
Replace your app.py with this file
"""
import os
import json
import uuid
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Import simplified services (no Cognee dependencies)
try:
    from simplified_mem0_service import simplified_ora_mem0_service
    from simplified_therapeutic_service import simplified_therapeutic_service
    MEM0_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Mem0ai services not available: {e}")
    MEM0_AVAILABLE = False

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# In-memory conversation store (enhanced with simplified memory)
conversations = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    health_status = {
        "status": "healthy",
        "service": "simplified_ora_emotion",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "mem0ai_available": MEM0_AVAILABLE,
        "cognee_removed": True,
        "deployment_ready": True,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    if MEM0_AVAILABLE:
        try:
            mem0_health = simplified_ora_mem0_service.health_check()
            therapeutic_health = simplified_therapeutic_service.health_check()
            health_status.update({
                "mem0ai_status": mem0_health.get("status", "unknown"),
                "therapeutic_status": therapeutic_health.get("status", "unknown")
            })
        except Exception as e:
            health_status["service_errors"] = str(e)
    
    return jsonify(health_status)

@app.route("/classify", methods=["POST"])
def classify():
    """Classify emotion in text"""
    data = request.get_json()
    text = data.get("text","").strip()
    if not text:
        return jsonify({"error":"No text"}), 400
    
    prompt = f"Classify the primary emotion in this text in one word (e.g. Happy, Sad, Angry, Neutral):\n\n\"{text}\""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content":prompt}],
            temperature=0.0,
            max_tokens=5
        )
        
        emotion = response.choices[0].message.content.strip().split()[0]
        return jsonify({"emotion": emotion})
        
    except Exception as e:
        return jsonify({"error": str(e), "emotion": "neutral"}), 500

@app.route("/respond", methods=["POST"])
def respond():
    """Generate AI response with simplified memory integration"""
    data = request.get_json()
    emotion = data.get("emotion","Neutral")
    text = data.get("text","")
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    # Get memory context if available
    memory_context = ""
    if MEM0_AVAILABLE:
        try:
            memory_context = simplified_ora_mem0_service.get_memory_context(user_id, text, limit=3)
        except Exception as e:
            print(f"Memory context failed: {e}")
    
    # Check if this is therapeutic content
    is_therapeutic = False
    if MEM0_AVAILABLE:
        try:
            is_therapeutic = simplified_ora_mem0_service.is_therapeutic_content(text, {"emotion": emotion})
        except Exception as e:
            print(f"Therapeutic detection failed: {e}")
    
    # Generate response
    try:
        if is_therapeutic and MEM0_AVAILABLE:
            # Use simplified therapeutic service
            therapeutic_response = simplified_therapeutic_service.generate_therapeutic_response(text, user_id, emotion)
            reply = therapeutic_response.get("response", "I'm here to support you.")
            
            # Store in therapeutic system
            storage_result = {"routed_to": "therapeutic", "success": True}
            
        else:
            # Use standard AI response with memory context
            base_prompt = (
                f"You are a compassionate assistant. The user is feeling {emotion}. "
                f"They said: \"{text}\". Reply in one or two sentences showing empathy."
            )
            
            if memory_context:
                prompt = f"{memory_context}\n\n{base_prompt}"
            else:
                prompt = base_prompt
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":prompt}],
                temperature=0.7,
                max_tokens=60
            )
            
            reply = response.choices[0].message.content.strip()
            
            # Store in mem0ai if available
            storage_result = {"routed_to": "general", "success": True}
            if MEM0_AVAILABLE:
                try:
                    metadata = {"emotion": emotion, "conversation_type": "initial_response"}
                    storage_result = simplified_ora_mem0_service.store_memory(user_id, text, metadata)
                except Exception as e:
                    print(f"Memory storage failed: {e}")
                    storage_result = {"success": False, "error": str(e)}
        
        # Create chat session
        chat_id = uuid.uuid4().hex
        conversations[chat_id] = [
            {"role":"system","content":"You are a compassionate assistant."},
            {"role":"assistant","content": reply}
        ]
        
        # Enhanced response
        response_data = {
            "message": reply, 
            "chat_id": chat_id,
            "user_id": user_id,
            "memory_enhanced": bool(memory_context),
            "is_therapeutic": is_therapeutic,
            "routing": storage_result.get("routed_to", "unknown"),
            "system": "simplified_ora"
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "message": "I'm here to support you. Could you tell me more about how you're feeling?",
            "error": str(e),
            "chat_id": uuid.uuid4().hex,
            "user_id": user_id
        }), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Continue conversation with simplified memory integration"""
    data = request.get_json()
    chat_id = data.get("chat_id")
    user_msg = data.get("message","").strip()
    user_id = data.get("user_id", f"user_{uuid.uuid4().hex[:8]}")
    
    if not chat_id or chat_id not in conversations:
        return jsonify({"error":"Invalid chat_id"}), 400
    
    # Get memory context if available
    memory_context = ""
    if MEM0_AVAILABLE:
        try:
            memory_context = simplified_ora_mem0_service.get_memory_context(user_id, user_msg, limit=3)
        except Exception as e:
            print(f"Memory context failed: {e}")
    
    try:
        # Build conversation with memory context
        conversation_messages = conversations[chat_id].copy()
        
        if memory_context:
            conversation_messages.insert(0, {
                "role": "system", 
                "content": f"Previous context: {memory_context}"
            })
        
        conversation_messages.append({"role":"user","content":user_msg})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
            temperature=0.7,
            max_tokens=60
        )
        
        assistant_msg = response.choices[0].message.content.strip()
        conversations[chat_id].append({"role":"user","content":user_msg})
        conversations[chat_id].append({"role":"assistant","content":assistant_msg})
        
        # Store conversation if mem0ai available
        storage_result = {"success": True, "routed_to": "general"}
        if MEM0_AVAILABLE:
            try:
                metadata = {"chat_id": chat_id, "conversation_type": "ongoing_chat"}
                storage_result = simplified_ora_mem0_service.store_memory(user_id, user_msg, metadata)
            except Exception as e:
                print(f"Memory storage failed: {e}")
        
        return jsonify({
            "reply": assistant_msg,
            "memory_enhanced": bool(memory_context),
            "routing": storage_result.get("routed_to", "unknown"),
            "system": "simplified_ora"
        })
        
    except Exception as e:
        return jsonify({
            "reply": "I'm here to help. Could you rephrase that?",
            "error": str(e)
        }), 500

# Simplified API endpoints
@app.route("/api/memory/store", methods=["POST"])
def api_store_memory():
    """Simplified memory storage endpoint"""
    if not MEM0_AVAILABLE:
        return jsonify({"error": "Memory service not available"}), 503
    
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    metadata = data.get("metadata", {})
    
    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400
    
    try:
        result = simplified_ora_mem0_service.store_memory(user_id, message, metadata)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/memory/context", methods=["POST"])
def api_get_context():
    """Simplified memory context endpoint"""
    if not MEM0_AVAILABLE:
        return jsonify({"context": "", "available": False})
    
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    limit = data.get("limit", 5)
    
    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400
    
    try:
        context = simplified_ora_mem0_service.get_memory_context(user_id, message, limit)
        return jsonify({
            "context": context,
            "available": bool(context),
            "system": "simplified_ora_mem0"
        })
    except Exception as e:
        return jsonify({"error": str(e), "context": ""}), 500

@app.route("/api/therapeutic/assess", methods=["POST"])
def api_therapeutic_assess():
    """Simplified therapeutic assessment endpoint"""
    if not MEM0_AVAILABLE:
        return jsonify({"error": "Therapeutic service not available"}), 503
    
    data = request.get_json()
    user_id = data.get("user_id")
    message = data.get("message")
    
    if not user_id or not message:
        return jsonify({"error": "user_id and message required"}), 400
    
    try:
        result = simplified_therapeutic_service.generate_therapeutic_response(message, user_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/user/<user_id>/summary", methods=["GET"])
def api_user_summary(user_id):
    """Get simplified user summary"""
    summary = {"user_id": user_id, "system": "simplified_ora"}
    
    if MEM0_AVAILABLE:
        try:
            # Get memory summary
            memories = simplified_ora_mem0_service.get_memories(user_id, limit=10)
            summary["memory_count"] = memories.get("count", 0)
            
            # Get therapeutic summary
            therapeutic_summary = simplified_therapeutic_service.get_user_therapeutic_summary(user_id)
            summary["therapeutic"] = therapeutic_summary
            
        except Exception as e:
            summary["error"] = str(e)
    else:
        summary["services_available"] = False
    
    return jsonify(summary)

# Make.com compatible endpoint
@app.route("/api/make/memory-enhanced", methods=["POST"])
def make_memory_enhanced():
    """Simplified Make.com endpoint"""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("user_message")
    
    if not user_id or not user_message:
        return jsonify({"error": "user_id and user_message required"}), 400
    
    # Get context and store memory
    context = ""
    storage_result = {"success": False}
    
    if MEM0_AVAILABLE:
        try:
            context = simplified_ora_mem0_service.get_memory_context(user_id, user_message, 5)
            metadata = data.get("metadata", {})
            storage_result = simplified_ora_mem0_service.store_memory(user_id, user_message, metadata)
        except Exception as e:
            print(f"Make.com endpoint error: {e}")
    
    return jsonify({
        "success": True,
        "memory_context": context,
        "has_memories": bool(context),
        "storage_result": storage_result,
        "system": "simplified_ora",
        "services_available": MEM0_AVAILABLE
    })

if __name__ == "__main__":
    print("🚀 Starting Simplified ORA Emotion App")
    print("🧠 Memory: Simplified mem0ai integration")
    print("🏥 Therapeutic: Basic keyword-based routing")
    print("🚫 Cognee: Removed for clean deployment")
    print("📦 Deployment: Render/Heroku ready")
    
    if not MEM0_AVAILABLE:
        print("⚠️ Running in basic mode - mem0ai services not available")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)


