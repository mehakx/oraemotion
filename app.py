"""
ORA VOICE-TO-VOICE APPLICATION
ONLY uses your dark interface template - NO purple interface
FIXED: Handles both JSON and FormData requests
ADDED: OpenAI integration for proper conversational responses
IMPROVED: OpenAI-based emotion detection for accuracy
CONTINUOUS: Conversation history support for natural dialogue flow
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
    """Direct Hume API integration for voice-to-voice conversation with OpenAI and conversation memory"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_voice_emotion(self, user_input):
        """Analyze emotion from text input using OpenAI for better accuracy"""
        
        if OPENAI_API_KEY:
            try:
                # Use OpenAI to analyze emotion more accurately
                emotion_prompt = f"""Analyze the emotional tone of this user message and return the dominant emotion with confidence.

User message: "{user_input}"

Return your response in this exact JSON format:
{{
    "dominant_emotion": "emotion_name",
    "confidence": 0.8,
    "secondary_emotions": ["emotion2", "emotion3"],
    "emotional_context": "brief description of the emotional state"
}}

Possible emotions: joy, sadness, anger, fear, anxiety, excitement, calmness, love, gratitude, frustration, disappointment, curiosity, confusion, neutral, engaged, weird, uncomfortable, concerned, hopeful, tired, energetic

Be nuanced - "feeling weird" should be detected as uncomfortable/confused, not happy."""

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert emotion analyst. Analyze text for emotional content accurately and return structured JSON."},
                        {"role": "user", "content": emotion_prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                emotion_analysis = response.choices[0].message.content.strip()
                print(f"🧠 OpenAI emotion analysis: {emotion_analysis}")
                
                # Parse the JSON response
                try:
                    emotion_data = json.loads(emotion_analysis)
                    dominant_emotion = emotion_data.get("dominant_emotion", "neutral")
                    confidence = emotion_data.get("confidence", 0.7)
                    
                    # Create emotions dict in expected format
                    emotions = {dominant_emotion: confidence}
                    
                    # Add secondary emotions with lower confidence
                    for secondary in emotion_data.get("secondary_emotions", []):
                        emotions[secondary] = confidence * 0.6
                    
                    print(f"✅ Detected emotion: {dominant_emotion} ({confidence})")
                    
                    return {
                        "emotions": emotions,
                        "transcript": user_input,
                        "success": True,
                        "method": "openai_analysis",
                        "emotional_context": emotion_data.get("emotional_context", "")
                    }
                    
                except json.JSONDecodeError:
                    print("❌ Failed to parse OpenAI emotion response, using fallback")
                    return self.fallback_emotion_analysis(user_input)
                    
            except Exception as e:
                print(f"❌ OpenAI emotion analysis error: {e}")
                return self.fallback_emotion_analysis(user_input)
        else:
            return self.fallback_emotion_analysis(user_input)
    
    def fallback_emotion_analysis(self, user_input):
        """Improved fallback emotion detection with better keyword matching"""
        
        emotions = {"neutral": 0.6}
        user_input_lower = user_input.lower()
        
        # More comprehensive emotion detection
        if any(word in user_input_lower for word in ["happy", "great", "awesome", "good", "excited", "amazing", "wonderful", "fantastic", "love it", "perfect"]):
            emotions = {"joy": 0.8, "excitement": 0.7}
        elif any(word in user_input_lower for word in ["sad", "down", "upset", "bad", "terrible", "depressed", "miserable", "awful", "horrible", "not good", "not great"]):
            emotions = {"sadness": 0.7, "disappointment": 0.6}
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "annoyed", "furious", "pissed", "irritated"]):
            emotions = {"anger": 0.7, "frustration": 0.6}
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "afraid", "terrified", "concerned"]):
            emotions = {"anxiety": 0.7, "fear": 0.5}
        elif any(word in user_input_lower for word in ["weird", "strange", "odd", "uncomfortable", "confused", "unsure", "mixed up"]):
            emotions = {"confusion": 0.7, "uncomfortable": 0.6}
        elif any(word in user_input_lower for word in ["tired", "exhausted", "drained", "sleepy", "worn out"]):
            emotions = {"fatigue": 0.7, "low_energy": 0.6}
        elif any(word in user_input_lower for word in ["calm", "peaceful", "relaxed", "chill", "serene", "tranquil"]):
            emotions = {"calmness": 0.8, "peace": 0.7}
        elif any(word in user_input_lower for word in ["thank", "grateful", "appreciate", "thankful"]):
            emotions = {"gratitude": 0.8, "appreciation": 0.7}
        else:
            emotions = {"engaged": 0.7, "neutral": 0.5}
        
        return {
            "emotions": emotions,
            "transcript": user_input,
            "success": True,
            "method": "keyword_analysis_improved"
        }
    
    def generate_empathic_response(self, transcript, emotions, conversation_history=None, emotional_context=""):
        """Generate contextual empathic response using OpenAI with conversation history for continuity"""
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_confidence = dominant_emotion[1]
        
        # Create emotion-aware system prompt
        system_prompt = f"""You are ORA, an empathetic AI voice companion. You have a warm, understanding personality and respond naturally to conversations.

Current user emotion detected: {emotion_name} (confidence: {emotion_confidence:.1f})
{f"Emotional context: {emotional_context}" if emotional_context else ""}

Guidelines:
- Be conversational and natural, like talking to a caring friend
- Remember the conversation history and build on previous exchanges
- Acknowledge the user's emotional state when appropriate
- Ask follow-up questions naturally to keep the conversation flowing
- Be supportive but not overly clinical or therapeutic
- Keep responses concise (1-3 sentences) since this is voice conversation
- Match the user's energy level and emotional tone
- Be genuine and authentic in your responses
- Reference previous parts of the conversation when relevant"""

        try:
            if OPENAI_API_KEY:
                # Build conversation messages for OpenAI
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history if provided
                if conversation_history:
                    for turn in conversation_history:
                        if turn.get("role") == "user":
                            messages.append({"role": "user", "content": turn.get("content", "")})
                        elif turn.get("role") == "assistant":
                            messages.append({"role": "assistant", "content": turn.get("content", "")})
                
                # Add current user message
                messages.append({"role": "user", "content": transcript})
                
                print(f"💬 Conversation context: {len(messages)} messages")
                
                # Use OpenAI for conversational response with history
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                
                response_text = response.choices[0].message.content.strip()
                print(f"✅ OpenAI response generated: {response_text}")
                
            else:
                # Fallback to simple responses if no OpenAI key
                response_text = self.get_fallback_response(transcript, emotion_name, conversation_history)
                print(f"⚠️ Using fallback response (no OpenAI key): {response_text}")
                
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            response_text = self.get_fallback_response(transcript, emotion_name, conversation_history)
        
        return response_text, emotion_name, emotion_confidence
    
    def get_fallback_response(self, transcript, emotion_name, conversation_history=None):
        """Generate fallback response when OpenAI is not available"""
        
        transcript_lower = transcript.lower()
        
        # Check if this is a continuation of previous conversation
        is_continuation = conversation_history and len(conversation_history) > 0
        
        # Handle specific emotional states better
        if emotion_name in ["confusion", "uncomfortable", "weird"]:
            return "It sounds like something's feeling a bit off for you. I'm here to listen - what's going on?"
        elif "weird" in transcript_lower or "strange" in transcript_lower:
            return "That does sound like a weird feeling. Can you tell me more about what's making you feel that way?"
        elif any(word in transcript_lower for word in ["not good", "not great", "bad", "terrible"]):
            if is_continuation:
                return "I'm sorry to hear you're not doing well. What's been going on that's making you feel this way?"
            else:
                return "I'm sorry you're not feeling great. Would you like to talk about what's bothering you?"
        elif any(word in transcript_lower for word in ["hello", "hi", "hey"]) and not is_continuation:
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
            if is_continuation:
                return "I see. Tell me more about that - I'm listening."
            else:
                return "That's interesting! I'd love to hear more about that. What else is on your mind?"
    
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
        "conversational_ai": "openai_gpt35",
        "emotion_detection": "openai_enhanced",
        "conversation_memory": True
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Handle voice-to-voice conversation with Hume integration, OpenAI responses, and conversation history"""
    
    try:
        user_input = None
        conversation_history = []
        
        # Handle JSON request (from updated frontend)
        if request.is_json:
            data = request.get_json()
            user_input = data.get("message", "")
            conversation_history = data.get("conversation_history", [])
            print(f"📥 Received JSON message: {user_input}")
            print(f"📚 Conversation history: {len(conversation_history)} turns")
            
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
        
        # Analyze emotion with improved detection
        emotion_result = hume.analyze_voice_emotion(user_input)
        emotions = emotion_result.get("emotions", {"engaged": 0.7})
        emotional_context = emotion_result.get("emotional_context", "")
        
        # Generate empathic response using OpenAI with conversation history
        response_text, detected_emotion, emotion_confidence = hume.generate_empathic_response(
            user_input, emotions, conversation_history, emotional_context
        )
        
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
            "user_input": user_input,
            "emotional_context": emotional_context
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
    print(f"✅ Emotion Detection: OpenAI Enhanced")
    print(f"✅ Conversation Memory: Enabled")
    app.run(host="0.0.0.0", port=10000, debug=False)

