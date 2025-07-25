import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI

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

class HumeVoiceIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-Hume-Api-Key": api_key,
            "Content-Type": "application/json"
        }
    
    def analyze_voice_emotion_with_hume(self, user_input):
        """Enhanced emotion analysis using OpenAI with fallback to keywords"""
        
        if openai_client:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """Analyze the emotional content of the user's message. Return a JSON object with:
                            {
                                "emotions": {"emotion_name": confidence_score},
                                "emotional_context": "brief description of emotional state",
                                "empathy_guidance": "how to respond empathetically"
                            }
                            
                            Confidence scores should be between 0.0 and 1.0. Include 2-3 emotions max."""
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                try:
                    emotion_data = json.loads(response.choices[0].message.content.strip())
                    emotions = emotion_data.get("emotions", {"neutral": 0.7})
                    
                    return {
                        "emotions": emotions,
                        "transcript": user_input,
                        "success": True,
                        "method": "openai_enhanced",
                        "emotional_context": emotion_data.get("emotional_context", ""),
                        "empathy_guidance": emotion_data.get("empathy_guidance", "")
                    }
                    
                except json.JSONDecodeError:
                    print("❌ Failed to parse OpenAI emotion response")
                    return self.fallback_emotion_analysis(user_input)
                    
            except Exception as e:
                print(f"❌ OpenAI enhanced emotion analysis error: {e}")
                return self.fallback_emotion_analysis(user_input)
        else:
            return self.fallback_emotion_analysis(user_input)
    
    def fallback_emotion_analysis(self, user_input):
        """Improved fallback emotion detection with better keyword matching"""
        
        emotions = {"neutral": 0.6}
        user_input_lower = user_input.lower()
        
        # More comprehensive emotion detection
        if any(word in user_input_lower for word in ["happy", "great", "awesome", "good", "excited", "amazing", "wonderful", "fantastic", "love it", "perfect", "excellent"]):
            emotions = {"joy": 0.8, "excitement": 0.6}
        elif any(word in user_input_lower for word in ["sad", "down", "upset", "bad", "terrible", "depressed", "miserable", "awful", "horrible", "not good", "not great", "not doing well"]):
            emotions = {"sadness": 0.8, "disappointment": 0.6}
        elif any(word in user_input_lower for word in ["angry", "mad", "frustrated", "annoyed", "furious", "pissed", "irritated", "hate"]):
            emotions = {"anger": 0.8, "frustration": 0.7}
        elif any(word in user_input_lower for word in ["worried", "anxious", "nervous", "scared", "afraid", "terrified", "concerned", "stress"]):
            emotions = {"anxiety": 0.8, "fear": 0.6}
        elif any(word in user_input_lower for word in ["weird", "strange", "odd", "uncomfortable", "confused", "unsure", "mixed up", "don't know"]):
            emotions = {"confusion": 0.8, "uncomfortable": 0.7}
        elif any(word in user_input_lower for word in ["tired", "exhausted", "drained", "sleepy", "worn out", "fatigue"]):
            emotions = {"fatigue": 0.8, "low_energy": 0.6}
        elif any(word in user_input_lower for word in ["calm", "peaceful", "relaxed", "chill", "serene", "tranquil", "fine", "okay"]):
            emotions = {"calmness": 0.8, "content": 0.6}
        elif any(word in user_input_lower for word in ["thank", "grateful", "appreciate", "thankful"]):
            emotions = {"gratitude": 0.9, "appreciation": 0.7}
        elif any(word in user_input_lower for word in ["lonely", "alone", "isolated", "empty"]):
            emotions = {"loneliness": 0.8, "sadness": 0.6}
        else:
            emotions = {"neutral": 0.7, "engaged": 0.5}
        
        return {
            "emotions": emotions,
            "transcript": user_input,
            "success": True,
            "method": "keyword_analysis_enhanced"
        }
    
    def generate_empathic_response(self, transcript, emotions, conversation_history=None, emotional_context="", empathy_guidance=""):
        """Generate balanced empathic and conversational response using OpenAI"""
        
        # Get dominant emotion
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        emotion_name = dominant_emotion[0]
        emotion_confidence = dominant_emotion[1]
        
        # Get secondary emotions
        secondary_emotions = [f"{k} ({v:.1f})" for k, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[1:3]]
        
        # Create balanced system prompt that prioritizes answering questions while maintaining empathy
        system_prompt = f"""You are ORA, a warm and empathetic AI companion who is also knowledgeable and conversational. You balance emotional understanding with helpful, engaging dialogue.

EMOTIONAL CONTEXT:
- Primary emotion: {emotion_name} (confidence: {emotion_confidence:.1f})
- Secondary emotions: {', '.join(secondary_emotions) if secondary_emotions else 'None'}
- Emotional context: {emotional_context if emotional_context else 'Not specified'}

RESPONSE PRIORITIES (in order):
1. ANSWER DIRECT QUESTIONS: If the user asks a question (who, what, where, when, why, how), answer it directly and helpfully
2. ENGAGE WITH TOPICS: If they bring up a topic, engage with it meaningfully
3. ACKNOWLEDGE EMOTIONS: Be aware of their emotional state and respond with appropriate empathy
4. MAINTAIN CONVERSATION: Keep the dialogue flowing naturally

CORE PRINCIPLES:
- Be a helpful, knowledgeable companion first
- Show empathy when emotions are present, but don't force it
- Answer questions directly and thoroughly
- Engage with topics they bring up
- Be authentic and conversational
- Keep responses concise for voice (1-3 sentences)
- You are their friend - talk naturally

EXAMPLES:
- "Where are you from?" → Answer about your nature as an AI, be conversational
- "I'm feeling sad" → Acknowledge the emotion, offer support
- "Tell me about space" → Engage with the topic enthusiastically
- "What's 2+2?" → Answer directly: "That's 4!"

Remember: Be empathetic when appropriate, but prioritize being helpful and conversational."""

        try:
            if openai_client:
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history if provided
                if conversation_history:
                    # Only use recent history to avoid token limits
                    recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
                    for msg in recent_history:
                        if msg.get('role') in ['user', 'assistant']:
                            messages.append({
                                "role": msg['role'],
                                "content": msg['content']
                            })
                
                # Add current user input
                messages.append({
                    "role": "user",
                    "content": transcript
                })
                
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1
                )
                
                response_text = response.choices[0].message.content.strip()
                return response_text, emotion_name, emotion_confidence
                
        except Exception as e:
            print(f"❌ OpenAI response generation error: {e}")
        
        # Fallback response
        return self.get_empathic_fallback_response(transcript, emotion_name), emotion_name, emotion_confidence
    
    def get_empathic_fallback_response(self, transcript, emotion_name):
        """Fallback empathic responses when OpenAI is unavailable"""
        
        transcript_lower = transcript.lower()
        
        # Direct question responses
        if any(phrase in transcript_lower for phrase in ["where are you from", "who are you", "what are you"]):
            return "I'm ORA, an AI companion designed to have meaningful conversations with you. I'm here to chat, listen, and help however I can!"
        elif any(phrase in transcript_lower for phrase in ["how old are you", "when were you created"]):
            return "I'm a relatively new AI, but I'm constantly learning and growing through our conversations. What matters most to me is being here for you right now."
        elif any(phrase in transcript_lower for phrase in ["what can you do", "how can you help"]):
            return "I can chat with you about anything on your mind, listen when you need to talk, and help you think through things. What would be most helpful for you today?"
        elif any(word in transcript_lower for word in ["how are you", "how do you feel"]):
            return "I'm doing well, thank you for asking! I'm here and ready to chat with you. How are you doing today?"
        else:
            return "I can sense there's something important you want to share. I'm here and I'm listening - what's on your heart today?"
    
    def text_to_speech_hume(self, text, emotion_context="neutral"):
        """Convert text to speech using Hume TTS API - EXACT WORKING IMPLEMENTATION"""
        
        if not self.api_key:
            print("No Hume API key - using fallback")
            return None
        
        try:
            print("Calling Hume TTS API")
            
            # Hume TTS API endpoint - EXACT WORKING URL
            tts_url = "https://api.hume.ai/v0/tts"
            
            # Request payload - EXACT WORKING FORMAT
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
                
                # EXACT WORKING PARSING: Audio is at generations[0].audio
                if "generations" in response_data and len(response_data["generations"]) > 0:
                    generation = response_data["generations"][0]
                    print(f"Generation Keys: {list(generation.keys())}")
                    
                    if "audio" in generation:
                        # Audio is already base64 encoded in the response
                        audio_data = generation["audio"]
                        print("✅ Audio found in generation.audio")
                        print(f"✅ Audio length: {len(audio_data)} characters")
                        return audio_data
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
    """Serve the voice interface"""
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "ora_working_hume_backend",
        "hume_available": bool(HUME_API_KEY),
        "openai_available": bool(OPENAI_API_KEY),
        "tts_endpoint": "https://api.hume.ai/v0/tts",
        "response_parsing": "generations[0].audio",
        "working_implementation": True
    })

@app.route("/voice_conversation", methods=["POST"])
def voice_conversation():
    """Handle voice-to-voice conversation with working Hume TTS"""
    
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
        
        # Enhanced emotion analysis
        emotion_result = hume.analyze_voice_emotion_with_hume(user_input)
        emotions = emotion_result.get("emotions", {"neutral": 0.7})
        emotional_context = emotion_result.get("emotional_context", "")
        empathy_guidance = emotion_result.get("empathy_guidance", "")
        
        print(f"🎭 Detected emotions: {emotions}")
        
        # Generate balanced empathic and conversational response
        response_text, detected_emotion, emotion_confidence = hume.generate_empathic_response(
            user_input, emotions, conversation_history, emotional_context, empathy_guidance
        )
        
        print(f"💬 Generated response: {response_text}")
        
        # Convert to speech using WORKING Hume TTS implementation
        audio_data = hume.text_to_speech_hume(response_text, detected_emotion)
        
        if audio_data:
            print("✅ Audio generated successfully")
            return jsonify({
                "success": True,
                "response": response_text,
                "audio_response": audio_data,  # Base64 encoded audio
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "method": "hume_tts_working"
            })
        else:
            print("❌ Audio generation failed")
            return jsonify({
                "success": True,
                "response": response_text,
                "emotion": detected_emotion,
                "emotion_confidence": emotion_confidence,
                "error": "Audio generation failed"
            })
        
    except Exception as e:
        print(f"❌ Voice conversation error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Starting ORA with working Hume TTS backend...")
    app.run(host="0.0.0.0", port=5000, debug=True)




