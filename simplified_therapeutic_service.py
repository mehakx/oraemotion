"""
Simplified Therapeutic Service for ORA Emotion System
NO COGNEE DEPENDENCIES - Clean deployment for Render/Heroku
Place this file as: simplified_therapeutic_service.py
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TherapeuticInsight:
    insight_type: str
    content: str
    confidence: float
    timestamp: datetime
    user_id: str

@dataclass
class CrisisAssessment:
    risk_level: str  # "low", "medium", "high"
    indicators: List[str]
    immediate_actions: List[str]
    timestamp: datetime

class SimplifiedTherapeuticService:
    """
    Simplified therapeutic service without Cognee dependencies
    Uses basic SQLite storage and keyword-based analysis
    """
    
    def __init__(self):
        self.db_path = "ora_therapeutic.db"
        self.crisis_hotlines = {
            "US": "988",
            "UK": "116 123", 
            "Canada": "1-833-456-4566",
            "Australia": "13 11 14"
        }
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for therapeutic data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Therapeutic conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS therapeutic_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    emotion TEXT,
                    crisis_level TEXT DEFAULT 'low',
                    therapeutic_response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    keywords TEXT,
                    intervention_applied BOOLEAN DEFAULT 0
                )
            ''')
            
            # User therapeutic profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_therapeutic_profiles (
                    user_id TEXT PRIMARY KEY,
                    dominant_emotions TEXT,
                    crisis_history TEXT,
                    therapeutic_progress TEXT,
                    last_assessment DATETIME,
                    risk_level TEXT DEFAULT 'low'
                )
            ''')
            
            # Crisis interventions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crisis_interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    indicators TEXT,
                    actions_taken TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    outcome TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Simplified therapeutic database initialized")
            
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
    
    def detect_crisis_indicators(self, message: str, user_context: Dict = None) -> CrisisAssessment:
        """
        Simplified crisis detection using keyword matching
        No Cognee dependencies
        """
        message_lower = message.lower()
        
        # High-risk crisis indicators
        high_risk_keywords = [
            'want to die', 'kill myself', 'suicide', 'end it all',
            'better off dead', 'no point living', 'hurt myself',
            'self-harm', 'overdose', 'jump off', 'hang myself'
        ]
        
        # Medium-risk indicators
        medium_risk_keywords = [
            'hopeless', 'worthless', 'burden', 'give up',
            'can\'t go on', 'end the pain', 'no way out',
            'everyone would be better', 'tired of living'
        ]
        
        # Low-risk indicators
        low_risk_keywords = [
            'sad', 'depressed', 'anxious', 'stressed',
            'overwhelmed', 'lonely', 'frustrated'
        ]
        
        risk_level = "low"
        indicators = []
        immediate_actions = []
        
        # Check for high-risk indicators
        for keyword in high_risk_keywords:
            if keyword in message_lower:
                risk_level = "high"
                indicators.append(f"High-risk keyword: {keyword}")
                immediate_actions.extend([
                    "Contact crisis hotline immediately",
                    "Ensure user safety",
                    "Provide immediate resources"
                ])
                break
        
        # Check for medium-risk if not high-risk
        if risk_level != "high":
            for keyword in medium_risk_keywords:
                if keyword in message_lower:
                    risk_level = "medium"
                    indicators.append(f"Medium-risk keyword: {keyword}")
                    immediate_actions.extend([
                        "Provide supportive response",
                        "Offer coping strategies",
                        "Monitor closely"
                    ])
                    break
        
        # Check for low-risk indicators
        if risk_level == "low":
            for keyword in low_risk_keywords:
                if keyword in message_lower:
                    indicators.append(f"Emotional distress: {keyword}")
                    immediate_actions.extend([
                        "Provide empathetic response",
                        "Offer therapeutic techniques"
                    ])
                    break
        
        return CrisisAssessment(
            risk_level=risk_level,
            indicators=indicators,
            immediate_actions=immediate_actions,
            timestamp=datetime.now()
        )
    
    def generate_therapeutic_response(self, user_message: str, user_id: str, emotion: str = "neutral") -> Dict:
        """
        Generate simplified therapeutic response
        No Cognee dependencies - uses basic therapeutic principles
        """
        try:
            # Detect crisis level
            crisis_assessment = self.detect_crisis_indicators(user_message)
            
            # Store conversation in database
            self._store_therapeutic_conversation(user_id, user_message, emotion, crisis_assessment.risk_level)
            
            # Generate appropriate response based on crisis level
            if crisis_assessment.risk_level == "high":
                response = self._generate_crisis_response(crisis_assessment)
            elif crisis_assessment.risk_level == "medium":
                response = self._generate_supportive_response(user_message, emotion)
            else:
                response = self._generate_basic_therapeutic_response(user_message, emotion)
            
            # Add crisis assessment to response
            response["crisis_assessment"] = {
                "risk_level": crisis_assessment.risk_level,
                "indicators": crisis_assessment.indicators,
                "immediate_actions": crisis_assessment.immediate_actions
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Therapeutic response generation error: {e}")
            return {
                "response": "I'm here to support you. Could you tell me more about how you're feeling?",
                "error": str(e),
                "crisis_assessment": {"risk_level": "unknown"}
            }
    
    def _store_therapeutic_conversation(self, user_id: str, message: str, emotion: str, crisis_level: str):
        """Store therapeutic conversation in SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO therapeutic_conversations 
                (user_id, message, emotion, crisis_level, keywords)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, message, emotion, crisis_level, emotion))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Database storage error: {e}")
    
    def _generate_crisis_response(self, crisis_assessment: CrisisAssessment) -> Dict:
        """Generate immediate crisis intervention response"""
        return {
            "response": "I'm very concerned about you right now. Your life has value and there are people who want to help. Please reach out to a crisis counselor immediately.",
            "therapeutic_context": {
                "session_type": "crisis_intervention",
                "priority": "immediate_safety"
            },
            "immediate_resources": {
                "crisis_hotlines": self.crisis_hotlines,
                "emergency": "Call 911 if in immediate danger"
            },
            "safety_plan": [
                "Remove any means of self-harm",
                "Stay with someone you trust",
                "Go to emergency room if needed"
            ]
        }
    
    def _generate_supportive_response(self, message: str, emotion: str) -> Dict:
        """Generate supportive therapeutic response for medium-risk situations"""
        responses = {
            "sad": "I can hear that you're going through a really difficult time. These feelings of sadness are valid, and you don't have to face them alone.",
            "anxious": "Anxiety can feel overwhelming, but there are ways to manage these feelings. Let's focus on what you can control right now.",
            "angry": "It sounds like you're feeling really frustrated. Anger often tells us something important about our needs or boundaries.",
            "default": "I can sense you're struggling right now. Your feelings are important and valid. What would feel most helpful for you in this moment?"
        }
        
        response_text = responses.get(emotion.lower(), responses["default"])
        
        return {
            "response": response_text,
            "therapeutic_context": {
                "session_type": "supportive_therapy",
                "emotion_addressed": emotion
            },
            "coping_strategies": self._get_coping_strategies(emotion),
            "follow_up": f"Would you like to explore what's contributing to these feelings of {emotion}?"
        }
    
    def _generate_basic_therapeutic_response(self, message: str, emotion: str) -> Dict:
        """Generate basic therapeutic response for low-risk situations"""
        return {
            "response": f"Thank you for sharing that with me. I can sense you're feeling {emotion}. It takes courage to express your feelings.",
            "therapeutic_context": {
                "session_type": "general_support",
                "emotion_acknowledged": emotion
            },
            "reflection_questions": [
                "What has been most challenging for you lately?",
                "How are you taking care of yourself?",
                "What support do you have in your life right now?"
            ]
        }
    
    def _get_coping_strategies(self, emotion: str) -> List[str]:
        """Get basic coping strategies for different emotions"""
        strategies = {
            "anxious": [
                "Try deep breathing: 4 counts in, 6 counts out",
                "Ground yourself: name 5 things you can see, 4 you can touch",
                "Practice progressive muscle relaxation"
            ],
            "sad": [
                "Allow yourself to feel the emotion without judgment",
                "Reach out to a trusted friend or family member",
                "Engage in one small self-care activity"
            ],
            "angry": [
                "Take a pause before responding",
                "Try physical exercise to release tension",
                "Identify what need isn't being met"
            ],
            "default": [
                "Practice mindful breathing",
                "Connect with your support system",
                "Be gentle with yourself"
            ]
        }
        
        return strategies.get(emotion.lower(), strategies["default"])
    
    def get_user_therapeutic_summary(self, user_id: str) -> Dict:
        """Get simplified therapeutic summary for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get recent conversations
            cursor.execute('''
                SELECT emotion, crisis_level, timestamp 
                FROM therapeutic_conversations 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''', (user_id,))
            
            conversations = cursor.fetchall()
            
            # Analyze patterns
            emotions = [conv[0] for conv in conversations if conv[0]]
            crisis_levels = [conv[1] for conv in conversations if conv[1]]
            
            # Calculate basic statistics
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
            
            # Check for recent high-risk episodes
            high_risk_count = crisis_levels.count("high")
            medium_risk_count = crisis_levels.count("medium")
            
            current_risk = "low"
            if high_risk_count > 0:
                current_risk = "high"
            elif medium_risk_count > 2:
                current_risk = "medium"
            
            conn.close()
            
            return {
                "user_id": user_id,
                "conversation_count": len(conversations),
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotion_counts,
                "current_risk_level": current_risk,
                "high_risk_episodes": high_risk_count,
                "medium_risk_episodes": medium_risk_count,
                "last_conversation": conversations[0][2] if conversations else None,
                "system": "simplified_therapeutic_service"
            }
            
        except Exception as e:
            logger.error(f"❌ User summary error: {e}")
            return {"error": str(e), "user_id": user_id}
    
    def health_check(self) -> Dict:
        """Health check for simplified therapeutic service"""
        try:
            # Test database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM therapeutic_conversations")
            conversation_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                "service": "simplified_therapeutic_service",
                "status": "healthy",
                "database": "connected",
                "conversation_count": conversation_count,
                "cognee_removed": True,
                "deployment_ready": True,
                "crisis_detection": "keyword_based",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "service": "simplified_therapeutic_service",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

# Global service instance
simplified_therapeutic_service = SimplifiedTherapeuticService()

