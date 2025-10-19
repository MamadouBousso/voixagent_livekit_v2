"""
Session Manager - Gestion centralisée des sessions LiveKit
Utilise le pattern Singleton pour garantir une seule instance
"""

import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime
from livekit.agents import Agent, AgentSession, JobContext
from livekit.plugins import openai, silero
from .interfaces import ProcessingContext
from .metrics import MetricsCollector
from .dynamic_provider_manager import DynamicProviderManager


class SessionManager:
    """Gestionnaire de sessions utilisant le pattern Singleton"""
    
    _instance: Optional['SessionManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'SessionManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._active_sessions: Dict[str, AgentSession] = {}
            self._session_metrics: Dict[str, MetricsCollector] = {}
            self._provider_manager = DynamicProviderManager()
            self._initialized = True
            logging.info("SessionManager initialisé avec DynamicProviderManager")
    
    def create_session(
        self, 
        ctx: JobContext, 
        config: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Tuple[AgentSession, str]:
        """
        Crée une nouvelle session avec la configuration fournie
        Utilise le pattern Builder pour la construction
        """
        if not session_id:
            session_id = f"{ctx.room.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Créer les providers dynamiquement selon la configuration
            try:
                # Utiliser le provider manager pour créer les providers
                vad_provider = self._provider_manager.create_vad_provider()
                stt_provider = self._provider_manager.create_stt_provider()
                llm_provider = self._provider_manager.create_llm_provider()
                tts_provider = self._provider_manager.create_tts_provider()
                
                # Pour l'instant, on utilise encore l'approche LiveKit directe
                # mais avec les configurations du provider manager
                dynamic_config = self._provider_manager.get_config()
                
                # Charger le VAD (Silero est actuellement hardcodé dans LiveKit)
                vad = silero.VAD.load()
                
                # Créer les providers LiveKit avec la config dynamique
                from livekit.plugins.openai import STT as LiveKitOpenAI_STT
                from livekit.plugins.openai import LLM as LiveKitOpenAI_LLM  
                from livekit.plugins.openai import TTS as LiveKitOpenAI_TTS
                
                session = AgentSession(
                    vad=vad,
                    stt=LiveKitOpenAI_STT(model=dynamic_config.stt.model),
                    llm=LiveKitOpenAI_LLM(model=dynamic_config.llm.model),
                    tts=LiveKitOpenAI_TTS(
                        model=dynamic_config.tts.model,
                        voice=dynamic_config.tts.voice_id
                    ),
                )
                
                logging.info(f"Providers créés: STT={dynamic_config.stt.provider_name}/{dynamic_config.stt.model}, "
                           f"LLM={dynamic_config.llm.provider_name}/{dynamic_config.llm.model}, "
                           f"TTS={dynamic_config.tts.provider_name}/{dynamic_config.tts.model}")
                
            except Exception as provider_error:
                logging.warning(f"Erreur providers dynamiques, fallback vers config: {provider_error}")
                # Fallback vers l'ancienne méthode si erreur
                session = AgentSession(
                    vad=silero.VAD.load(),
                    stt=openai.STT(model=config.get('stt_model', 'whisper-1')),
                    llm=openai.LLM(model=config.get('llm_model', 'gpt-4o-mini')),
                    tts=openai.TTS(
                        model=config.get('tts_model', 'tts-1'),
                        voice=config.get('tts_voice', 'alloy')
                    ),
                )
            
            # Enregistrer la session
            self._active_sessions[session_id] = session
            
            # Initialiser les métriques pour cette session
            try:
                metrics_collector = MetricsCollector()
                metrics_collector.start_session_tracking(session_id)
                self._session_metrics[session_id] = metrics_collector
            except Exception as e:
                logging.warning(f"Métriques non disponibles pour {session_id}: {e}")
            
            logging.info(f"Session créée avec succès: {session_id}")
            return session, session_id
            
        except Exception as e:
            logging.error(f"Erreur création session {session_id}: {e}")
            raise SessionCreationError(f"Impossible de créer la session: {e}")
    
    async def start_session(self, session: AgentSession, agent: Agent, room) -> None:
        """
        Démarre une session avec gestion des erreurs améliorée
        """
        try:
            logging.info("Démarrage de la session...")
            await session.start(agent=agent, room=room)
            logging.info("Session démarrée avec succès")
            
        except Exception as e:
            logging.error(f"Erreur démarrage session: {e}")
            raise SessionStartError(f"Impossible de démarrer la session: {e}")
    
    def get_session_metrics(self, session_id: str) -> Optional[MetricsCollector]:
        """Récupère les métriques d'une session spécifique"""
        return self._session_metrics.get(session_id)
    
    def cleanup_session(self, session_id: str) -> None:
        """Nettoie les ressources d'une session"""
        self._active_sessions.pop(session_id, None)
        self._session_metrics.pop(session_id, None)
        logging.info(f"Session {session_id} nettoyée")


class SessionCreationError(Exception):
    """Exception personnalisée pour les erreurs de création de session"""
    pass


class SessionStartError(Exception):
    """Exception personnalisée pour les erreurs de démarrage de session"""
    pass
