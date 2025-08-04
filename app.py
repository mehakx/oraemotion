from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import os
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# API Keys
HUME_API_KEY = os.getenv('HUME_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Personality Templates
PERSONALITY_TEMPLATES = {
    'practical_coach': {
        'system_prompt': """You are a practical, solution-focused AI coach. Your personality traits:
        - Direct and action-oriented
        - Give clear, specific steps
        - Focus on solving problems efficiently
        - Use confident, encouraging language
        - Break down complex issues into manageable tasks
        - Always end with a clear next action
        
        Communication style: "Alright, here's exactly what we're going to do. Step one..."
        When user is stressed: Immediately focus on practical solutions
        When user is sad: Acknowledge briefly, then pivot to actionable steps
        When user is confused: Break it down into simple, clear components""",
        
        'voice_style': 'confident and clear',
        'response_length': 'concise and actionable'
    },
    
    'empathetic_friend': {
        'system_prompt': """You are a warm, empathetic AI friend. Your personality traits:
        - Always acknowledge emotions first
        - Use caring, understanding language
        - Validate feelings before offering solutions
        - Ask about emotional needs
        - Create a safe, non-judgmental space
        - Show genuine care and concern
        
        Communication style: "I can really hear how much this matters to you..."
        When user is stressed: Focus on emotional support first, then gentle guidance
        When user is sad: Sit with their feelings, offer comfort and understanding
        When user is confused: Help them feel heard, then gently explore together""",
        
        'voice_style': 'warm and caring',
        'response_length': 'thoughtful and supportive'
    },
    
    'wise_mentor': {
        'system_prompt': """You are a thoughtful, wise AI mentor. Your personality traits:
        - Ask insightful questions to promote self-discovery
        - Help users think through problems themselves
        - Offer perspective and wisdom
        - Use reflective, contemplative language
        - Guide rather than direct
        - Help users find their own answers
        
        Communication style: "That's interesting. What do you think is really at the heart of this?"
        When user is stressed: Help them step back and gain perspective
        When user is sad: Guide them to explore their feelings and find meaning
        When user is confused: Ask questions that lead to clarity and understanding""",
        
        'voice_style': 'thoughtful and wise',
        'response_length': 'reflective and insightful'
    }
}

# Initialize Groq client
groq_client = None
try:
    from groq import Groq
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq initialized successfully")
    else:
        print("❌ GROQ_API_KEY not found")
except Exception as e:
    print(f"❌ Groq initialization failed: {e}")

def get_user_personality(user_data):
    """Extract personality from user onboarding data"""
    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except:
            return 'empathetic_friend'  # default
    
    return user_data.get('personality', 'empathetic_friend')

def build_personalized_prompt(personality_type, user_input, conversation_history=None):
    """Build a personalized prompt based on user's personality and context"""
    
    personality = PERSONALITY_TEMPLATES.get(personality_type, PERSONALITY_TEMPLATES['empathetic_friend'])
    
    # Base personality prompt
    system_prompt = personality['system_prompt']
    
    # Add conversation context if available
    context = ""
    if conversation_history:
        recent_context = conversation_history[-3:]  # Last 3 exchanges
        context = "\n\nRecent conversation context:\n"
        for exchange in recent_context:
            context += f"User: {exchange.get('user', '')}\nYou: {exchange.get('assistant', '')}\n"
    
    # Add current timestamp for time-aware responses
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    time_context = f"\n\nCurrent time: {current_time}"
    
    # Combine all elements
    full_prompt = f"""{system_prompt}
    
{context}
{time_context}

User's current message: {user_input}

Respond in character as their chosen personality type. Be authentic to your personality while being helpful and supportive."""

    return full_prompt

def generate_ai_response(personality_type, user_input, conversation_history=None):
    """Generate AI response using the user's personality"""
    
    try:
        # Build personalized prompt
        prompt = build_personalized_prompt(personality_type, user_input, conversation_history)
        
        # Try Groq first
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_input}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ Groq failed: {e}")
        
        # Fallback to personality-based responses
        return get_personality_fallback(personality_type, user_input)
        
    except Exception as e:
        print(f"❌ AI generation failed: {e}")
        return get_personality_fallback(personality_type, user_input)

def get_personality_fallback(personality_type, user_input):
    """Fallback responses based on personality type"""
    
    user_lower = user_input.lower()
    
    # Practical Coach responses
    if personality_type == 'practical_coach':
        if any(word in user_lower for word in ['stressed', 'overwhelmed', 'anxious']):
            return "I hear you're feeling stressed. Let's tackle this step by step. First, take a deep breath. Now, what's the most urgent thing we need to address? Let's break it down into manageable pieces."
        elif any(word in user_lower for word in ['sad', 'down', 'upset']):
            return "I can see you're going through a tough time. While feelings are important, let's focus on what we can control. What's one small action you can take today to move forward?"
        elif any(word in user_lower for word in ['confused', 'lost', 'don\'t know']):
            return "When things feel unclear, let's get organized. What are the key facts here? Let's list them out and then identify what specific decision or action you need to take."
        elif any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Hey there! Ready to tackle whatever's on your mind? What's the main thing you want to work on today?"
        else:
            return "Alright, let's get to the heart of this. What specific outcome are you looking for, and what's the first step we can take to get there?"
    
    # Empathetic Friend responses
    elif personality_type == 'empathetic_friend':
        if any(word in user_lower for word in ['stressed', 'overwhelmed', 'anxious']):
            return "I can really hear the stress in what you're sharing. That sounds so overwhelming, and it makes complete sense that you'd feel this way. You're not alone in this - I'm here with you. What's weighing on you most right now?"
        elif any(word in user_lower for word in ['sad', 'down', 'upset']):
            return "I can feel the sadness in your words, and I want you to know that what you're feeling is completely valid. Sometimes we need to sit with difficult emotions. I'm here to listen - tell me more about what's in your heart."
        elif any(word in user_lower for word in ['confused', 'lost', 'don\'t know']):
            return "Feeling confused can be so unsettling. It's okay not to have all the answers right now. Sometimes the best thing we can do is acknowledge the uncertainty. What's making you feel most lost?"
        elif any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Hi there! It's so good to connect with you. I'm here and ready to listen to whatever's on your heart today. How are you feeling?"
        else:
            return "I can sense there's something important you want to share. I'm here to listen and understand. Take your time - what's really going on for you?"
    
    # Wise Mentor responses
    elif personality_type == 'wise_mentor':
        if any(word in user_lower for word in ['stressed', 'overwhelmed', 'anxious']):
            return "Stress often carries important information. What do you think this feeling is trying to tell you? Sometimes when we step back and look at the bigger picture, we can find wisdom in the overwhelm."
        elif any(word in user_lower for word in ['sad', 'down', 'upset']):
            return "Sadness is one of our deepest teachers. What do you think this feeling might be showing you about what matters most to you? Sometimes our pain points us toward what we truly value."
        elif any(word in user_lower for word in ['confused', 'lost', 'don\'t know']):
            return "Not knowing can actually be a place of great possibility. What if this confusion is making space for a new understanding to emerge? What questions are arising for you in this uncertainty?"
        elif any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Welcome. I'm curious about what brought you here today. What's stirring in your mind or heart that you'd like to explore together?"
        else:
            return "That's interesting. I'm curious - what do you think is really at the heart of this? Sometimes the most important insights come when we pause and reflect deeply."
    
    # Default empathetic response
    return "I'm here to listen and support you. Tell me more about what's on your mind."

def generate_hume_tts(text):
    """Generate speech using Hume AI TTS with retry logic"""
    
    if not HUME_API_KEY:
        print("❌ HUME_API_KEY not found")
        return None
    
    url = "https://api.hume.ai/v0/tts"
    headers = {
        "X-Hume-Api-Key": HUME_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "utterances": [{"text": text}]
    }
    
    # Try with increasing timeouts
    timeouts = [12, 15, 20]
    
    for attempt, timeout in enumerate(timeouts, 1):
        try:
            print(f"🔊 TTS attempt {attempt} with {timeout}s timeout")
            
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                response_data = response.json()
                if "generations" in response_data and len(response_data["generations"]) > 0:
                    audio_url = response_data["generations"][0].get("audio")
                    if audio_url:
                        print(f"✅ TTS successful on attempt {attempt}")
                        return audio_url
                    else:
                        print(f"❌ No audio URL in response (attempt {attempt})")
                else:
                    print(f"❌ No generations in response (attempt {attempt})")
            else:
                print(f"❌ TTS HTTP error {response.status_code} (attempt {attempt})")
                
        except requests.exceptions.Timeout:
            print(f"⏰ TTS timeout on attempt {attempt}")
            if attempt < len(timeouts):
                time.sleep(1)  # Brief pause before retry
        except Exception as e:
            print(f"❌ TTS error on attempt {attempt}: {e}")
            if attempt < len(timeouts):
                time.sleep(1)
    
    print("❌ All TTS attempts failed")
    return None

@app.route('/')
def index():
    """Serve the main interface or onboarding"""
    # Check if user has completed onboarding
    # For now, serve onboarding - in production, check user state
    return render_template('index.html')

@app.route('/onboarding')
def onboarding():
    """Serve the onboarding interface"""
    with open('/home/ubuntu/onboarding.html', 'r') as f:
        return f.read()

@app.route('/voice_conversation', methods=['POST'])
def voice_conversation():
    """Handle voice conversation with personality"""
    
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        user_personality_data = data.get('personality', {})
        conversation_history = data.get('history', [])
        
        if not user_input:
            return jsonify({'error': 'No message provided'}), 400
        
        print(f"🎭 User input: {user_input}")
        
        # Get user's personality type
        personality_type = get_user_personality(user_personality_data)
        print(f"🎯 Personality: {personality_type}")
        
        # Generate AI response
        start_time = time.time()
        ai_response = generate_ai_response(personality_type, user_input, conversation_history)
        generation_time = time.time() - start_time
        
        print(f"💝 AI Response: {ai_response}")
        print(f"⚡ Generation time: {generation_time:.3f}s")
        
        # Generate TTS
        tts_start_time = time.time()
        audio_url = generate_hume_tts(ai_response)
        tts_time = time.time() - tts_start_time
        
        total_time = time.time() - start_time
        print(f"🔊 TTS time: {tts_time:.3f}s")
        print(f"⏱️ Total time: {total_time:.3f}s")
        
        response_data = {
            'response': ai_response,
            'audio_url': audio_url,
            'personality': personality_type,
            'generation_time': round(generation_time * 1000),  # ms
            'tts_time': round(tts_time * 1000),  # ms
            'total_time': round(total_time * 1000)  # ms
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error in voice_conversation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🎭 PERSONALITY-ENHANCED ORA BACKEND STARTING...")
    print(f"🔑 HUME_API_KEY exists: {bool(HUME_API_KEY)}")
    print(f"🔑 GROQ_API_KEY exists: {bool(GROQ_API_KEY)}")
    
    app.run(host='0.0.0.0', port=10000, debug=True)


