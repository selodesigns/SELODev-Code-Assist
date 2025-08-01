import aiohttp
import json
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from config import Config
import logging
import time
import asyncio

# Optional cloud imports (only if user wants expensive fallback)
try:
    import openai
except ImportError:
    openai = None
    
try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

@dataclass
class CodeContext:
    """Context information for code completion requests"""
    file_path: str
    language: str
    cursor_position: int
    prefix: str  # Code before cursor
    suffix: str  # Code after cursor
    surrounding_code: Optional[str] = None

@dataclass
class CompletionResult:
    """Result from AI code completion"""
    completion: str
    confidence: float
    model_used: str
    processing_time: float
    provider: str  # 'ollama', 'lm_studio', 'openai', 'anthropic'
    cost: float = 0.0  # Always 0 for local models

class LocalLLMService:
    """Free local LLM service - PRIMARY AI provider"""
    
    def __init__(self):
        self.session = None
        
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=Config.LOCAL_MODEL_TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def check_ollama_availability(self) -> bool:
        """Check if Ollama is running and has the model"""
        try:
            session = await self._get_session()
            async with session.get(f"{Config.OLLAMA_BASE_URL}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    return Config.OLLAMA_MODEL in models
                return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    async def check_lm_studio_availability(self) -> bool:
        """Check if LM Studio is running"""
        try:
            session = await self._get_session()
            async with session.get(f"{Config.LM_STUDIO_BASE_URL}/models") as response:
                return response.status == 200
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")
            return False
    
    async def ollama_completion(self, context: CodeContext) -> str:
        """Get completion from Ollama (FREE)"""
        prompt = self._build_code_prompt(context)
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": Config.LOCAL_MODEL_TEMPERATURE,
                "num_predict": Config.LOCAL_MODEL_MAX_TOKENS,
                "stop": ["\n\n", "```", "</code>", "# End"]
            }
        }
        
        session = await self._get_session()
        async with session.post(f"{Config.OLLAMA_BASE_URL}/api/generate", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('response', '').strip()
            else:
                raise Exception(f"Ollama API error: {response.status}")
    
    async def lm_studio_completion(self, context: CodeContext) -> str:
        """Get completion from LM Studio (FREE)"""
        prompt = self._build_code_prompt(context)
        
        payload = {
            "model": Config.LM_STUDIO_MODEL,
            "messages": [
                {"role": "system", "content": "You are an expert code completion assistant. Provide only the code that should be inserted at the cursor position."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": Config.LOCAL_MODEL_MAX_TOKENS,
            "temperature": Config.LOCAL_MODEL_TEMPERATURE,
            "stop": ["\n\n", "```"]
        }
        
        session = await self._get_session()
        async with session.post(f"{Config.LM_STUDIO_BASE_URL}/chat/completions", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                raise Exception(f"LM Studio API error: {response.status}")
    
    async def ollama_explain(self, code: str, language: str) -> str:
        """Explain code using Ollama (FREE)"""
        prompt = f"Explain this {language} code clearly and concisely:\n\n{code}\n\nExplanation:"
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 300
            }
        }
        
        session = await self._get_session()
        async with session.post(f"{Config.OLLAMA_BASE_URL}/api/generate", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('response', '').strip()
            else:
                raise Exception(f"Ollama API error: {response.status}")
    
    async def ollama_improve(self, code: str, language: str) -> List[str]:
        """Get improvement suggestions using Ollama (FREE)"""
        prompt = f"Analyze this {language} code and provide 3-5 specific improvement suggestions:\n\n{code}\n\nSuggestions:"
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 400
            }
        }
        
        session = await self._get_session()
        async with session.post(f"{Config.OLLAMA_BASE_URL}/api/generate", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                suggestions_text = data.get('response', '').strip()
                # Parse suggestions into list
                suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip() and len(s.strip()) > 10]
                return suggestions[:5]
            else:
                raise Exception(f"Ollama API error: {response.status}")
    
    def _build_code_prompt(self, context: CodeContext) -> str:
        """Build optimized prompt for code completion"""
        return f"""Complete the {context.language} code at the cursor position.

File: {context.file_path}

Code before cursor:
{context.prefix}

<CURSOR>

Code after cursor:
{context.suffix}

Complete the code at <CURSOR>. Provide only the completion code:"""
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()

class CloudLLMService:
    """Expensive cloud LLM service - FALLBACK ONLY"""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize cloud clients only if API keys are provided"""
        if Config.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("⚠️  OpenAI client initialized (COSTS MONEY)")
            
        if Config.ANTHROPIC_API_KEY and anthropic:
            self.anthropic_client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            logger.info("⚠️  Anthropic client initialized (COSTS MONEY)")
    
    async def openai_completion(self, context: CodeContext) -> str:
        """Get completion from OpenAI (EXPENSIVE)"""
        if not self.openai_client:
            raise Exception("OpenAI not configured")
            
        prompt = f"""Complete this {context.language} code at the cursor position. Return only the completion:

{context.prefix}<CURSOR>{context.suffix}"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a code completion assistant. Provide only the code completion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=Config.LOCAL_MODEL_MAX_TOKENS,
            temperature=Config.LOCAL_MODEL_TEMPERATURE
        )
        
        return response.choices[0].message.content.strip()

class AIService:
    """Unified AI service - prioritizes FREE local LLMs over expensive cloud APIs"""
    
    def __init__(self):
        self.local_service = LocalLLMService()
        self.cloud_service = CloudLLMService()
        self.provider_priority = Config.get_ai_provider_priority()
        logger.info(f"🚀 AI Service initialized. Priority: {' -> '.join(self.provider_priority)}")
    
    async def get_code_completion(self, context: CodeContext) -> CompletionResult:
        """Get AI-powered code completion (FREE local first, expensive cloud fallback)"""
        start_time = time.time()
        
        for provider in self.provider_priority:
            try:
                if provider == 'ollama':
                    if await self.local_service.check_ollama_availability():
                        completion = await self.local_service.ollama_completion(context)
                        return CompletionResult(
                            completion=completion,
                            confidence=0.85,
                            model_used=Config.OLLAMA_MODEL,
                            processing_time=time.time() - start_time,
                            provider='ollama',
                            cost=0.0
                        )
                    else:
                        logger.info("💡 Ollama not available. Install with: curl -fsSL https://ollama.ai/install.sh | sh")
                        
                elif provider == 'lm_studio':
                    if await self.local_service.check_lm_studio_availability():
                        completion = await self.local_service.lm_studio_completion(context)
                        return CompletionResult(
                            completion=completion,
                            confidence=0.80,
                            model_used=Config.LM_STUDIO_MODEL,
                            processing_time=time.time() - start_time,
                            provider='lm_studio',
                            cost=0.0
                        )
                    else:
                        logger.info("💡 LM Studio not available. Download from: https://lmstudio.ai")
                        
                elif provider == 'openai' and self.cloud_service.openai_client:
                    logger.warning("💸 Using expensive OpenAI API - consider installing Ollama for free local AI")
                    completion = await self.cloud_service.openai_completion(context)
                    return CompletionResult(
                        completion=completion,
                        confidence=0.90,
                        model_used="gpt-3.5-turbo",
                        processing_time=time.time() - start_time,
                        provider='openai',
                        cost=0.002  # Approximate cost
                    )
                    
            except Exception as e:
                logger.error(f"Provider {provider} failed: {e}")
                continue
        
        raise Exception("No AI providers available. Install Ollama (free) or configure cloud APIs (expensive)")
    
    async def explain_code(self, code: str, language: str) -> str:
        """Explain code (FREE local first)"""
        try:
            if await self.local_service.check_ollama_availability():
                return await self.local_service.ollama_explain(code, language)
            else:
                return "Install Ollama for free code explanations: curl -fsSL https://ollama.ai/install.sh | sh"
        except Exception as e:
            logger.error(f"Code explanation failed: {e}")
            return f"Error: {str(e)}. Install Ollama for free AI: https://ollama.ai"
    
    async def suggest_improvements(self, code: str, language: str) -> List[str]:
        """Suggest code improvements (FREE local first)"""
        try:
            if await self.local_service.check_ollama_availability():
                return await self.local_service.ollama_improve(code, language)
            else:
                return ["Install Ollama for free code suggestions: curl -fsSL https://ollama.ai/install.sh | sh"]
        except Exception as e:
            logger.error(f"Code suggestions failed: {e}")
            return [f"Error: {str(e)}. Install Ollama for free AI: https://ollama.ai"]
    
    async def close(self):
        """Clean up resources"""
        await self.local_service.close()

# Global AI service instance
ai_service = AIService()
