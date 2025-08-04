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

print(f"🎭 BALANCED EMPATHY + SPEED SETUP:")
print(f"HUME_API_KEY exists: {bool(HUME_API_KEY)}")
print(f"GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")

# Initialize Groq client for fast AI responses
groq_client = None
groq_working = False

if GROQ_API_KEY:
    try:
        # Try different import methods for Groq
        try:
            from groq import Groq
            print("✅ Imported Groq from groq")
        except ImportError:
            try:
                import groq
                Groq = groq.Client
                print("✅ Imported Groq as groq.Client")
            except:
                try:
                    import groq
                    Groq = groq.Groq
                    print("✅ Imported Groq as groq.Groq")
                except:
                    raise ImportError("Could not import Groq client")
        
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
        
    except Exception as e:
        print(f"❌ Groq initialization failed: {e}")
        groq_working = False

# Instant empathetic responses for common emotional states
EMPATHETIC_CACHE = {
    "hello": "Hey there! I'm really glad you're here. How are you feeling today?",
    "hi": "Hi! It's so good to connect with you. What's on your mind?",
    "hey": "Hey! I'm here for you. How can I support you right now?",
    "i'm sad": "I can really hear the sadness in what you're sharing. That sounds so difficult. I'm here with you - what's been weighing on your heart?",
    "i feel down": "I can sense you're feeling down right now. Those feelings are so valid. Want to tell me more about what's going on?",
    "i'm anxious": "I can feel the anxiety in your words. That must feel so overwhelming right now. Let's take this one breath at a time. What's making you feel most anxious?",
    "i'm worried": "I hear the worry in your voice. It makes complete sense that you'd feel this way. What's been on your mind that's causing this worry?",
    "i'm angry": "I can hear the anger in your voice, and that's completely valid. Something has really upset you. What happened that's made you feel this way?",
    "i'm happy": "I can hear the joy in your voice and it just lights up my whole world! What's been bringing you this happiness?",
    "i'm lonely": "Loneliness can feel so heavy and isolating. I want you to know that I'm here with you, and you matter so much. You're not as alone as you feel right now.",
    "how are you": "I'm doing well, thank you for asking! But more importantly, how are YOU doing? I really want to know how you're feeling.",
}

class BalancedEmpathyIntegration:
    def __init__(self, hume_api_key):
        self.hume_api_key = hume_api_key
        self.headers = {
            "X-Hume-Api-Key": hume_api_key,
            "Content-Type": "application/json"
        }
    
    def detect_emotion_advanced(self, user_input):
        """Advanced emotion detection with nuanced understanding"""
        user_input_lower = user_input.lower()
        
        # Sadness indicators
        sadness_words = ["sad", "down", "depressed", "crying", "tears", "miserable", "awful", "terrible", "hopeless", "empty", "broken"]
        if any(word in user_input_lower for word in sadness_words):
            confidence = 0.9 if any(strong in user_input_lower for strong in ["crying", "depressed", "miserable"]) else 0.8
            return "sadness", confidence, "deep emotional pain"
        
        # Anxiety indicators
        anxiety_words = ["anxious", "worried", "nervous", "scared", "afraid", "panic", "stress", "overwhelmed", "can't breathe"]
        if any(word in user_input_lower for word in anxiety_words):
            confidence = 0.9 if any(strong in user_input_lower for strong in ["panic", "can't breathe", "overwhelmed"]) else 0.8
            return "anxiety", confidence, "heightened worry and fear"
        
        # Anger indicators
        anger_words = ["angry", "mad", "furious", "frustrated", "annoyed", "pissed", "hate", "rage"]
        if any(word in user_input_lower for word in anger_words):
            confidence = 0.9 if any(strong in user_input_lower for strong in ["furious", "rage", "hate"]) else 0.8
            return "anger", confidence, "intense frustration"
        
        # Joy indicators
        joy_words = ["happy", "excited", "great", "amazing", "wonderful", "fantastic", "awesome", "thrilled", "elated"]
        if any(word in user_input_lower for word in joy_words):
            confidence = 0.8
            return "joy", confidence, "positive emotional state"
        
        # Loneliness indicators
        loneliness_words = ["lonely", "alone", "isolated", "nobody", "no one", "empty", "disconnected"]
        if any(word in user_input_lower for word in loneliness_words):
            confidence = 0.8
            return "loneliness", confidence, "feeling disconnected and isolated"
        
        # Confusion indicators
        confusion_words = ["confused", "don't understand", "unclear", "lost", "don't know", "weird", "strange"]
        if any(word in user_input_lower for word in confusion_words):
            confidence = 0.7
            return "confusion", confidence, "seeking clarity and understanding"
        
        return "neutral", 0.6, "balanced emotional state"
    
    def generate_empathetic_response(self, user_input, emotion, emotion_context, conversation_history=None):
        """Generate empathetic response balancing speed and emotional intelligence"""
        
        start_time = time.time()
        user_input_clean = user_input.lower().strip()
        
        # Check empathetic cache first for instant emotional responses
        for cached_phrase, empathetic_response in EMPATHETIC_CACHE.items():
            if cached_phrase in user_input_clean or user_input_clean in cached_phrase:
                processing_time = time.time() - start_time
                print(f"💝 EMPATHETIC CACHE HIT: {cached_phrase}")
                return empathetic_response, processing_time
        
        # Use Groq for complex emotional responses if available
        if groq_client and groq_working:
            try:
                current_time = datetime.now()
                
                # Enhanced empathy-focused system prompt
                system_prompt = f"""You are ORA, a deeply empathetic AI companion with advanced emotional intelligence. Current time: {current_time.strftime('%I:%M %p, %A %B %d, %Y')}.

EMOTIONAL CONTEXT:
- User's emotion: {emotion} (context: {emotion_context})
- This is a real person sharing their feelings with you

EMPATHY PRINCIPLES:
1. ALWAYS acknowledge their emotional state first with genuine empathy
2. Use phrases like "I can hear the [emotion] in your voice" or "That sounds so [emotion descriptor]"
3. Validate their feelings completely - never minimize or dismiss
4. Show you're truly present and listening
5. Ask gentle, caring follow-up questions
6. Match their emotional energy appropriately
7. Be warm, genuine, and deeply caring

RESPONSE STYLE:
- If they're sad: Be gentle, validating, present. "I can really hear the sadness..."
- If they're anxious: Be calming, understanding. "That sounds so overwhelming..."
- If they're angry: Be validating, non-judgmental. "I can hear the frustration..."
- If they're happy: Share their joy genuinely. "I can hear the happiness in your voice!"
- If they're lonely: Be present, caring. "You're not as alone as you feel..."

Keep responses 2-3 sentences, deeply empathetic, and emotionally intelligent."""

                messages = [{"role": "system", "content": system_prompt}]
                
                # Add recent conversation for emotional context
                if conversation_history:
                    recent = conversation_history[-3:]
                    for msg in recent:
                        if msg.get('role') in ['user', 'assistant']:
                            messages.append({"role": msg['role'], "content": msg['content']})
                
                messages.append({"role": "user", "content": user_input})
                
                # Generate empathetic response
                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=80,
                    temperature=0.8,
                    top_p=0.9
                )
                
                response_text = response.choices[0].message.content.strip()
                processing_time = time.time() - start_time
                print(f"💝 Groq empathetic response in {processing_time:.3f}s: {response_text}")
                return response_text, processing_time
                
            except Exception as e:
                print(f"❌ Groq error: {e}")
        
        # Empathetic fallback responses based on detected emotion
        fallback_response = self.get_empathetic_fallback(user_input, emotion)
        processing_time = time.time() - start_time
        return fallback_response, processing_time
    
    def get_empathetic_fallback(self, user_input, emotion):
        """Empathetic fallback responses that maintain emotional intelligence"""
        user_input_lower = user_input.lower()
        
        # Time-based responses with empathy
        if any(phrase in user_input_lower for phrase in ["time", "date", "what time is it"]):
            current_time = datetime.now()
            return f"It's {current_time.strftime('%I:%M %p')} right now. How are you feeling at this moment? Is there something on your mind?"
        
        # Emotion-specific empathetic responses
        if emotion == "sadness":
            return "I can really hear the sadness in what you're sharing. That sounds so difficult, and I want you to know I'm here with you. What's been weighing on your heart?"
        elif emotion == "anxiety":
            return "I can sense the anxiety in your words, and that must feel so overwhelming. Let's take this one moment at a time. What's been making you feel most anxious?"
        elif emotion == "anger":
            return "I can hear the frustration and anger in your voice, and those feelings are completely valid. Something has really upset you. What happened?"
        elif emotion == "joy":
            return "I can hear the happiness in your voice and it just brightens everything! I love seeing you feel this way. What's been bringing you this joy?"
        elif emotion == "loneliness":
            return "I hear that feeling of loneliness, and I want you to know that you're not as alone as you feel right now. I'm here with you. What's been making you feel most isolated?"
        elif emotion == "confusion":
            return "I can sense you're feeling confused or unclear about something. That's completely understandable. I'm here to help you work through whatever is puzzling you."
        else:
            return "I'm here and I'm listening to you with my whole attention. Whatever you're feeling right now is valid and important. What's on your mind?"
    
    def text_to_speech_hume_reliable(self, text):
        """Reliable Hume TTS with retry logic and better timeout handling"""
        
        if not self.hume_api_key:
            print("❌ No Hume API key")
            return None
        
        # Keep text length reasonable for natural delivery
        if len(text) > 180:
            text = text[:177] + "..."
        
        tts_url = "https://api.hume.ai/v0/tts"
        payload = {"utterances": [{"text": text}]}
        
        # Try multiple times with increasing timeouts
        timeouts = [12, 15, 20]  # Increased timeouts
        
        for attempt, timeout in enumerate(timeouts, 1):
            try:
                print(f"🔊 TTS attempt {attempt}/{len(timeouts)} (timeout: {timeout}s): {text[:40]}...")
                
                response = requests.post(
                    tts_url, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=timeout
                )
                
                print(f"🔊 TTS response status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        
                        if "generations" in response_data and response_data["generations"]:
                            generation = response_data["generations"][0]
                            
                            if "audio" in generation:
                                audio_data = generation["audio"]
                                print(f"✅ TTS success on attempt {attempt}: {len(audio_data)} chars")
                                return audio_data
                            else:
                                print(f"❌ No 'audio' key in generation (attempt {attempt})")
                        else:
                            print(f"❌ No 'generations' in response (attempt {attempt})")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON decode error (attempt {attempt}): {e}")
                        
                elif response.status_code == 429:  # Rate limit
                    print(f"⏳ Rate limited, waiting before retry...")
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ TTS HTTP error (attempt {attempt}): {response.status_code}")
                    print(f"❌ Response: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print(f"⏰ TTS timeout on attempt {attempt} ({timeout}s)")
                if attempt < len(timeouts):
                    print(f"🔄 Retrying with longer timeout...")
                    continue
            except requests.exceptions.ConnectionError:
                print(f"🌐 Connection error on attempt {attempt}")
                if attempt < len(timeouts):
                    time.sleep(1)
                    continue
            except Exception as e:
                print(f"❌ TTS error on attempt {attempt}: {e}")
                if attempt < len(timeouts):
                    continue
        
        print("❌ All TTS attempts failed")
        return None

# Initialize balanced empathy integration
hume = BalancedEmpathyIntegration(HUME_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "ora_groq_import_fixed",
        "groq_working": groq_working,
        "hume_key_exists": bool(HUME_API_KEY),
        "current_time": datetime.now().isoformat(),
        "ai_provider": "Groq + Empathetic Intelligence" if groq_working else "Empathetic Fallbacks",
        "empathy_engine": "active",
        "tts_reliability": "enhanced_with_retry",
        "target_response_time": "< 2 seconds with emotional intelligence",
        "empathetic_cache_size": len(EMPATHETIC_CACHE),
        "features": [
            "advanced_emotion_detection",
            "empathetic_response_generation",
            "emotional_cache_responses",
            "reliable_tts_with_retry",
            "balanced_speed_and_empathy"
        ]
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Balanced empathy and speed voice conversation processing with reliable TTS"""
    
    total_start_time = time.time()
    
    try:
        user_input = None
        conversation_history = []
        
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"💝 EMPATHETIC ORA: {user_input}")
            
        elif 'audio' in request.files:
            user_input = "hello can you hear me"
            
        else:
            return jsonify({"success": False, "error": "No input provided"}), 400
        
        if not user_input:
            return jsonify({"success": False, "error": "Empty message"}), 400
        
        # Advanced emotion detection
        emotion, confidence, emotion_context = hume.detect_emotion_advanced(user_input)
        print(f"🎭 Emotion detected: {emotion} ({confidence:.1f}) - {emotion_context}")
        
        # Generate empathetic response
        response_text, ai_time = hume.generate_empathetic_response(
            user_input, emotion, emotion_context, conversation_history
        )
        
        print(f"💝 Empathetic response: {response_text}")
        print(f"⚡ Generation time: {ai_time:.3f}s")
        
        # Generate reliable empathetic audio
        tts_start = time.time()
        audio_data = hume.text_to_speech_hume_reliable(response_text)
        tts_time = time.time() - tts_start
        
        total_time = time.time() - total_start_time
        print(f"🔊 TTS time: {tts_time:.3f}s")
        print(f"💝 TOTAL empathetic response time: {total_time:.3f}s")
        
        if audio_data:
            return jsonify({
                "success": True,
                "response": response_text,
                "audio_response": audio_data,
                "emotion": emotion,
                "emotion_confidence": confidence,
                "emotion_context": emotion_context,
                "processing_time": total_time,
                "ai_generation_time": ai_time,
                "tts_time": tts_time,
                "method": "groq_import_fixed",
                "ai_provider": "Groq + Empathetic Intelligence" if groq_working else "Empathetic Fallbacks",
                "empathy_level": "high",
                "tts_status": "success"
            })
        else:
            return jsonify({
                "success": True,
                "response": response_text,
                "emotion": emotion,
                "emotion_confidence": confidence,
                "emotion_context": emotion_context,
                "processing_time": total_time,
                "ai_generation_time": ai_time,
                "tts_time": tts_time,
                "error": "Audio generation failed after retries",
                "ai_provider": "Groq + Empathetic Intelligence" if groq_working else "Empathetic Fallbacks",
                "tts_status": "failed"
            })
        
    except Exception as e:
        print(f"❌ EMPATHETIC ERROR: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    print("💝 Starting GROQ IMPORT FIXED + EMPATHY ORA Backend...")
    print(f"🎭 Empathy Engine: ACTIVE")
    print(f"🔊 TTS: Enhanced reliability with retry logic")
    print(f"⚡ AI Provider: {'Groq + Empathy' if groq_working else 'Empathetic Fallbacks'}")
    print(f"🎯 Target: < 3 seconds with deep emotional intelligence + reliable audio")
    print(f"💝 Empathetic responses loaded: {len(EMPATHETIC_CACHE)}")
    app.run(host="0.0.0.0", port=5000, debug=True)


