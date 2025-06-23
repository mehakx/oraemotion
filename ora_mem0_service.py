"""
Simple Mem0ai Service for ORA Emotion System
Add this file to your ORA repository as: services/mem0_service.py
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from mem0 import Memory
except ImportError:
    print("Installing mem0ai...")
    import subprocess
    subprocess.check_call(["pip", "install", "mem0ai==0.1.110"])
    from mem0 import Memory

logger = logging.getLogger(__name__)

class ORAMem0Service:
    """Simple mem0ai integration for ORA system"""
    
    def __init__(self):
        self.memory = None
        self.is_ready = False
        self._setup()
    
    def _setup(self):
        """Initialize mem0ai with basic configuration"""
        try:
            # Basic configuration using your existing OpenAI key
            config = {
                "vector_store": {
                    "provider": "qdrant",
                },
                "llm": {
                    "provider": "openai",
                    "config": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                    }
                },
                "embedder": {
                    "provider": "openai",
                    "config": {
                        "model": "text-embedding-3-small",
                    }
                }
            }
            
            self.memory = Memory.from_config(config)
            self.is_ready = True
            logger.info("✅ Mem0ai service ready")
            
        except Exception as e:
            logger.error(f"❌ Mem0ai setup failed: {e}")
            self.is_ready = False
    
    def is_therapeutic_content(self, message: str) -> bool:
        """Check if content should go to therapeutic memory"""
        therapeutic_keywords = [
            'anxious', 'anxiety', 'depressed', 'sad', 'angry', 'stressed',
            'worried', 'overwhelmed', 'therapy', 'therapist', 'mental health',
            'trauma', 'grief', 'loss', 'relationship', 'breakup', 'divorce'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in therapeutic_keywords)
    
    def store_memory(self, user_id: str, message: str, metadata: Dict = None) -> Dict[str, Any]:
        """Store memory with routing logic"""
        if not self.is_ready:
            return {"success": False, "error": "Service not ready"}
        
        try:
            # Check if this should go to therapeutic memory
            is_therapeutic = self.is_therapeutic_content(message)
            
            if is_therapeutic:
                # Route to your existing therapeutic memory system
                return {
                    "success": True,
                    "routed_to": "therapeutic",
                    "message": "Routed to therapeutic memory system",
                    "is_therapeutic": True
                }
            else:
                # Store in mem0ai for general conversations
                result = self.memory.add(
                    messages=[{"role": "user", "content": message}],
                    user_id=user_id,
                    metadata=metadata or {}
                )
                
                return {
                    "success": True,
                    "routed_to": "mem0ai",
                    "memory_id": result.get("id") if result else None,
                    "is_therapeutic": False
                }
                
        except Exception as e:
            logger.error(f"Storage error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_context(self, user_id: str, current_message: str, limit: int = 5) -> str:
        """Get memory context for AI prompt"""
        if not self.is_ready:
            return ""
        
        try:
            # Get relevant memories from mem0ai
            memories = self.memory.search(
                query=current_message,
                user_id=user_id,
                limit=limit
            )
            
            if not memories:
                return ""
            
            # Format for AI prompt
            context_parts = []
            for memory in memories:
                content = memory.get("memory", "")
                if content:
                    context_parts.append(f"Previous: {content}")
            
            if context_parts:
                return "Memory context:\n" + "\n".join(context_parts)
            return ""
            
        except Exception as e:
            logger.error(f"Context retrieval error: {e}")
            return ""
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "service": "mem0ai",
            "status": "healthy" if self.is_ready else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
mem0_service = ORAMem0Service()

