import os
import json
import requests
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Environment variables
HUME_API_KEY = os.getenv("HUME_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print(f"🚀 GROQ ULTRA-FAST SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")
print(f"GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")

# Initialize Groq client with better error handling
groq_client = None
groq_working = False

if GROQ_API_KEY:
    try:
        # Try importing and initializing Groq
        from groq import Groq
        
        # Initialize with minimal parameters to avoid compatibility issues
        groq_client = Groq(api_key=GROQ_API_KEY)
        
        # Test Groq connection
        test_response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": "Say 'working'"}],
            max_tokens=5,
            temperature=0.1
        )
        print(f"✅ Groq test successful: {test_response.choices[0].message.content}")
        groq_working = True
        
    except ImportError as e:
        print(f"❌ Groq import failed: {e}")
        groq_working = False
    except Exception as e:
        print(f"❌ Groq initialization failed: {e}")
        groq_working = False
else:
    print("❌ No Groq API key found")

# Ultra-fast response cache for instant replies
INSTANT_CACHE = {
    "hello": "Hey there! How are you doing?",
    "hi": "Hi! Great to see you!",
    "hey": "Hey! What's going on?",
    "how are you": "I'm doing great, thanks for asking! How about you?",
    "good morning": "Good morning! Hope you're having a wonderful day!",
    "good evening": "Good evening! How has your day been?",
    "thank you": "You're very welcome! Happy to help!",
    "thanks": "Of course! Anytime!",
    "what's up": "Not much, just here chatting with you! What's going on?",
    "2+2": "That's 4!",
    "what's 2+2": "2 plus 2 equals 4!",
    "what time is it": f"It's {datetime.now().strftime('%I:%M %p')} right now!",
    "what's the time": f"The time is {datetime.now().strftime('%I:%M %p')}!"
}

class UltraFastIntegration:
    def __init__(self, hume_api_key):
        self.hume_api_key = hume_api_key
        self.headers = {
            "X-Hume-Api-Key": hume_api_key,
            "Content-Type": "application/json"
        }
    
    def quick_emotion_detection(self, user_input):
        """Lightning-fast emotion detection using keywords only"""
        user_input_lower = user_input.lower()
        
        # Ultra-fast keyword matching
        if any(word in user_input_lower for word in ["sad", "down", "upset", "depressed", "terrible", "awful"]):
            return "sadness", 0.9
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "annoyed", "hate"]):
            return "anger", 0.8
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "stress"]):
            return "anxiety", 0.8
        elif any(word in user_input_lower for word in ["happy", "great", "awesome", "amazing", "excited", "wonderful"]):
            return "joy", 0.8
        elif any(word in user_input_lower for word in ["confused", "weird", "strange", "don't understand"]):
            return "confusion", 0.7
        else:
            return "neutral", 0.7
    
    def generate_ultra_fast_response(self, user_input, emotion, conversation_history=None):
        """Generate ultra-fast response using Groq or smart fallbacks"""
        
        start_time = time.time()
        
        # Check instant cache first (0ms response time)
        user_input_clean = user_input.lower().strip()
        for cached_phrase, cached_response in INSTANT_CACHE.items():
            if cached_phrase in user_input_clean:
                print(f"⚡ INSTANT CACHE HIT: {cached_phrase}")
                return cached_response, time.time() - start_time
        
        # Handle date/time questions instantly with current time
        if any(phrase in user_input_clean for phrase in ["time", "date", "what time is it", "current time"]):
            current_time = datetime.now()
            response = f"It's {current_time.strftime('%I:%M %p')} on {current_time.strftime('%A, %B %d')}. How can I help you?"
            return response, time.time() - start_time
        
        # Try Groq if available
        if groq_client and groq_working:
            try:
                # Ultra-optimized prompt for speed
                current_time = datetime.now()
                
                system_prompt = f"""You are ORA, a warm AI companion. Current time: {current_time.strftime('%I:%M %p, %A %B %d, %Y')}.

EMOTION: User seems {emotion}

RULES:
- Keep responses SHORT (1-2 sentences max)
- Be warm and natural
- Answer questions directly
- If they're sad/anxious, be supportive
- If they're happy, share their energy
- Be conversational, not formal

Examples:
- Sad: "I can hear that you're feeling down. I'm here for you - what's going on?"
- Happy: "I love hearing the joy in your voice! What's got you feeling so good?"
- Questions: Answer directly and warmly"""

                messages = [{"role": "system", "content": system_prompt}]
                
                # Only use last 2 messages for maximum speed
                if conversation_history:
                    recent = conversation_history[-2:]
                    for msg in recent:
                        if msg.get('role') in ['user', 'assistant']:
                            messages.append({"role": msg['role'], "content": msg['content']})
                
                messages.append({"role": "user", "content": user_input})
                
                # Ultra-fast Groq call
                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=60,
                    temperature=0.7,
                    top_p=0.9
                )
                
                response_text = response.choices[0].message.content.strip()
                processing_time = time.time() - start_time
                print(f"⚡ Groq response in {processing_time:.3f}s: {response_text}")
                return response_text, processing_time
                
            except Exception as e:
                print(f"❌ Groq error: {e}")
                print("🔄 Falling back to smart responses")
        
        # Smart fallback responses (still very fast)
        fallback_response = self.get_smart_fallback(user_input, emotion)
        return fallback_response, time.time() - start_time
    
    def get_smart_fallback(self, user_input, emotion):
        """Smart fallback responses that feel natural"""
        user_input_lower = user_input.lower()
        
        # Handle common questions intelligently
        if any(phrase in user_input_lower for phrase in ["who are you", "what are you"]):
            return "I'm ORA, your AI companion! I'm here to chat with you."
        elif any(phrase in user_input_lower for phrase in ["how are you"]):
            return "I'm doing great! How about you?"
        elif any(phrase in user_input_lower for phrase in ["what can you do", "help me"]):
            return "I can chat about anything on your mind! What would you like to talk about?"
        elif any(phrase in user_input_lower for phrase in ["tell me a joke", "joke"]):
            return "Why don't scientists trust atoms? Because they make up everything! What else can I help you with?"
        elif any(phrase in user_input_lower for phrase in ["how old are you", "age"]):
            return "I'm a pretty new AI, but I'm always learning! What about you?"
        elif "weather" in user_input_lower:
            return "I don't have access to current weather data, but you can check your weather app! Is there something specific you're planning?"
        elif any(word in user_input_lower for word in ["calculate", "math", "plus", "minus", "times", "divided"]):
            return "I'd be happy to help with math! What calculation do you need?"
        
        # Emotion-based responses
        if emotion == "sadness":
            return "I can hear that you're feeling down. I'm here for you - what's going on?"
        elif emotion == "anxiety":
            return "That sounds stressful. Want to talk about what's worrying you?"
        elif emotion == "anger":
            return "I can hear the frustration. That sounds really tough."
        elif emotion == "joy":
            return "I love hearing the happiness in your voice! What's got you feeling so good?"
        else:
            return "I'm here and listening. What's on your mind?"
    
    def text_to_speech_hume_optimized(self, text):
        """Optimized Hume TTS with better error handling"""
        
        if not self.hume_api_key:
            print("❌ No Hume API key")
            return None
        
        try:
            print(f"🔊 TTS: {text[:30]}...")
            
            # Keep text short for faster TTS
            if len(text) > 150:
                text = text[:147] + "..."
            
            tts_url = "https://api.hume.ai/v0/tts"
            payload = {
                "utterances": [
                    {
                        "text": text
                    }
                ]
            }
            
            # Faster timeout
            response = requests.post(
                tts_url, 
                headers=self.headers, 
                json=payload, 
                timeout=8
            )
            
            print(f"🔊 Hume TTS status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    if "generations" in response_data and response_data["generations"]:
                        generation = response_data["generations"][0]
                        
                        if "audio" in generation:
                            audio_data = generation["audio"]
                            print(f"✅ TTS success: {len(audio_data)} chars")
                            return audio_data
                        else:
                            print("❌ No 'audio' key in generation")
                    else:
                        print("❌ No 'generations' in response")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
            else:
                print(f"❌ TTS HTTP error: {response.status_code}")
            
            return None
                
        except requests.exceptions.Timeout:
            print("❌ TTS timeout")
            return None
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None

# Initialize ultra-fast integration
hume = UltraFastIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_ultra_fast_fixed",
        "groq_working": groq_working,
        "groq_key_exists": bool(GROQ_API_KEY),
        "hume_key_exists": bool(HUME_API_KEY),
        "current_time": datetime.now().isoformat(),
        "ai_provider": "Groq + Smart Fallbacks",
        "model": "llama3-8b-8192" if groq_working else "Smart Fallbacks",
        "target_response_time": "< 2 seconds",
        "features": [
            "instant_cache_responses",
            "smart_fallback_responses",
            "optimized_tts",
            "minimal_processing_delays"
        ]
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Ultra-fast voice conversation processing"""
    
    total_start_time = time.time()
    
    try:
        user_input = None
        conversation_history = []
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"⚡ ULTRA-FAST: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Lightning-fast emotion detection
        emotion, confidence = hume.quick_emotion_detection(user_input)
        print(f"🎭 Emotion: {emotion} ({confidence})")
        
        # Ultra-fast response generation
        response_text, ai_time = hume.generate_ultra_fast_response(
            user_input, emotion, conversation_history
        )
        
        print(f"💬 Response: {response_text}")
        print(f"⚡ AI generation time: {ai_time:.3f}s")
        
        # TTS generation
        tts_start = time.time()
        audio_data = hume.text_to_speech_hume_optimized(response_text)
        tts_time = time.time() - tts_start
        
        total_time = time.time() - total_start_time
        print(f"⚡ TTS time: {tts_time:.3f}s")
        print(f"⚡ TOTAL time: {total_time:.3f}s")
        
        if audio_data:
            return jsonify({
                "success": True,
                "response": response_text,
                "audio_response": audio_data,
                "emotion": emotion,
                "emotion_confidence": confidence,
                "processing_time": total_time,
                "ai_generation_time": ai_time,
                "tts_time": tts_time,
                "method": "ultra_fast_fixed",
                "ai_provider": "Groq + Smart Fallbacks",
                "groq_used": groq_working
            })
        else:
            return jsonify({
                "success": True,
                "response": response_text,
                "emotion": emotion,
                "emotion_confidence": confidence,
                "processing_time": total_time,
                "ai_generation_time": ai_time,
                "error": "Audio generation failed",
                "ai_provider": "Groq + Smart Fallbacks"
            })
        
    except Exception as e:
        print(f"❌ ULTRA-FAST ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting ULTRA-FAST ORA Backend (Fixed)...")
    print(f"⚡ AI Provider: {'Groq' if groq_working else 'Smart Fallbacks'}")
    print(f"🎯 Groq Status: {'✅ Working' if groq_working else '❌ Using Fallbacks'}")
    print(f"🎯 Target: < 2 seconds total response time")
    app.run(host="0.0.0.0", port=5000, debug=True)

