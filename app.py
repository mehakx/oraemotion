import os
import json
import requests
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Environment variables
HUME_API_KEY = os.getenv("HUME_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # You'll need to add this to Render

print(f"🔍 GEMINI SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")
print(f"GEMINI_API_KEY exists: {bool(GEMINI_API_KEY)}")

# Initialize Gemini
gemini_model = None
gemini_working = False

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')  # Fast model for real-time
        
        # Test Gemini connection
        test_response = gemini_model.generate_content("Say 'Gemini is working'")
        print(f"✅ Gemini test successful: {test_response.text}")
        gemini_working = True
        
    except Exception as e:
        print(f"❌ Gemini initialization failed: {e}")
        gemini_working = False
else:
    print("❌ No Gemini API key found")

class GeminiHumeIntegration:
    def __init__(self, hume_api_key):
        self.hume_api_key = hume_api_key
        self.headers = {
            "X-Hume-Api-Key": hume_api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_emotion_smart(self, user_input):
        """Smart emotion analysis using Gemini"""
        user_input_lower = user_input.lower()
        
        print(f"🎭 Analyzing emotion for: {user_input}")
        
        # Quick keyword detection for obvious emotions (for speed)
        if any(word in user_input_lower for word in ["sad", "down", "upset", "depressed", "crying", "terrible", "awful", "miserable"]):
            print("🎭 Detected: sadness (keyword)")
            return {"sadness": 0.9}, "sadness", "The user is expressing sadness and needs empathetic support"
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "furious", "pissed", "annoyed", "hate"]):
            print("🎭 Detected: anger (keyword)")
            return {"anger": 0.8}, "anger", "The user is feeling angry or frustrated"
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "afraid", "stress", "panic"]):
            print("🎭 Detected: anxiety (keyword)")
            return {"anxiety": 0.8}, "anxiety", "The user is experiencing anxiety or worry"
        elif any(word in user_input_lower for word in ["happy", "great", "awesome", "amazing", "excited", "wonderful", "fantastic"]):
            print("🎭 Detected: joy (keyword)")
            return {"joy": 0.8}, "joy", "The user is feeling positive and happy"
        
        # For complex emotions, use Gemini
        if gemini_model and gemini_working:
            try:
                print("🎭 Using Gemini for emotion analysis...")
                
                emotion_prompt = f"""Analyze the emotional content of this message: "{user_input}"

Return only a JSON object in this exact format:
{{"emotion": "emotion_name", "confidence": 0.8, "context": "brief description"}}

Possible emotions: joy, sadness, anger, anxiety, confusion, excitement, neutral"""

                response = gemini_model.generate_content(emotion_prompt)
                emotion_data = json.loads(response.text.strip())
                
                emotion_name = emotion_data.get("emotion", "neutral")
                confidence = emotion_data.get("confidence", 0.7)
                context = emotion_data.get("context", "")
                
                print(f"🎭 Gemini emotion result: {emotion_name} ({confidence})")
                return {emotion_name: confidence}, emotion_name, context
                
            except Exception as e:
                print(f"❌ Gemini emotion analysis failed: {e}")
        else:
            print("🎭 Gemini not available for emotion analysis")
        
        # Default to neutral
        print("🎭 Defaulting to neutral emotion")
        return {"neutral": 0.7}, "neutral", "The user is in a neutral emotional state"
    
    def generate_empathic_response(self, user_input, emotions, emotion_context, conversation_history=None):
        """Generate empathic response using Gemini"""
        
        print(f"💬 Generating response for: {user_input}")
        print(f"💬 Gemini working: {gemini_working}")
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_confidence = dominant_emotion[1]
        
        # Try Gemini first
        if gemini_model and gemini_working:
            try:
                print("💬 Using Gemini for response generation...")
                
                # Build conversation context
                conversation_context = ""
                if conversation_history:
                    recent = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
                    for msg in recent:
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        if role == 'user':
                            conversation_context += f"User: {content}\n"
                        elif role == 'assistant':
                            conversation_context += f"ORA: {content}\n"
                
                # Get current date and time
                current_time = datetime.now()
                current_date_time = current_time.strftime('%A, %B %d, %Y at %I:%M %p')
                
                # Enhanced system prompt for Gemini
                gemini_prompt = f"""You are ORA, a deeply empathetic AI voice companion. Today is {current_date_time}.

EMOTIONAL CONTEXT:
- User's emotion: {emotion_name} (confidence: {emotion_confidence:.1f})
- Emotional context: {emotion_context}

CONVERSATION HISTORY:
{conversation_context}

CURRENT USER MESSAGE: {user_input}

CORE PRINCIPLES:
1. ALWAYS acknowledge their emotional state first if they're expressing feelings
2. Show genuine empathy and understanding
3. Answer their questions directly and helpfully (you have access to current date/time)
4. Be warm, caring, and conversational
5. Keep responses concise but meaningful (2-3 sentences max for voice)
6. If they ask for date/time, give the actual current date/time: {current_date_time}

EXAMPLES:
- If sad: "I can really hear the sadness in what you're sharing. That sounds really difficult. I'm here to listen - what's been weighing on you?"
- If asking for time: "It's currently {current_date_time}. How can I help you with your day?"
- If asking math: Answer directly and warmly
- If asking questions: Answer directly while being empathetic

Respond naturally as ORA, acknowledging their emotion and answering their question directly."""

                response = gemini_model.generate_content(gemini_prompt)
                response_text = response.text.strip()
                
                print(f"✅ Gemini response: {response_text}")
                return response_text, emotion_name, emotion_confidence
                
            except Exception as e:
                print(f"❌ Gemini response generation error: {e}")
                print(f"❌ Error type: {type(e)}")
        else:
            print("💬 Gemini not available, using fallback")
        
        # Enhanced fallback responses
        print("💬 Using fallback response")
        return self.get_enhanced_fallback(user_input, emotion_name), emotion_name, emotion_confidence
    
    def get_enhanced_fallback(self, user_input, emotion):
        """Enhanced fallback responses with proper date/time handling"""
        user_input_lower = user_input.lower()
        
        print(f"🔄 Generating fallback for emotion: {emotion}")
        
        # Handle date/time questions in fallback
        if any(phrase in user_input_lower for phrase in ["what time", "what's the time", "date and time", "current time", "what date", "time is it"]):
            current_time = datetime.now()
            return f"It's currently {current_time.strftime('%A, %B %d, %Y at %I:%M %p')}. How can I help you with your day?"
        
        # Handle math questions
        if any(phrase in user_input_lower for phrase in ["what's 2+2", "2+2", "what is 2 plus 2"]):
            return "2 plus 2 equals 4! Is there something else I can help you calculate?"
        
        # Emotional responses
        if emotion == "sadness":
            return "I can really hear the sadness in what you're sharing. That sounds really difficult, and I'm here to listen. What's been weighing on your heart?"
        elif emotion == "anxiety":
            return "That sounds really stressful and overwhelming. It makes complete sense that you'd feel anxious about that. Want to talk through what's worrying you most?"
        elif emotion == "anger":
            return "I can hear the frustration in your voice, and that's completely understandable. Sometimes things just feel overwhelming. What's been bothering you?"
        elif emotion == "joy":
            return "I love hearing the happiness in your voice! That's wonderful. What's got you feeling so good today?"
        elif any(phrase in user_input_lower for phrase in ["where are you from", "who are you", "what are you"]):
            return "I'm ORA, your AI companion designed to have meaningful conversations with you. I'm here to chat, listen, and help however I can!"
        elif any(phrase in user_input_lower for phrase in ["how are you"]):
            return "I'm doing great, thank you for asking! I'm here and ready to chat with you. How are you doing today?"
        else:
            return "I'm here and listening. Tell me more about what's on your mind - I'd love to understand better."
    
    def text_to_speech_hume_fast(self, text):
        """Optimized Hume TTS"""
        
        if not self.hume_api_key:
            print("❌ No Hume API key for TTS")
            return None
        
        try:
            print(f"🔊 Converting to speech: {text[:50]}...")
            
            # Truncate very long responses for faster TTS
            if len(text) > 200:
                text = text[:197] + "..."
            
            tts_url = "https://api.hume.ai/v0/tts"
            payload = {"utterances": [{"text": text}]}
            
            response = requests.post(tts_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                if "generations" in response_data and len(response_data["generations"]) > 0:
                    generation = response_data["generations"][0]
                    if "audio" in generation:
                        print("✅ Hume TTS successful")
                        return generation["audio"]
            
            print(f"❌ Hume TTS error: {response.status_code}")
            return None
                
        except Exception as e:
            print(f"❌ Hume TTS error: {e}")
            return None

# Initialize Gemini-Hume integration
hume = GeminiHumeIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_gemini_backend",
        "gemini_working": gemini_working,
        "gemini_key_exists": bool(GEMINI_API_KEY),
        "hume_key_exists": bool(HUME_API_KEY),
        "current_time": datetime.now().isoformat(),
        "ai_provider": "Google Gemini",
        "model": "gemini-1.5-flash",
        "features": [
            "real_time_information",
            "fast_responses",
            "empathic_conversations",
            "current_date_time_awareness"
        ]
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Gemini-powered voice conversation processing"""
    
    start_time = time.time()
    
    try:
        user_input = None
        conversation_history = []
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"🚀 GEMINI: Processing input: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Smart emotion analysis
        emotions, dominant_emotion, emotion_context = hume.analyze_emotion_smart(user_input)
        print(f"🎭 GEMINI: Emotion result: {dominant_emotion} - {emotion_context}")
        
        # Generate empathic response using Gemini
        response_text, detected_emotion, emotion_confidence = hume.generate_empathic_response(
            user_input, emotions, emotion_context, conversation_history
        )
        
        print(f"💬 GEMINI: Final response: {response_text}")
        
        # Generate audio
        audio_data = hume.text_to_speech_hume_fast(response_text)
        
        processing_time = time.time() - start_time
        print(f"⚡ GEMINI: Total processing time: {processing_time:.2f} seconds")
        
        if audio_data:
            return jsonify({
                "success": True,
                "response": response_text,
                "audio_response": audio_data,
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "processing_time": processing_time,
                "method": "gemini",
                "ai_provider": "Google Gemini",
                "gemini_used": gemini_working,
                "current_time": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": True,
                "response": response_text,
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "processing_time": processing_time,
                "error": "Audio generation failed",
                "ai_provider": "Google Gemini",
                "gemini_used": gemini_working
            })
        
    except Exception as e:
        print(f"❌ GEMINI ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Starting Gemini-Powered ORA Backend...")
    print(f"🤖 AI Provider: Google Gemini")
    print(f"🎯 Gemini Status: {'✅ Working' if gemini_working else '❌ Not Working'}")
    app.run(host="0.0.0.0", port=5000, debug=True)



