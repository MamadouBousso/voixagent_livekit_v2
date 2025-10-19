"""
Factory pattern pour créer les instances des différents composants.
Permet de changer facilement de fournisseur (LLM, STT, TTS, etc.)
"""
from typing import Dict, Type, Any
from .interfaces import LLMProvider, STTProvider, TTSProvider, VADProvider, AgentPlugin
from .providers.openai_provider import OpenAILLMProvider, OpenAISTTProvider, OpenAITTSProvider
from .providers.silero_provider import SileroVADProvider
from .plugins.example_plugin import ExampleAgentPlugin
from .plugins.sentiment_analysis_plugin import SentimentAnalysisPlugin
from .plugins.profanity_filter_plugin import ProfanityFilterPlugin
from .plugins.conversation_memory_plugin import ConversationMemoryPlugin


class LLMProviderFactory:
    """Factory pour créer les fournisseurs de LLM."""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAILLMProvider,
        # Ajouter d'autres fournisseurs ici
        # "anthropic": AnthropicLLMProvider,
        # "cohere": CohereLLMProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> LLMProvider:
        """Crée une instance du fournisseur LLM spécifié."""
        if provider_name not in cls._providers:
            raise ValueError(f"Fournisseur LLM non supporté: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """Enregistre un nouveau fournisseur LLM."""
        cls._providers[name] = provider_class


class STTProviderFactory:
    """Factory pour créer les fournisseurs de STT."""
    
    _providers: Dict[str, Type[STTProvider]] = {
        "openai": OpenAISTTProvider,
        # Ajouter d'autres fournisseurs ici
        # "google": GoogleSTTProvider,
        # "azure": AzureSTTProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> STTProvider:
        """Crée une instance du fournisseur STT spécifié."""
        if provider_name not in cls._providers:
            raise ValueError(f"Fournisseur STT non supporté: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)


class TTSProviderFactory:
    """Factory pour créer les fournisseurs de TTS."""
    
    _providers: Dict[str, Type[TTSProvider]] = {
        "openai": OpenAITTSProvider,
        # Ajouter d'autres fournisseurs ici
        # "elevenlabs": ElevenLabsTTSProvider,
        # "azure": AzureTTSProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> TTSProvider:
        """Crée une instance du fournisseur TTS spécifié."""
        if provider_name not in cls._providers:
            raise ValueError(f"Fournisseur TTS non supporté: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)


class VADProviderFactory:
    """Factory pour créer les fournisseurs de VAD."""
    
    _providers: Dict[str, Type[VADProvider]] = {
        "silero": SileroVADProvider,
        # Ajouter d'autres fournisseurs ici
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> VADProvider:
        """Crée une instance du fournisseur VAD spécifié."""
        if provider_name not in cls._providers:
            raise ValueError(f"Fournisseur VAD non supporté: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)


class PluginFactory:
    """Factory pour créer les plugins d'agent."""
    
    _plugins: Dict[str, Type[AgentPlugin]] = {
        "example": ExampleAgentPlugin,
        "sentiment_analysis": SentimentAnalysisPlugin,
        "profanity_filter": ProfanityFilterPlugin,
        "conversation_memory": ConversationMemoryPlugin,
        # Ajouter d'autres plugins ici
    }
    
    @classmethod
    def create(cls, plugin_name: str, **kwargs) -> AgentPlugin:
        """Crée une instance du plugin spécifié."""
        if plugin_name not in cls._plugins:
            raise ValueError(f"Plugin non supporté: {plugin_name}")
        
        plugin_class = cls._plugins[plugin_name]
        return plugin_class(**kwargs)
    
    @classmethod
    def register_plugin(cls, name: str, plugin_class: Type[AgentPlugin]):
        """Enregistre un nouveau plugin."""
        cls._plugins[name] = plugin_class
    
    @classmethod
    def list_available_plugins(cls) -> list[str]:
        """Retourne la liste des plugins disponibles."""
        return list(cls._plugins.keys())
