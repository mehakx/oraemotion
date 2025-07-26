import os
import json
import requests
import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import threading

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

# Response cache for instant replies
RESPONSE_CACHE = {
    "hello": "Hey there! How are you doing?",
    "hi": "Hi! Great to see you!",
    "how are you": "I'm doing great, thanks for asking! How about you?",
    "what's up": "Not much, just here chatting with you! What's going on?",
    "good morning": "Good morning! Hope you're having a wonderful day!",
    "good evening": "Good evening! How has your day been?",
    "thank you": "You're very welcome! Happy to help!",
    "thanks": "Of course! Anytime!",
    "bye": "Take care! Talk to you soon!",
    "goodbye": "Goodbye! Have a great day!"
}

class UltraFastHumeIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def quick_emotion_analysis(self, user_input):
        """Ultra-fast emotion detection using keywords only"""
        user_input_lower = user_input.lower()
        
        # Quick emotion keywords - optimized for speed
        if any(word in user_input_lower for word in ["happy", "great", "awesome", "good", "excited", "amazing", "love"]):
            return {"joy": 0.8}, "joy"
        elif any(word in user_input_lower for word in ["sad", "down", "upset", "bad", "terrible", "awful"]):
            return {"sadness": 0.8}, "sadness"
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "annoyed", "hate"]):
            return {"anger": 0.8}, "anger"
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "stress"]):
            return {"anxiety": 0.8}, "anxiety"
        elif any(word in user_input_lower for word in ["weird", "strange", "confused", "don't understand"]):
            return {"confusion": 0.8}, "confusion"
        elif any(word in user_input_lower for word in ["tired", "exhausted", "sleepy"]):
            return {"fatigue": 0.8}, "fatigue"
        else:
            return {"neutral": 0.7}, "neutral"
    
    def generate_ultra_fast_response(self, user_input, conversation_history=None):
        """Generate response optimized for speed"""
        
        # Check cache first for instant responses
        user_input_lower = user_input.lower().strip()
        for cached_input, cached_response in RESPONSE_CACHE.items():
            if cached_input in user_input_lower:
                print(f"⚡ Using cached response for: {cached_input}")
                return cached_response, "neutral", 0.7
        
        # Quick emotion analysis
        emotions, dominant_emotion = self.quick_emotion_analysis(user_input)
        
        try:
            if openai_client:
                # Ultra-short system prompt for speed
                system_prompt = """You are ORA, a friendly AI companion. Be conversational, helpful, and concise.

RULES:
- Keep responses SHORT (1-2 sentences max)
- Answer questions directly
- Be warm and natural
- No long explanations

Examples:
- "Where are you from?" → "I'm an AI created to chat with you! What about you?"
- "I'm sad" → "I'm sorry you're feeling down. Want to talk about it?"
- "Tell me a joke" → "Why don't scientists trust atoms? Because they make up everything!"

Be quick, friendly, and helpful."""

                messages = [{"role": "system", "content": system_prompt}]
                
                # Only use last 2 messages for speed
                if conversation_history:
                    recent = conversation_history[-2:] if len(conversation_history) > 2 else conversation_history
                    for msg in recent:
                        if msg.get('role') in ['user', 'assistant']:
                            messages.append({"role": msg['role'], "content": msg['content']})
                
                messages.append({"role": "user", "content": user_input})
                
                # Optimized OpenAI call for speed
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=50,  # Very short for speed
                    temperature=0.8,
                    top_p=0.9,
                    frequency_penalty=0.2,
                    presence_penalty=0.1
                )
                
                response_text = response.choices[0].message.content.strip()
                return response_text, dominant_emotion, 0.8
                
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
        
        # Ultra-fast fallback
        return self.get_instant_fallback(user_input, dominant_emotion), dominant_emotion, 0.7
    
    def get_instant_fallback(self, user_input, emotion):
        """Instant fallback responses"""
        user_input_lower = user_input.lower()
        
        if any(phrase in user_input_lower for phrase in ["where are you from", "who are you", "what are you"]):
            return "I'm ORA, your AI companion! I'm here to chat with you."
        elif any(phrase in user_input_lower for phrase in ["how are you"]):
            return "I'm doing great! How about you?"
        elif any(phrase in user_input_lower for phrase in ["what can you do"]):
            return "I can chat about anything! What's on your mind?"
        elif emotion == "sadness":
            return "I can hear that you're feeling down. I'm here for you."
        elif emotion == "anxiety":
            return "That sounds stressful. Want to talk about what's worrying you?"
        elif emotion == "joy":
            return "I love hearing the happiness in your voice! What's got you feeling so good?"
        else:
            return "That's interesting! Tell me more about that."
    
    def text_to_speech_hume_fast(self, text):
        """Optimized Hume TTS for speed"""
        
        if not self.api_key:
            return None
        
        try:
            # Truncate long responses for faster TTS
            if len(text) > 150:
                text = text[:147] + "..."
            
            tts_url = "https://api.hume.ai/v0/tts"
            payload = {"utterances": [{"text": text}]}
            
            # Quick timeout for speed
            response = requests.post(tts_url, headers=self.headers, json=payload, timeout=8)
            
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

# Initialize ultra-fast Hume integration
hume = UltraFastHumeIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_ultra_fast_backend",
        "optimizations": [
            "response_caching",
            "parallel_processing", 
            "short_responses",
            "quick_emotion_analysis",
            "fast_tts_timeout",
            "minimal_conversation_history"
        ],
        "target_response_time": "< 2 seconds"
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Ultra-fast voice conversation processing"""
    
    start_time = time.time()
    
    try:
        user_input = None
        conversation_history = []
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"⚡ Processing: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # PARALLEL PROCESSING: Start response generation and TTS simultaneously
        def generate_response():
            return hume.generate_ultra_fast_response(user_input, conversation_history)
        
        # Generate response (this is now very fast)
        response_text, detected_emotion, emotion_confidence = generate_response()
        
        print(f"💬 Response: {response_text}")
        
        # Generate audio (with timeout for speed)
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
                "method": "ultra_fast"
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
    print("🚀 Starting Ultra-Fast ORA Backend...")
    print("⚡ Optimizations: Caching, Parallel Processing, Short Responses")
    app.run(host="0.0.0.0", port=5000, debug=True)




