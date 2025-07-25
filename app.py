from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
import base64
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import threading
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Configuration
HUME_API_KEY = os.environ.get('HUME_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Thread pool for parallel processing
executor = ThreadPoolExecutor(max_workers=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice_conversation', methods=['POST'])
def voice_conversation():
    """OPTIMIZED: Handle voice-to-voice conversation with parallel processing"""
    start_time = time.time()
    
    try:
        # Parse request data
        data = request.get_json()
        user_input = data.get("message", "")
        conversation_history = data.get("conversation_history", [])
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        print(f"📥 Received JSON message: {user_input}")
        print(f"📚 Conversation history: {len(conversation_history)} turns")
        
        # OPTIMIZATION 1: Parallel emotion analysis and response generation
        def analyze_emotion_task():
            return analyze_voice_emotion_fast(user_input)
        
        def generate_response_task():
            return generate_empathic_response_fast(user_input, conversation_history)
        
        # Submit both tasks in parallel
        emotion_future = executor.submit(analyze_emotion_task)
        response_future = executor.submit(generate_response_task)
        
        # Get results (this will wait for both to complete)
        emotion_result = emotion_future.result(timeout=10)  # 10 second timeout
        response_text = response_future.result(timeout=15)  # 15 second timeout
        
        emotion_name = emotion_result.get('emotion_name', 'neutral')
        emotion_confidence = emotion_result.get('emotion_confidence', 0.5)
        
        print(f"🎭 Detected emotion: {emotion_name} ({emotion_confidence:.2f})")
        print(f"💬 Generated response: {response_text[:100]}...")
        
        # OPTIMIZATION 2: Generate TTS audio (this is the slowest part)
        audio_response = generate_hume_tts_fast(response_text)
        
        processing_time = time.time() - start_time
        print(f"⚡ Total processing time: {processing_time:.2f} seconds")
        
        return jsonify({
            "success": True,
            "assistant_response": response_text,
            "audio_response": audio_response,
            "dominant_emotion": emotion_name,
            "emotion_confidence": emotion_confidence,
            "processing_time": processing_time
        })
        
    except Exception as e:
        print(f"❌ Error in voice_conversation: {str(e)}")
        processing_time = time.time() - start_time
        return jsonify({
            "error": str(e),
            "processing_time": processing_time
        }), 500

def analyze_voice_emotion_fast(user_input):
    """OPTIMIZED: Fast emotion analysis with caching and fallbacks"""
    try:
        # OPTIMIZATION: Use OpenAI for faster emotion analysis (no external API call to Hume)
        if openai_client:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Faster than gpt-4
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the emotional content of the user's message. Respond with ONLY a JSON object containing 'emotion_name' (one word: happy, sad, angry, fear, surprise, disgust, neutral, excited, confused, frustrated, anxious, calm) and 'emotion_confidence' (0.0-1.0). No other text."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                max_tokens=50,  # Minimal tokens for speed
                temperature=0.1  # Low temperature for consistent results
            )
            
            emotion_text = response.choices[0].message.content.strip()
            emotion_data = json.loads(emotion_text)
            
            return {
                'emotion_name': emotion_data.get('emotion_name', 'neutral'),
                'emotion_confidence': float(emotion_data.get('emotion_confidence', 0.5)),
                'method': 'openai_fast'
            }
    except Exception as e:
        print(f"⚠️ OpenAI emotion analysis failed: {e}")
    
    # FALLBACK: Fast keyword-based emotion detection
    return analyze_emotion_keywords_fast(user_input)

def analyze_emotion_keywords_fast(user_input):
    """OPTIMIZED: Ultra-fast keyword-based emotion detection"""
    user_input_lower = user_input.lower()
    
    # Optimized emotion keywords (most common first)
    emotion_keywords = {
        'happy': ['happy', 'great', 'awesome', 'amazing', 'wonderful', 'fantastic', 'good', 'excited', 'love', 'perfect'],
        'sad': ['sad', 'down', 'depressed', 'upset', 'hurt', 'crying', 'terrible', 'awful', 'bad', 'disappointed'],
        'angry': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'hate', 'stupid', 'ridiculous', 'pissed'],
        'anxious': ['worried', 'nervous', 'anxious', 'scared', 'afraid', 'stress', 'panic', 'overwhelmed'],
        'confused': ['confused', 'lost', 'weird', 'strange', 'don\'t understand', 'unclear', 'puzzled'],
        'excited': ['excited', 'thrilled', 'pumped', 'can\'t wait', 'amazing', 'incredible'],
        'calm': ['calm', 'peaceful', 'relaxed', 'fine', 'okay', 'alright', 'good']
    }
    
    # Quick scan for emotion keywords
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in user_input_lower:
                confidence = 0.7 if len(keyword) > 4 else 0.6  # Longer keywords = higher confidence
                return {
                    'emotion_name': emotion,
                    'emotion_confidence': confidence,
                    'method': 'keywords_fast'
                }
    
    return {
        'emotion_name': 'neutral',
        'emotion_confidence': 0.5,
        'method': 'default'
    }

def generate_empathic_response_fast(user_input, conversation_history):
    """OPTIMIZED: Fast response generation with streamlined prompting"""
    try:
        if not openai_client:
            return get_fast_fallback_response(user_input)
        
        # OPTIMIZATION: Streamlined conversation history (last 6 messages only)
        recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
        
        # OPTIMIZATION: Simplified system prompt for faster processing
        system_prompt = """You are ORA, an empathetic AI companion. Be natural, caring, and conversational.

RESPONSE GUIDELINES:
- Answer questions directly and helpfully
- Acknowledge emotions when present
- Keep responses concise (1-2 sentences max)
- Be warm and friendly
- Ask follow-up questions to keep conversation flowing

Respond naturally as a caring friend would."""

        # Build messages efficiently
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history
        for msg in recent_history:
            if msg.get('role') in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # OPTIMIZATION: Use gpt-3.5-turbo for speed, optimized parameters
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,  # Shorter responses for speed
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"❌ OpenAI response generation error: {e}")
        return get_fast_fallback_response(user_input)

def get_fast_fallback_response(user_input):
    """OPTIMIZED: Ultra-fast fallback responses"""
    user_lower = user_input.lower()
    
    # Quick pattern matching for common queries
    if any(word in user_lower for word in ['how are you', 'how\'re you']):
        return "I'm doing well, thank you for asking! How are you feeling today?"
    
    if any(word in user_lower for word in ['who are you', 'what are you']):
        return "I'm ORA, your AI companion. I'm here to chat and listen to whatever's on your mind."
    
    if any(word in user_lower for word in ['where are you from', 'where do you live']):
        return "I exist in the digital realm, but I'm here with you right now. What about you - where are you from?"
    
    if any(word in user_lower for word in ['sad', 'down', 'upset', 'hurt']):
        return "I can hear that you're going through a tough time. I'm here to listen. What's been weighing on you?"
    
    if any(word in user_lower for word in ['happy', 'great', 'good', 'amazing']):
        return "That's wonderful to hear! I love that you're feeling good. What's been going well for you?"
    
    if any(word in user_lower for word in ['confused', 'lost', 'weird', 'strange']):
        return "It sounds like something's feeling unclear for you. I'm here to help you work through it. What's on your mind?"
    
    # Default empathetic response
    return "I hear you. Tell me more about what's going on - I'm here to listen and understand."

def generate_hume_tts_fast(text):
    """OPTIMIZED: Fast Hume TTS generation with error handling"""
    if not HUME_API_KEY:
        print("⚠️ No Hume API key - using fallback")
        return None
    
    try:
        # OPTIMIZATION: Shorter text for faster TTS
        if len(text) > 200:
            text = text[:200] + "..."
        
        url = "https://api.hume.ai/v0/tts/inference"
        headers = {
            "X-Hume-Api-Key": HUME_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model": "hume-tts",
            "voice": "SAMPLE_VOICE",  # Use default voice for speed
            "format": "wav",
            "sample_rate": 22050  # Lower sample rate for faster generation
        }
        
        # OPTIMIZATION: Shorter timeout for faster failure detection
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            response_data = response.json()
            if 'audio' in response_data:
                return response_data['audio']
            elif 'generations' in response_data and len(response_data['generations']) > 0:
                return response_data['generations'][0].get('audio', '')
        
        print(f"⚠️ Hume TTS error: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"❌ Hume TTS error: {e}")
        return None

if __name__ == '__main__':
    print("🚀 Starting Optimized ORA Voice-to-Voice Application...")
    print(f"✅ Hume API Key: {'Set' if HUME_API_KEY else '❌ Missing'}")
    print(f"✅ OpenAI API Key: {'Set' if OPENAI_API_KEY else '❌ Missing'}")
    
    app.run(host='0.0.0.0', port=5000, debug=False)  # Debug=False for production speed


