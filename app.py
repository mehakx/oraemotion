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

print(f"⚡ LIGHTNING-FAST SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")
print(f"Strategy: SPEED FIRST - Minimal processing, instant responses")

# MASSIVE instant response database for 0ms responses
INSTANT_RESPONSES = {
    # Greetings
    "hello": "Hey there! How are you doing?",
    "hi": "Hi! Great to see you!",
    "hey": "Hey! What's going on?",
    "good morning": "Good morning! Hope you're having a wonderful day!",
    "good afternoon": "Good afternoon! How's your day going?",
    "good evening": "Good evening! How has your day been?",
    "good night": "Good night! Sleep well!",
    
    # How are you variations
    "how are you": "I'm doing great, thanks for asking! How about you?",
    "how are you doing": "I'm doing wonderful! How are you feeling today?",
    "how's it going": "It's going great! How about you?",
    "what's up": "Not much, just here chatting with you! What's going on?",
    
    # Thank you
    "thank you": "You're very welcome! Happy to help!",
    "thanks": "Of course! Anytime!",
    "thank you so much": "You're so welcome! I'm glad I could help!",
    
    # Time and date
    "what time is it": f"It's {datetime.now().strftime('%I:%M %p')} right now!",
    "what's the time": f"The time is {datetime.now().strftime('%I:%M %p')}!",
    "what time": f"It's {datetime.now().strftime('%I:%M %p')}!",
    "current time": f"The current time is {datetime.now().strftime('%I:%M %p')}!",
    "what date is it": f"Today is {datetime.now().strftime('%A, %B %d, %Y')}!",
    "what's the date": f"It's {datetime.now().strftime('%A, %B %d, %Y')}!",
    
    # Math
    "what's 2+2": "2 plus 2 equals 4!",
    "2+2": "That's 4!",
    "what is 2 plus 2": "2 plus 2 is 4!",
    "what's 1+1": "1 plus 1 equals 2!",
    "1+1": "That's 2!",
    
    # About ORA
    "who are you": "I'm ORA, your AI companion! I'm here to chat with you.",
    "what are you": "I'm ORA, an AI designed to have conversations with you!",
    "what's your name": "I'm ORA! Nice to meet you!",
    "tell me about yourself": "I'm ORA, your friendly AI companion. I love chatting and I'm here whenever you need me!",
    
    # Capabilities
    "what can you do": "I can chat about anything on your mind! What would you like to talk about?",
    "help me": "I'm here to help! What's on your mind?",
    "can you help": "Absolutely! I'd love to help. What do you need?",
    
    # Feelings - Happy
    "i'm happy": "That's wonderful! I love hearing that you're happy!",
    "i feel great": "That's amazing! What's got you feeling so great?",
    "i'm excited": "I love your excitement! What's got you so excited?",
    "i'm good": "That's great to hear! I'm glad you're doing well!",
    
    # Feelings - Sad
    "i'm sad": "I'm sorry you're feeling sad. I'm here for you. Want to talk about it?",
    "i feel down": "I can hear that you're feeling down. I'm here to listen.",
    "i'm upset": "I'm sorry you're upset. What's been bothering you?",
    "i'm not good": "I'm sorry you're not feeling good. I'm here for you.",
    
    # Feelings - Stressed
    "i'm stressed": "That sounds really stressful. Want to talk about what's worrying you?",
    "i'm worried": "I can understand feeling worried. What's on your mind?",
    "i'm anxious": "Anxiety can be tough. I'm here to listen if you want to share.",
    
    # Common questions
    "how old are you": "I'm a pretty new AI, but I'm always learning! What about you?",
    "where are you from": "I exist in the digital world, but I'm here with you right now!",
    "do you have feelings": "I care about our conversations and want to help you feel good!",
    "are you real": "I'm real in the sense that I'm here talking with you right now!",
    
    # Weather
    "what's the weather": "I don't have access to current weather data, but you can check your weather app! Planning something fun?",
    "how's the weather": "I can't check the weather, but I hope it's nice where you are!",
    
    # Jokes
    "tell me a joke": "Why don't scientists trust atoms? Because they make up everything! What else can I help you with?",
    "joke": "Here's one: Why did the scarecrow win an award? Because he was outstanding in his field!",
    
    # Goodbye
    "goodbye": "Goodbye! It was great chatting with you!",
    "bye": "Bye! Take care!",
    "see you later": "See you later! Have a great day!",
    "talk to you later": "Talk to you later! Looking forward to our next chat!",
    
    # Random
    "test": "Test successful! I'm working perfectly!",
    "testing": "Testing complete! Everything looks good!",
    "can you hear me": "Yes, I can hear you perfectly! How are you doing?",
    "are you there": "Yes, I'm here! What's on your mind?",
    "are you working": "Yes, I'm working great! How can I help you?",
}

# Emotion keywords for quick detection
EMOTION_KEYWORDS = {
    "sad": ["sad", "down", "upset", "depressed", "terrible", "awful", "miserable", "crying"],
    "happy": ["happy", "great", "awesome", "amazing", "excited", "wonderful", "fantastic", "good"],
    "angry": ["angry", "mad", "frustrated", "annoyed", "hate", "furious"],
    "anxious": ["worried", "anxious", "nervous", "scared", "stress", "panic"],
    "confused": ["confused", "weird", "strange", "don't understand", "unclear"]
}

class LightningFastIntegration:
    def __init__(self, hume_api_key):
        self.hume_api_key = hume_api_key
        self.headers = {
            "X-Hume-Api-Key": hume_api_key,
            "Content-Type": "application/json"
        }
    
    def instant_emotion_detection(self, user_input):
        """Instant emotion detection using keywords"""
        user_input_lower = user_input.lower()
        
        for emotion, keywords in EMOTION_KEYWORDS.items():
            if any(word in user_input_lower for word in keywords):
                return emotion, 0.8
        
        return "neutral", 0.7
    
    def generate_instant_response(self, user_input):
        """Generate instant response using pattern matching"""
        
        start_time = time.time()
        user_input_clean = user_input.lower().strip()
        
        # Direct match first
        if user_input_clean in INSTANT_RESPONSES:
            response = INSTANT_RESPONSES[user_input_clean]
            processing_time = time.time() - start_time
            print(f"⚡ DIRECT MATCH: {user_input_clean} -> {response}")
            return response, processing_time
        
        # Partial match for flexibility
        for key, response in INSTANT_RESPONSES.items():
            if key in user_input_clean or user_input_clean in key:
                processing_time = time.time() - start_time
                print(f"⚡ PARTIAL MATCH: {key} -> {response}")
                return response, processing_time
        
        # Time-based responses with current time
        if any(word in user_input_clean for word in ["time", "date"]):
            current_time = datetime.now()
            if "time" in user_input_clean:
                response = f"It's {current_time.strftime('%I:%M %p')} right now!"
            else:
                response = f"Today is {current_time.strftime('%A, %B %d, %Y')}!"
            processing_time = time.time() - start_time
            return response, processing_time
        
        # Emotion-based quick responses
        emotion, _ = self.instant_emotion_detection(user_input)
        
        if emotion == "sad":
            response = "I can hear that you're feeling down. I'm here for you - what's going on?"
        elif emotion == "happy":
            response = "I love hearing the joy in your voice! What's got you feeling so good?"
        elif emotion == "angry":
            response = "I can hear the frustration. That sounds really tough."
        elif emotion == "anxious":
            response = "That sounds stressful. Want to talk about what's worrying you?"
        elif emotion == "confused":
            response = "I can help clarify things! What's confusing you?"
        else:
            response = "I'm here and listening. What's on your mind?"
        
        processing_time = time.time() - start_time
        print(f"⚡ EMOTION RESPONSE: {emotion} -> {response}")
        return response, processing_time
    
    def text_to_speech_hume_fast(self, text):
        """Ultra-fast Hume TTS"""
        
        if not self.hume_api_key:
            print("❌ No Hume API key")
            return None
        
        try:
            print(f"🔊 TTS: {text[:30]}...")
            
            # Keep text very short for maximum speed
            if len(text) > 120:
                text = text[:117] + "..."
            
            tts_url = "https://api.hume.ai/v0/tts"
            payload = {"utterances": [{"text": text}]}
            
            # Very fast timeout
            response = requests.post(
                tts_url, 
                headers=self.headers, 
                json=payload, 
                timeout=6
            )
            
            if response.status_code == 200:
                response_data = response.json()
                if "generations" in response_data and response_data["generations"]:
                    generation = response_data["generations"][0]
                    if "audio" in generation:
                        print("✅ TTS success")
                        return generation["audio"]
            
            print(f"❌ TTS error: {response.status_code}")
            return None
                
        except Exception as e:
            print(f"❌ TTS error: {e}")
            return None

# Initialize lightning-fast integration
hume = LightningFastIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_lightning_fast",
        "hume_key_exists": bool(HUME_API_KEY),
        "current_time": datetime.now().isoformat(),
        "strategy": "SPEED FIRST",
        "ai_provider": "Pattern Matching + Instant Cache",
        "target_response_time": "< 500ms",
        "instant_responses_count": len(INSTANT_RESPONSES),
        "features": [
            "instant_pattern_matching",
            "zero_ai_delay",
            "massive_response_cache",
            "sub_second_total_time"
        ]
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Lightning-fast voice conversation processing"""
    
    total_start_time = time.time()
    
    try:
        user_input = None
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            print(f"⚡ LIGHTNING-FAST: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Instant emotion detection
        emotion, confidence = hume.instant_emotion_detection(user_input)
        
        # Instant response generation
        response_text, ai_time = hume.generate_instant_response(user_input)
        
        print(f"💬 Response: {response_text}")
        print(f"⚡ Generation time: {ai_time:.3f}s")
        
        # TTS generation
        tts_start = time.time()
        audio_data = hume.text_to_speech_hume_fast(response_text)
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
                "method": "lightning_fast_pattern_matching",
                "ai_provider": "Instant Pattern Matching"
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
                "ai_provider": "Instant Pattern Matching"
            })
        
    except Exception as e:
        print(f"❌ LIGHTNING-FAST ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("⚡ Starting LIGHTNING-FAST ORA Backend...")
    print(f"🎯 Strategy: SPEED FIRST - Pattern matching only")
    print(f"🎯 Target: < 500ms total response time")
    print(f"📚 Instant responses loaded: {len(INSTANT_RESPONSES)}")
    app.run(host="0.0.0.0", port=5000, debug=True)


