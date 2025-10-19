"""
Provider OpenAI implémentant les interfaces abstraites.
"""
import os
from typing import Dict, Any, List
from ..interfaces import LLMProvider, STTProvider, TTSProvider
from ..metrics import MetricsTimer


class OpenAILLMProvider(LLMProvider):
    """Implémentation OpenAI pour le LLM."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # Import conditionnel pour éviter les erreurs si OpenAI n'est pas installé
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    async def generate_response(self, message: str, system_prompt: str = "") -> str:
        """Génère une réponse à partir d'un message utilisateur."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erreur LLM OpenAI: {e}")
    
    async def generate_streaming_response(self, message: str, system_prompt: str = ""):
        """Génère une réponse en streaming."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": message})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Erreur streaming LLM OpenAI: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle."""
        return {
            "provider": "openai",
            "model": self.model,
            "max_tokens": 4096
        }


class OpenAISTTProvider(STTProvider):
    """Implémentation OpenAI pour le STT."""
    
    def __init__(self, model: str = "whisper-1", api_key: str = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed")
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcrit l'audio en texte."""
        try:
            # Note: Dans une vraie implémentation, il faudrait gérer le format audio
            # et utiliser l'API Whisper appropriée
            response = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_data
            )
            return response.text
        except Exception as e:
            raise Exception(f"Erreur STT OpenAI: {e}")
    
    async def transcribe_streaming(self, audio_stream):
        """Transcrit un flux audio en continu."""
        # Implémentation du streaming STT
        # Dans une vraie implémentation, il faudrait utiliser l'API streaming de Whisper
        raise NotImplementedError("Streaming STT not implemented yet")


class OpenAITTSProvider(TTSProvider):
    """Implémentation OpenAI pour le TTS."""
    
    def __init__(self, model: str = "tts-1", voice: str = "alloy", api_key: str = None):
        self.model = model
        self.voice = voice
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        try:
            import openai
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed")
    
    async def synthesize(self, text: str, voice_id: str = None) -> bytes:
        """Synthétise le texte en audio."""
        try:
            voice = voice_id or self.voice
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text
            )
            
            # Retourner les données audio
            return response.content
        except Exception as e:
            raise Exception(f"Erreur TTS OpenAI: {e}")
    
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Retourne la liste des voix disponibles."""
        return [
            {"id": "alloy", "name": "Alloy"},
            {"id": "echo", "name": "Echo"},
            {"id": "fable", "name": "Fable"},
            {"id": "onyx", "name": "Onyx"},
            {"id": "nova", "name": "Nova"},
            {"id": "shimmer", "name": "Shimmer"}
        ]
