"""
Mem0ai Flask Routes for ORA Emotion System
Place this file in your repository root: mem0_routes.py
(Same directory as enhanced_app.py)

This module provides Flask routes that integrate mem0ai with your existing
ORA system while preserving your memory-api therapeutic functionality.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
import logging
from datetime import datetime

# Import the ORA-specific mem0 service
from mem0_service import ora_mem0_service

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint for mem0ai routes
mem0_bp = Blueprint('ora_mem0', __name__)

@mem0_bp.route('/api/ora/mem0/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Health check endpoint for ORA mem0ai integration
    Compatible with your existing monitoring setup
    """
    try:
        health_status = ora_mem0_service.health_check()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        # Add ORA-specific health information
        health_status.update({
            "ora_integration": "active",
            "therapeutic_routing": "enabled",
            "memory_api_preserved": True
        })
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"ORA mem0ai health check error: {str(e)}")
        return jsonify({
            "service": "ora_mem0ai",
            "status": "error",
            "error": str(e),
            "ora_integration": "failed"
        }), 500

@mem0_bp.route('/api/ora/mem0/store', methods=['POST'])
@cross_origin()
def store_memory():
    """
    Store memory with ORA's intelligent routing system
    Routes therapeutic content to memory-api, general content to mem0ai
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        message = data.get('message')
        metadata = data.get('metadata', {})
        
        # Add ORA-specific metadata
        metadata.update({
            "source_app": "ora_emotion",
            "enhanced_app_version": "latest",
            "request_timestamp": datetime.utcnow().isoformat()
        })
        
        if not user_id or not message:
            return jsonify({
                "error": "user_id and message are required",
                "ora_system": "validation_failed"
            }), 400
        
        # Store memory with intelligent routing
        result = ora_mem0_service.store_memory(user_id, message, metadata)
        
        # Add ORA-specific response information
        result.update({
            "ora_system": "hybrid_memory",
            "therapeutic_api_available": True,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"ORA memory storage error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "storage_failed"
        }), 500

@mem0_bp.route('/api/ora/mem0/context', methods=['POST'])
@cross_origin()
def get_memory_context():
    """
    Get memory context for ORA AI responses
    Enhances your existing AI with relevant memory context
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        message = data.get('message')
        limit = data.get('limit', 5)
        
        if not user_id or not message:
            return jsonify({
                "error": "user_id and message are required",
                "ora_system": "validation_failed"
            }), 400
        
        # Get memory context from mem0ai
        context = ora_mem0_service.get_memory_context(user_id, message, limit)
        
        # Check if this is therapeutic content
        is_therapeutic = ora_mem0_service.is_therapeutic_content(message, data.get('metadata', {}))
        
        response = {
            "success": True,
            "memory_context": context,
            "has_context": bool(context),
            "is_therapeutic_content": is_therapeutic,
            "ora_system": "context_retrieved",
            "source": "mem0ai" if context else "no_memories",
            "note": "Therapeutic memories handled by memory-api" if is_therapeutic else "General memories from mem0ai",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"ORA context retrieval error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "context_failed"
        }), 500

@mem0_bp.route('/api/ora/mem0/memories/<user_id>', methods=['GET'])
@cross_origin()
def get_user_memories(user_id):
    """
    Get memories for a specific user from mem0ai
    Note: Therapeutic memories are in memory-api system
    """
    try:
        query = request.args.get('query')
        limit = int(request.args.get('limit', 10))
        
        result = ora_mem0_service.get_memories(user_id, query, limit)
        
        if result.get('success'):
            result.update({
                "ora_system": "memories_retrieved",
                "source": "mem0ai_general_memories",
                "note": "Therapeutic memories available via memory-api endpoints",
                "therapeutic_api_path": "/memory-api/src/routes/"
            })
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"ORA memory retrieval error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "retrieval_failed"
        }), 500

@mem0_bp.route('/api/ora/mem0/user/<user_id>/delete', methods=['DELETE'])
@cross_origin()
def delete_user_memories(user_id):
    """
    Delete user memories from mem0ai (GDPR compliance)
    Note: This only deletes general memories, not therapeutic memories
    """
    try:
        result = ora_mem0_service.delete_user_memories(user_id)
        
        if result.get('success'):
            result.update({
                "ora_system": "memories_deleted",
                "scope": "general_memories_only",
                "note": "Therapeutic memories in memory-api not affected",
                "therapeutic_deletion": "Use memory-api endpoints for therapeutic data"
            })
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"ORA memory deletion error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "deletion_failed"
        }), 500

@mem0_bp.route('/api/ora/routing/analyze', methods=['POST'])
@cross_origin()
def analyze_content_routing():
    """
    Analyze content to see how ORA's routing system would handle it
    Useful for testing and debugging routing decisions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        message = data.get('message')
        metadata = data.get('metadata', {})
        
        if not message:
            return jsonify({
                "error": "message is required",
                "ora_system": "validation_failed"
            }), 400
        
        # Analyze routing decision
        is_therapeutic = ora_mem0_service.is_therapeutic_content(message, metadata)
        
        response = {
            "success": True,
            "message": message,
            "is_therapeutic": is_therapeutic,
            "would_route_to": "memory-api/therapeutic_service" if is_therapeutic else "mem0ai",
            "routing_reason": "Therapeutic keywords detected" if is_therapeutic else "General conversation",
            "ora_system": "routing_analyzed",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"ORA routing analysis error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "analysis_failed"
        }), 500

# Make.com Compatible Endpoints
@mem0_bp.route('/api/make/ora/memory-enhanced', methods=['POST'])
@cross_origin()
def make_memory_enhanced():
    """
    Enhanced Make.com endpoint for ORA system
    Drop-in replacement for your existing Make.com memory endpoint
    Provides hybrid memory functionality with enhanced context
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id')
        user_message = data.get('user_message')
        ai_response = data.get('ai_response', '')
        emotional_tone = data.get('emotional_tone', '')
        conversation_type = data.get('conversation_type', '')
        
        if not user_id or not user_message:
            return jsonify({
                "error": "user_id and user_message are required",
                "ora_system": "make_validation_failed"
            }), 400
        
        # Prepare metadata for ORA system
        metadata = {
            "emotional_tone": emotional_tone,
            "conversation_type": conversation_type,
            "ai_response": ai_response,
            "make_com_timestamp": data.get('timestamp', ''),
            "source": "make_com_workflow",
            "ora_enhanced": True
        }
        
        # Get memory context BEFORE storing new memory
        memory_context = ora_mem0_service.get_memory_context(user_id, user_message, 5)
        
        # Store the new conversation
        storage_result = ora_mem0_service.store_memory(user_id, user_message, metadata)
        
        # Determine if this was therapeutic content
        is_therapeutic = ora_mem0_service.is_therapeutic_content(user_message, metadata)
        
        # Get routing statistics
        routing_stats = ora_mem0_service.get_routing_stats(user_id)
        
        # Prepare enhanced response for Make.com
        response = {
            "success": True,
            "memory_context": memory_context,
            "has_memories": bool(memory_context),
            "storage_result": storage_result,
            "routed_to": storage_result.get("routed_to", "unknown"),
            "is_therapeutic": is_therapeutic,
            "ora_system": "make_enhanced_complete",
            "routing_stats": routing_stats,
            "performance_metrics": {
                "context_length": len(memory_context) if memory_context else 0,
                "routing_decision": "therapeutic" if is_therapeutic else "general",
                "timestamp": datetime.utcnow().isoformat()
            },
            "integration_info": {
                "therapeutic_system": "memory-api preserved",
                "general_system": "mem0ai enhanced",
                "hybrid_routing": "active"
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"ORA Make.com enhanced endpoint error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "make_enhanced_failed"
        }), 500

@mem0_bp.route('/api/make/ora/user-summary/<user_id>', methods=['GET'])
@cross_origin()
def make_user_summary(user_id):
    """
    Get user summary for Make.com workflows
    Provides insights about user's memory and conversation patterns
    """
    try:
        # Get general memories from mem0ai
        memories_result = ora_mem0_service.get_memories(user_id, limit=20)
        
        if not memories_result.get('success'):
            return jsonify({
                "error": "Failed to retrieve user memories",
                "ora_system": "summary_failed"
            }), 400
        
        memories = memories_result.get('memories', [])
        
        # Analyze memory patterns
        total_memories = len(memories)
        recent_memories = [m for m in memories if m.get('created_at')]  # Would need date filtering
        
        # Create user summary
        summary = {
            "success": True,
            "user_id": user_id,
            "general_memory_count": total_memories,
            "has_conversation_history": total_memories > 0,
            "memory_source": "mem0ai_general_only",
            "ora_system": "user_summary_complete",
            "note": "Therapeutic memories counted separately in memory-api",
            "summary_timestamp": datetime.utcnow().isoformat(),
            "integration_status": {
                "mem0ai_memories": total_memories,
                "therapeutic_api": "available_separately",
                "hybrid_system": "active"
            }
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"ORA user summary error: {str(e)}")
        return jsonify({
            "error": str(e),
            "ora_system": "summary_failed"
        }), 500

def register_ora_mem0_routes(app):
    """
    Register ORA mem0ai routes with your Flask application
    Call this function from your enhanced_app.py
    
    Usage in enhanced_app.py:
        from mem0_routes import register_ora_mem0_routes
        register_ora_mem0_routes(app)
    """
    try:
        # Register the blueprint
        app.register_blueprint(mem0_bp)
        
        # Log successful registration
        app.logger.info("✅ ORA Mem0ai routes registered successfully")
        app.logger.info("📍 Available endpoints:")
        app.logger.info("   - /api/ora/mem0/health (Health check)")
        app.logger.info("   - /api/ora/mem0/store (Store memory)")
        app.logger.info("   - /api/ora/mem0/context (Get context)")
        app.logger.info("   - /api/make/ora/memory-enhanced (Make.com enhanced)")
        app.logger.info("   - /api/make/ora/user-summary/<user_id> (User summary)")
        app.logger.info("🔄 Hybrid routing: Therapeutic → memory-api, General → mem0ai")
        
        return True
        
    except Exception as e:
        app.logger.error(f"❌ Failed to register ORA mem0ai routes: {str(e)}")
        return False

# For backward compatibility, also provide the blueprint directly
ora_mem0_blueprint = mem0_bp

