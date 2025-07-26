import os
import json
import requests
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Environment variables
HUME_API_KEY = os.getenv("HUME_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
openai_client = None
if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ OpenAI client initialization failed: {e}")

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

# Quick response cache for common greetings only
QUICK_CACHE = {
    "hello": "Hey there! How are you doing?",
    "hi": "Hi! Great to see you!",
    "hey": "Hey! What's going on?",
    "good morning": "Good morning! Hope you're having a wonderful day!",
    "good evening": "Good evening! How has your day been?"
}

class FastEmpathicHumeIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_emotion_smart(self, user_input):
        """Smart emotion analysis - fast keywords + OpenAI for complex emotions"""
        user_input_lower = user_input.lower()
        
        # Quick keyword detection for obvious emotions
        if any(word in user_input_lower for word in ["sad", "down", "upset", "depressed", "crying", "terrible", "awful", "miserable"]):
            return {"sadness": 0.9}, "sadness", "The user is expressing sadness and needs empathetic support"
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "furious", "pissed", "annoyed", "hate"]):
            return {"anger": 0.8}, "anger", "The user is feeling angry or frustrated"
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "afraid", "stress", "panic"]):
            return {"anxiety": 0.8}, "anxiety", "The user is experiencing anxiety or worry"
        elif any(word in user_input_lower for word in ["happy", "great", "awesome", "amazing", "excited", "wonderful", "fantastic"]):
            return {"joy": 0.8}, "joy", "The user is feeling positive and happy"
        elif any(word in user_input_lower for word in ["confused", "weird", "strange", "don't understand", "lost"]):
            return {"confusion": 0.8}, "confusion", "The user is feeling confused or uncertain"
        
        # For complex emotions, use OpenAI quickly
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze emotion in this message. Return JSON: {\"emotion\": \"emotion_name\", \"confidence\": 0.8, \"context\": \"brief description\"}"
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    max_tokens=50,
                    temperature=0.1
                )
                
                emotion_data = json.loads(response.choices[0].message.content.strip())
                emotion_name = emotion_data.get("emotion", "neutral")
                confidence = emotion_data.get("confidence", 0.7)
                context = emotion_data.get("context", "")
                
                return {emotion_name: confidence}, emotion_name, context
                
            except Exception as e:
                print(f"OpenAI emotion analysis failed: {e}")
        
        # Default to neutral
        return {"neutral": 0.7}, "neutral", "The user is in a neutral emotional state"
    
    def generate_empathic_response(self, user_input, emotions, emotion_context, conversation_history=None):
        """Generate empathic response that actually addresses what the user said"""
        
        # Check for quick greetings first
        user_input_lower = user_input.lower().strip()
        for cached_input, cached_response in QUICK_CACHE.items():
            if user_input_lower == cached_input:
                print(f"⚡ Using cached response for: {cached_input}")
                return cached_response, "neutral", 0.7
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_confidence = dominant_emotion[1]
        
        try:
            if openai_client:
                # Empathic system prompt that prioritizes emotional understanding
                system_prompt = f"""You are ORA, a deeply empathetic AI companion who truly understands and responds to emotions.

EMOTIONAL CONTEXT:
- User's emotion: {emotion_name} (confidence: {emotion_confidence:.1f})
- Emotional context: {emotion_context}

CORE PRINCIPLES:
1. ALWAYS acknowledge their emotional state first if they're expressing feelings
2. Show genuine empathy and understanding
3. Answer their questions directly and helpfully
4. Be warm, caring, and conversational
5. Keep responses concise but meaningful (2-3 sentences)

EXAMPLES:
- If sad: "I can really hear the sadness in what you're sharing. That sounds really difficult. I'm here to listen - what's been weighing on you?"
- If anxious: "That sounds really stressful and overwhelming. It makes complete sense that you'd feel anxious about that. Want to talk through what's worrying you most?"
- If happy: "I love hearing the joy in your voice! That's wonderful news. What's got you feeling so good?"
- If asking questions: Answer directly while being warm and empathetic

Remember: Be genuinely caring and respond to what they're actually feeling and saying."""

                messages = [{"role": "system", "content": system_prompt}]
                
                # Add recent conversation history
                if conversation_history:
                    recent = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
                    for msg in recent:
                        if msg.get('role') in ['user', 'assistant']:
                            messages.append({"role": msg['role'], "content": msg['content']})
                
                messages.append({"role": "user", "content": user_input})
                
                # Generate empathic response
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=100,  # Balanced length
                    temperature=0.8,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                response_text = response.choices[0].message.content.strip()
                return response_text, emotion_name, emotion_confidence
                
        except Exception as e:
            print(f"❌ OpenAI response generation error: {e}")
        
        # Empathic fallback responses
        return self.get_empathic_fallback(user_input, emotion_name), emotion_name, emotion_confidence
    
    def get_empathic_fallback(self, user_input, emotion):
        """Empathic fallback responses that address emotions properly"""
        user_input_lower = user_input.lower()
        
        if emotion == "sadness":
            return "I can really hear the sadness in what you're sharing. That sounds really difficult, and I'm here to listen. What's been weighing on your heart?"
        elif emotion == "anxiety":
            return "That sounds really stressful and overwhelming. It makes complete sense that you'd feel anxious about that. Want to talk through what's worrying you most?"
        elif emotion == "anger":
            return "I can hear the frustration in your voice, and that's completely understandable. Sometimes things just feel overwhelming. What's been bothering you?"
        elif emotion == "joy":
            return "I love hearing the happiness in your voice! That's wonderful. What's got you feeling so good today?"
        elif emotion == "confusion":
            return "That does sound confusing and uncertain. It's totally normal to feel lost sometimes. What's been puzzling you?"
        elif any(phrase in user_input_lower for phrase in ["where are you from", "who are you", "what are you"]):
            return "I'm ORA, your AI companion designed to have meaningful conversations with you. I'm here to chat, listen, and help however I can!"
        elif any(phrase in user_input_lower for phrase in ["how are you"]):
            return "I'm doing great, thank you for asking! I'm here and ready to chat with you. How are you doing today?"
        else:
            return "I'm here and listening. Tell me more about what's on your mind - I'd love to understand better."
    
    def text_to_speech_hume_fast(self, text):
        """Optimized Hume TTS for speed"""
        
        if not self.api_key:
            return None
        
        try:
            # Truncate very long responses for faster TTS
            if len(text) > 200:
                text = text[:197] + "..."
            
            tts_url = "https://api.hume.ai/v0/tts"
            payload = {"utterances": [{"text": text}]}
            
            # Quick timeout for speed
            response = requests.post(tts_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if "generations" in response_data and len(response_data["generations"]) > 0:
                    generation = response_data["generations"][0]
                    if "audio" in generation:
                        return generation["audio"]
            
            print(f"Hume TTS error: {response.status_code}")
            return None
                
        except Exception as e:
            print(f"Hume TTS error: {e}")
            return None

# Initialize fast empathic Hume integration
hume = FastEmpathicHumeIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_fast_empathic_backend",
        "features": [
            "smart_emotion_detection",
            "empathic_responses", 
            "fast_processing",
            "contextual_understanding",
            "emotional_intelligence"
        ],
        "target_response_time": "< 3 seconds",
        "empathy_level": "high"
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Fast empathic voice conversation processing"""
    
    start_time = time.time()
    
    try:
        user_input = None
        conversation_history = []
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"💬 Processing: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Smart emotion analysis
        emotions, dominant_emotion, emotion_context = hume.analyze_emotion_smart(user_input)
        print(f"🎭 Detected emotion: {dominant_emotion} - {emotion_context}")
        
        # Generate empathic response
        response_text, detected_emotion, emotion_confidence = hume.generate_empathic_response(
            user_input, emotions, emotion_context, conversation_history
        )
        
        print(f"💝 Empathic response: {response_text}")
        
        # Generate audio
        audio_data = hume.text_to_speech_hume_fast(response_text)
        
        processing_time = time.time() - start_time
        print(f"⚡ Total processing time: {processing_time:.2f} seconds")
        
        if audio_data:
            return jsonify({
                "success": True,
                "response": response_text,
                "audio_response": audio_data,
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "processing_time": processing_time,
                "method": "fast_empathic"
            })
        else:
            return jsonify({
                "success": True,
                "response": response_text,
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "processing_time": processing_time,
                "error": "Audio generation failed"
            })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting Fast Empathic ORA Backend...")
    print("💝 Features: Smart Emotion Detection + Empathic Responses + Speed")
    app.run(host="0.0.0.0", port=5000, debug=True)



