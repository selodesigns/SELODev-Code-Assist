import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Local LLM Configuration (PRIMARY)
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'codellama:7b-instruct')
    
    LM_STUDIO_BASE_URL = os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
    LM_STUDIO_MODEL = os.getenv('LM_STUDIO_MODEL', 'local-model')
    
    # Local Model Settings
    LOCAL_MODEL_TIMEOUT = int(os.getenv('LOCAL_MODEL_TIMEOUT', 30))
    LOCAL_MODEL_MAX_TOKENS = int(os.getenv('LOCAL_MODEL_MAX_TOKENS', 512))
    LOCAL_MODEL_TEMPERATURE = float(os.getenv('LOCAL_MODEL_TEMPERATURE', 0.1))
    
    # Cloud AI Configuration (OPTIONAL FALLBACK)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Optional - costs money
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')  # Optional - costs money
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'ollama')  # ollama, lm_studio, openai, anthropic
    
    # Code Analysis Configuration
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', 10))
    SUPPORTED_LANGUAGES = os.getenv('SUPPORTED_LANGUAGES', 'python,javascript,typescript,html,css,json,yaml,go,rust,java,cpp').split(',')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        warnings = []
        
        # Check for local LLM availability (preferred)
        local_available = False
        
        if cls.DEFAULT_AI_PROVIDER == 'ollama':
            # Will check Ollama connectivity at runtime
            local_available = True
        elif cls.DEFAULT_AI_PROVIDER == 'lm_studio':
            # Will check LM Studio connectivity at runtime
            local_available = True
        
        # Check cloud fallbacks
        cloud_available = bool(cls.OPENAI_API_KEY or cls.ANTHROPIC_API_KEY)
        
        if not local_available and not cloud_available:
            issues.append("No AI providers configured. Install Ollama or LM Studio for free local AI, or set cloud API keys as fallback")
        
        if cloud_available and not local_available:
            warnings.append("Only expensive cloud APIs configured. Consider installing Ollama for free local AI")
            
        if cls.MAX_FILE_SIZE_MB > 50:
            warnings.append("MAX_FILE_SIZE_MB is very large, consider reducing for performance")
        
        if cls.DEFAULT_AI_PROVIDER not in ['ollama', 'lm_studio', 'openai', 'anthropic']:
            issues.append(f"Invalid DEFAULT_AI_PROVIDER: {cls.DEFAULT_AI_PROVIDER}. Must be: ollama, lm_studio, openai, or anthropic")
            
        return issues + [f"WARNING: {w}" for w in warnings]
    
    @classmethod
    def get_ai_provider_priority(cls) -> List[str]:
        """Get AI provider priority order (local first, cloud fallback)"""
        providers = []
        
        # Always prioritize local LLMs
        if cls.DEFAULT_AI_PROVIDER == 'ollama':
            providers.append('ollama')
            providers.append('lm_studio')  # Secondary local option
        elif cls.DEFAULT_AI_PROVIDER == 'lm_studio':
            providers.append('lm_studio')
            providers.append('ollama')  # Secondary local option
        
        # Add cloud fallbacks only if configured
        if cls.OPENAI_API_KEY:
            providers.append('openai')
        if cls.ANTHROPIC_API_KEY:
            providers.append('anthropic')
            
        return providers
