from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import logging
from typing import Dict, Any
import traceback
from datetime import datetime

from config import Config
from ai_service import ai_service, CodeContext
from code_validator import validate_and_format_python

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend integration
CORS(app, origins=Config.CORS_ORIGINS)

# Validate configuration on startup
config_issues = Config.validate_config()
if config_issues:
    logger.warning(f"Configuration issues: {config_issues}")

@app.route("/", methods=["GET"])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SELODev Code Assist",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_services": {
            "openai": bool(Config.OPENAI_API_KEY),
            "anthropic": bool(Config.ANTHROPIC_API_KEY)
        }
    })

@app.route("/ping", methods=["GET"])
def ping():
    """Legacy ping endpoint for backward compatibility"""
    return jsonify({"status": "pong"})

@app.route("/api/complete", methods=["POST"])
def code_completion():
    """AI-powered code completion endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['file_path', 'language', 'prefix', 'suffix', 'cursor_position']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create context
        context = CodeContext(
            file_path=data['file_path'],
            language=data['language'],
            cursor_position=data['cursor_position'],
            prefix=data['prefix'],
            suffix=data['suffix'],
            surrounding_code=data.get('surrounding_code')
        )
        
        # Get completion asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(ai_service.get_code_completion(context))
        loop.close()
        
        return jsonify({
            "completion": result.completion,
            "confidence": result.confidence,
            "model_used": result.model_used,
            "processing_time": result.processing_time
        })
        
    except Exception as e:
        logger.error(f"Code completion error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/api/explain", methods=["POST"])
def explain_code():
    """Code explanation endpoint"""
    try:
        data = request.get_json()
        
        if 'code' not in data or 'language' not in data:
            return jsonify({"error": "Missing 'code' or 'language' field"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        explanation = loop.run_until_complete(
            ai_service.explain_code(data['code'], data['language'])
        )
        loop.close()
        
        return jsonify({"explanation": explanation})
        
    except Exception as e:
        logger.error(f"Code explanation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/improve", methods=["POST"])
def suggest_improvements():
    """Code improvement suggestions endpoint"""
    try:
        data = request.get_json()
        
        if 'code' not in data or 'language' not in data:
            return jsonify({"error": "Missing 'code' or 'language' field"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        suggestions = loop.run_until_complete(
            ai_service.suggest_improvements(data['code'], data['language'])
        )
        loop.close()
        
        return jsonify({"suggestions": suggestions})
        
    except Exception as e:
        logger.error(f"Code improvement error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/format", methods=["POST"])
def format_code():
    """Code formatting endpoint (enhanced from original validator)"""
    try:
        data = request.get_json()
        
        if 'code' not in data:
            return jsonify({"error": "Missing 'code' field"}), 400
        
        language = data.get('language', 'python')
        
        if language == 'python':
            formatted_code = validate_and_format_python(data['code'])
            return jsonify({
                "formatted_code": formatted_code,
                "language": language,
                "formatter_used": "black + isort"
            })
        else:
            # For now, return original code for non-Python languages
            return jsonify({
                "formatted_code": data['code'],
                "language": language,
                "formatter_used": "none (language not supported yet)"
            })
        
    except Exception as e:
        logger.error(f"Code formatting error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/languages", methods=["GET"])
def supported_languages():
    """Get list of supported programming languages"""
    return jsonify({
        "languages": Config.SUPPORTED_LANGUAGES,
        "ai_completion": True,
        "formatting": {
            "python": True,
            "javascript": False,  # TODO: Add JS formatting
            "typescript": False,  # TODO: Add TS formatting
        }
    })

@app.route("/api/status", methods=["GET"])
def system_status():
    """Detailed system status endpoint"""
    return jsonify({
        "service": "SELODev Code Assist",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "code_completion": True,
            "code_explanation": True,
            "code_improvement": True,
            "code_formatting": True,
            "file_watching": True
        },
        "ai_services": {
            "openai_available": bool(Config.OPENAI_API_KEY),
            "anthropic_available": bool(Config.ANTHROPIC_API_KEY),
            "default_model": Config.DEFAULT_AI_MODEL
        },
        "configuration": {
            "max_file_size_mb": Config.MAX_FILE_SIZE_MB,
            "supported_languages": Config.SUPPORTED_LANGUAGES
        },
        "timestamp": datetime.utcnow().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

# OpenAI-compatible endpoints for Continue extension integration
@app.route("/api/v1/chat/completions", methods=["POST"])
def openai_compatible_chat():
    """OpenAI-compatible chat completions endpoint for Continue extension"""
    try:
        data = request.get_json()
        
        # Extract the last user message
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
            
        last_message = messages[-1]
        if last_message.get('role') != 'user':
            return jsonify({"error": "Last message must be from user"}), 400
            
        content = last_message.get('content', '')
        
        # Detect if this is a code completion request
        if '<CURSOR>' in content or 'complete' in content.lower():
            # Parse as code completion
            lines = content.split('\n')
            cursor_line = -1
            prefix_lines = []
            suffix_lines = []
            
            for i, line in enumerate(lines):
                if '<CURSOR>' in line:
                    cursor_line = i
                    prefix_lines = lines[:i]
                    prefix_lines.append(line.split('<CURSOR>')[0])
                    suffix_lines = [line.split('<CURSOR>')[1]] + lines[i+1:]
                    break
            
            if cursor_line == -1:
                # No cursor found, treat as explanation request
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                explanation = loop.run_until_complete(
                    ai_service.explain_code(content, 'python')
                )
                loop.close()
                
                return jsonify({
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": explanation
                        },
                        "finish_reason": "stop"
                    }],
                    "model": "selodev-local",
                    "usage": {"total_tokens": 0}
                })
            
            # Create context for completion
            context = CodeContext(
                file_path="untitled.py",
                language="python",
                cursor_position=len('\n'.join(prefix_lines)),
                prefix='\n'.join(prefix_lines),
                suffix='\n'.join(suffix_lines)
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(ai_service.get_code_completion(context))
            loop.close()
            
            return jsonify({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result.completion
                    },
                    "finish_reason": "stop"
                }],
                "model": result.model_used,
                "usage": {"total_tokens": 0}
            })
        
        else:
            # Treat as general code question
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            explanation = loop.run_until_complete(
                ai_service.explain_code(content, 'python')
            )
            loop.close()
            
            return jsonify({
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": explanation
                    },
                    "finish_reason": "stop"
                }],
                "model": "selodev-local",
                "usage": {"total_tokens": 0}
            })
            
    except Exception as e:
        logger.error(f"OpenAI-compatible endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/completions", methods=["POST"])
def openai_compatible_completions():
    """OpenAI-compatible completions endpoint for Continue extension"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Simple completion - treat as code completion
        context = CodeContext(
            file_path="untitled.py",
            language="python",
            cursor_position=len(prompt),
            prefix=prompt,
            suffix=""
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(ai_service.get_code_completion(context))
        loop.close()
        
        return jsonify({
            "choices": [{
                "text": result.completion,
                "finish_reason": "stop"
            }],
            "model": result.model_used,
            "usage": {"total_tokens": 0}
        })
        
    except Exception as e:
        logger.error(f"OpenAI-compatible completions error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/models", methods=["GET"])
def openai_compatible_models():
    """OpenAI-compatible models endpoint for Continue extension"""
    return jsonify({
        "data": [
            {
                "id": "selodev-local",
                "object": "model",
                "created": 1677610602,
                "owned_by": "selodev",
                "permission": [],
                "root": "selodev-local",
                "parent": None
            }
        ]
    })

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info(f"Starting SELODev Code Assist v2.0.0")
    logger.info(f"AI Services: OpenAI={bool(Config.OPENAI_API_KEY)}, Anthropic={bool(Config.ANTHROPIC_API_KEY)}")
    logger.info(f"Continue Extension Support: Enabled (OpenAI-compatible endpoints)")
    
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=Config.DEBUG
    )
