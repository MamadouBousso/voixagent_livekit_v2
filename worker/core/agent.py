"""
Agent principal utilisant l'architecture modulaire.
Implémente le pattern Strategy et Observer pour une gestion flexible des composants.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .interfaces import LLMProvider, STTProvider, TTSProvider, VADProvider, AgentPlugin, MetricData
from .factories import LLMProviderFactory, STTProviderFactory, TTSProviderFactory, VADProviderFactory, PluginFactory
from .config import AgentConfig
from .metrics import MetricsCollector, MetricsTimer, metrics_collector
from livekit.agents import Agent, AgentSession
from livekit.agents import AutoSubscribe


logger = logging.getLogger(__name__)


class ModularAgent:
    """
    Agent modulaire utilisant les design patterns Strategy et Observer.
    Permet de changer facilement de fournisseurs et d'ajouter des plugins.
    """
    
    def __init__(self, config: AgentConfig, metrics_collector: MetricsCollector = None):
        self.config = config
        self.metrics = metrics_collector or metrics_collector
        
        # Initialisation des providers avec le pattern Factory
        self.llm_provider: LLMProvider = self._create_llm_provider()
        self.stt_provider: STTProvider = self._create_stt_provider()
        self.tts_provider: TTSProvider = self._create_tts_provider()
        self.vad_provider: VADProvider = self._create_vad_provider()
        
        # Chargement des plugins
        self.plugins: List[AgentPlugin] = self._load_plugins()
        
        # Session LiveKit
        self.session: Optional[AgentSession] = None
        self.livekit_agent: Optional[Agent] = None
    
    def _create_llm_provider(self) -> LLMProvider:
        """Crée le provider LLM selon la configuration."""
        return LLMProviderFactory.create(
            self.config.llm.provider,
            model=self.config.llm.model,
            api_key=self.config.llm.api_key
        )
    
    def _create_stt_provider(self) -> STTProvider:
        """Crée le provider STT selon la configuration."""
        return STTProviderFactory.create(
            self.config.stt.provider,
            model=self.config.stt.model,
            api_key=self.config.stt.api_key
        )
    
    def _create_tts_provider(self) -> TTSProvider:
        """Crée le provider TTS selon la configuration."""
        return TTSProviderFactory.create(
            self.config.tts.provider,
            model=self.config.tts.model,
            voice=self.config.tts.voice,
            api_key=self.config.tts.api_key
        )
    
    def _create_vad_provider(self) -> VADProvider:
        """Crée le provider VAD selon la configuration."""
        return VADProviderFactory.create(self.config.vad.provider)
    
    def _load_plugins(self) -> List[AgentPlugin]:
        """Charge les plugins activés."""
        plugins = []
        for plugin_name in self.config.enabled_plugins:
            try:
                plugin = PluginFactory.create(plugin_name)
                if plugin.is_enabled():
                    plugins.append(plugin)
                    logger.info(f"Plugin chargé: {plugin.get_name()}")
            except Exception as e:
                logger.error(f"Erreur chargement plugin {plugin_name}: {e}")
        return plugins
    
    async def process_message_with_plugins(self, message: str, context: Dict[str, Any]) -> str:
        """
        Traite un message en passant par tous les plugins activés.
        Implémente le pattern Chain of Responsibility.
        """
        processed_message = message
        
        for plugin in self.plugins:
            try:
                processed_message = await plugin.process_message(processed_message, context)
                metric = MetricData(
                    name='plugin_processing',
                    value=1.0,
                    timestamp=datetime.now(),
                    unit='count',
                    metadata={
                        'plugin': plugin.get_name(),
                        'session_id': context.get('session_id', 'unknown')
                    }
                )
                self.metrics.record_metric(metric)
            except Exception as e:
                logger.error(f"Erreur dans le plugin {plugin.get_name()}: {e}")
        
        return processed_message
    
    async def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Génère une réponse en utilisant le LLM et les plugins."""
        session_id = context.get('session_id', 'unknown')
        
        # Traiter le message avec les plugins
        processed_message = await self.process_message_with_plugins(message, context)
        
        # Générer la réponse avec le LLM
        with MetricsTimer(self.metrics, "llm_latency", session_id):
            response = await self.llm_provider.generate_response(
                processed_message, 
                self.config.system_instructions
            )
        
        # Traiter la réponse avec les plugins (optionnel)
        for plugin in self.plugins:
            try:
                response = await plugin.process_message(response, context)
            except Exception as e:
                logger.error(f"Erreur plugin post-traitement {plugin.get_name()}: {e}")
        
        return response
    
    def update_llm_provider(self, provider_name: str, **kwargs) -> None:
        """Change le provider LLM à la volée."""
        try:
            self.llm_provider = LLMProviderFactory.create(provider_name, **kwargs)
            logger.info(f"Provider LLM changé vers: {provider_name}")
        except Exception as e:
            logger.error(f"Erreur changement provider LLM: {e}")
    
    def add_plugin(self, plugin_name: str, **kwargs) -> bool:
        """Ajoute un plugin à la volée."""
        try:
            plugin = PluginFactory.create(plugin_name, **kwargs)
            if plugin.is_enabled():
                self.plugins.append(plugin)
                logger.info(f"Plugin ajouté: {plugin.get_name()}")
                return True
        except Exception as e:
            logger.error(f"Erreur ajout plugin {plugin_name}: {e}")
        return False
    
    def get_metrics_summary(self, session_id: str = None) -> Dict[str, Any]:
        """Retourne un résumé des métriques."""
        if session_id:
            session_metrics = self.metrics.get_session_metrics(session_id)
            if session_metrics:
                return {
                    "session_id": session_id,
                    "stt_latency": session_metrics.stt_latency,
                    "llm_latency": session_metrics.llm_latency,
                    "tts_latency": session_metrics.tts_latency,
                    "total_latency": session_metrics.total_latency
                }
        
        avg_metrics = self.metrics.get_average_metrics()
        return {
            "average_metrics": avg_metrics,
            "active_plugins": [p.get_name() for p in self.plugins if p.is_enabled()],
            "llm_provider": self.llm_provider.get_model_info()["provider"],
            "tts_provider": "openai",  # TODO: implémenter get_provider_info
            "stt_provider": "openai"   # TODO: implémenter get_provider_info
        }
