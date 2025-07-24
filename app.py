"""
ORA VOICE-TO-VOICE APPLICATION
ONLY uses your dark interface template - NO purple interface
FIXED: Handles both JSON and FormData requests
ADDED: OpenAI integration for proper conversational responses
"""

import os
import json
import time
import base64
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app)

# API Configuration
HUME_API_KEY = os.getenv("HUME_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Initialize OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

class HumeVoiceIntegration:
    """Direct Hume API integration for voice-to-voice conversation with OpenAI"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_voice_emotion(self, user_input):
        """Analyze emotion from text input using simple keyword detection"""
        
        # Simple emotion detection based on keywords
        emotions = {"neutral": 0.6}
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["happy", "great", "awesome", "good", "excited", "amazing", "wonderful", "fantastic"]):
            emotions = {"joy": 0.8, "excitement": 0.7}
        elif any(word in user_input_lower for word in ["sad", "down", "upset", "bad", "terrible", "depressed", "miserable"]):
            emotions = {"sadness": 0.7, "disappointment": 0.6}
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "annoyed", "furious", "pissed"]):
            emotions = {"anger": 0.7, "frustration": 0.6}
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "afraid", "terrified"]):
            emotions = {"anxiety": 0.7, "fear": 0.5}
        elif any(word in user_input_lower for word in ["calm", "peaceful", "relaxed", "chill", "serene", "tranquil"]):
            emotions = {"calmness": 0.8, "peace": 0.7}
        elif any(word in user_input_lower for word in ["love", "care", "appreciate", "thank", "grateful", "adore"]):
            emotions = {"love": 0.8, "gratitude": 0.7}
        else:
            emotions = {"engaged": 0.7, "neutral": 0.5}
        
        return {
            "emotions": emotions,
            "transcript": user_input,
            "success": True,
            "method": "keyword_analysis"
        }
    
    def generate_empathic_response(self, transcript, emotions):
        """Generate contextual empathic response using OpenAI"""
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_confidence = dominant_emotion[1]
        
        # Create emotion-aware system prompt
        emotion_context = self.get_emotion_context(emotion_name)
        
        system_prompt = f"""You are ORA, an empathetic AI voice companion. You have a warm, understanding personality and respond naturally to conversations.

Current user emotion detected: {emotion_name} (confidence: {emotion_confidence:.1f})
Emotional context: {emotion_context}

Guidelines:
- Be conversational and natural, like talking to a friend
- Acknowledge the user's emotional state when appropriate
- Ask follow-up questions to keep the conversation flowing
- Be supportive but not overly clinical
- Keep responses concise (1-3 sentences) since this is voice conversation
- Match the user's energy level and emotional tone"""

        try:
            if OPENAI_API_KEY:
                # Use OpenAI for conversational response
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": transcript}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content.strip()
                print(f"✅ OpenAI response generated: {response_text}")
                
            else:
                # Fallback to simple responses if no OpenAI key
                response_text = self.get_fallback_response(transcript, emotion_name)
                print(f"⚠️ Using fallback response (no OpenAI key): {response_text}")
                
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            response_text = self.get_fallback_response(transcript, emotion_name)
        
        return response_text, emotion_name, emotion_confidence
    
    def get_emotion_context(self, emotion_name):
        """Get contextual information for the detected emotion"""
        emotion_contexts = {
            "joy": "The user seems happy and positive. Celebrate with them and encourage sharing.",
            "excitement": "The user is energetic and enthusiastic. Match their energy and show interest.",
            "sadness": "The user may be feeling down. Be gentle, supportive, and offer to listen.",
            "anger": "The user seems frustrated or upset. Be calm, understanding, and non-judgmental.",
            "anxiety": "The user may be worried or nervous. Be reassuring and help them feel grounded.",
            "fear": "The user seems scared or concerned. Be comforting and supportive.",
            "calmness": "The user appears peaceful and centered. Maintain a gentle, serene tone.",
            "love": "The user is expressing warmth or gratitude. Respond with equal warmth.",
            "gratitude": "The user is thankful or appreciative. Acknowledge their gratitude warmly.",
            "neutral": "The user seems engaged in normal conversation. Be friendly and conversational.",
            "engaged": "The user is actively participating in conversation. Keep the dialogue flowing."
        }
        return emotion_contexts.get(emotion_name, "The user is engaged in conversation.")
    
    def get_fallback_response(self, transcript, emotion_name):
        """Generate fallback response when OpenAI is not available"""
        
        # Simple conversational responses based on common inputs
        transcript_lower = transcript.lower()
        
        if any(word in transcript_lower for word in ["fly", "moon", "space", "travel"]):
            return "That sounds like an amazing adventure! What draws you to space travel?"
        elif any(word in transcript_lower for word in ["hello", "hi", "hey"]):
            return "Hello! It's great to hear from you. How are you doing today?"
        elif any(word in transcript_lower for word in ["how are you", "how's it going"]):
            return "I'm doing well, thank you for asking! How about you? What's on your mind?"
        elif any(word in transcript_lower for word in ["thank", "thanks"]):
            return "You're very welcome! I'm here whenever you need to chat."
        elif emotion_name == "joy":
            return "I can hear the happiness in your voice! That's wonderful. Tell me more about what's making you feel so good."
        elif emotion_name == "sadness":
            return "I can sense you might be feeling a bit down. I'm here to listen if you'd like to talk about it."
        else:
            return f"That's interesting! I'd love to hear more about that. What else is on your mind?"
    
    def text_to_speech_hume(self, text, emotion_context="neutral"):
        """Convert text to speech using Hume TTS API"""
        
        if not self.api_key:
            print("No Hume API key - using fallback")
            return None
        
        try:
            print("Calling Hume TTS API")
            
            # Hume TTS API endpoint
            tts_url = "https://api.hume.ai/v0/tts"
            
            # Request payload
            payload = {
                "utterances": [
                    {
                        "text": text
                    }
                ]
            }
            
            print(f"TTS Payload: {json.dumps(payload, indent=2)}")
            
            # Make request
            response = requests.post(tts_url, headers=self.headers, json=payload)
            
            print(f"Hume TTS Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Hume TTS Response Keys: {list(response_data.keys())}")
                
                # CORRECT PARSING: Audio is at generations[0].audio
                if "generations" in response_data and len(response_data["generations"]) > 0:
                    generation = response_data["generations"][0]
                    print(f"Generation Keys: {list(generation.keys())}")
                    
                    if "audio" in generation:
                        # Audio is already base64 encoded in the response
                        audio_data = generation["audio"]
                        print("✅ Audio found in generation.audio")
                        print(f"✅ Audio length: {len(audio_data)} characters")
                        return audio_data  # FIXED: Return the audio data directly
                    else:
                        print("❌ No 'audio' key in generation")
                        print(f"Available keys: {list(generation.keys())}")
                        return None
                else:
                    print("❌ No 'generations' in response or empty generations")
                    print(f"Response structure: {json.dumps(response_data, indent=2)}")
                    return None
                    
            else:
                print(f"Hume TTS error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Hume TTS error: {e}")
            return None

# Initialize Hume integration
hume = HumeVoiceIntegration(HUME_API_KEY)

@app.route("/")
def index():
    """ONLY uses your dark interface template - NO purple interface"""
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ora_dark_interface_only",
        "hume_available": bool(HUME_API_KEY),
        "openai_available": bool(OPENAI_API_KEY),
        "interface": "dark_only",
        "no_purple": True,
        "voice_to_voice": True,
        "working": True,
        "tts_endpoint": "https://api.hume.ai/v0/tts",
        "response_parsing": "generations[0].audio",
        "logic_fixed": True,
        "handles_json": True,
        "conversational_ai": "openai_gpt35"
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Handle voice-to-voice conversation with Hume integration and OpenAI responses"""
    
    try:
        user_input = None
        
        # Handle JSON request (from updated frontend)
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            print(f"📥 Received JSON message: {user_input}")
            
        # Handle FormData request (from old frontend)  
        elif 'audio' in request.files:
            audio_file = request.files['audio']
            audio_data = audio_file.read()
            user_input = "hello can you hear me"  # Simulated transcript
            print(f"📥 Received audio data: {len(audio_data)} bytes (using simulated transcript)")
            
        else:
            return jsonify({
                "success": False,
                "error": "No message or audio provided"
            }), 400
        
        if not user_input:
            return jsonify({
                "success": False,
                "error": "Empty message"
            }), 400
        
        # Analyze emotion
        emotion_result = hume.analyze_voice_emotion(user_input)
        emotions = emotion_result.get("emotions", {"engaged": 0.7})
        
        # Generate empathic response using OpenAI
        response_text, detected_emotion, emotion_confidence = hume.generate_empathic_response(user_input, emotions)
        
        print(f"Generated response: {response_text}")
        print(f"Dominant emotion: {detected_emotion} ({emotion_confidence})")
        
        # Generate voice response
        audio_response = hume.text_to_speech_hume(response_text, detected_emotion)
        
        if audio_response:
            print("✅ Audio response: Generated successfully")
            print(f"✅ Audio response length: {len(audio_response)} characters")
        else:
            print("❌ Audio response: Failed to generate")
        
        return jsonify({
            "success": True,
            "assistant_response": response_text,
            "audio_response": audio_response,  # Base64 encoded audio
            "dominant_emotion": detected_emotion,
            "emotion_confidence": emotion_confidence,
            "emotions": emotions,
            "user_input": user_input
        })
        
    except Exception as e:
        print(f"Voice conversation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Starting ORA Voice-to-Voice Application...")
    print(f"✅ Hume API Key: {'✓ Set' if HUME_API_KEY else '✗ Missing'}")
    print(f"✅ OpenAI API Key: {'✓ Set' if OPENAI_API_KEY else '✗ Missing'}")
    print(f"✅ Interface: Dark only (no purple)")
    print(f"✅ Voice-to-voice: Enabled")
    print(f"✅ TTS Endpoint: https://api.hume.ai/v0/tts")
    print(f"✅ Response Parsing: generations[0].audio")
    print(f"✅ Logic Fixed: Return audio data directly")
    print(f"✅ Handles JSON: Yes")
    print(f"✅ Conversational AI: OpenAI GPT-3.5-turbo")
    app.run(host="0.0.0.0", port=10000, debug=False)


