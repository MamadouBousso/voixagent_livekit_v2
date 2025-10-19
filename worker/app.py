# ============================================================
# IMPORTS - Architecture modulaire avec design patterns
# ============================================================
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, AutoSubscribe, cli
from livekit.plugins import openai, silero

# Imports de l'architecture modulaire
from core.config import ConfigManager
from core.agent import ModularAgent
from core.factories import LLMProviderFactory, STTProviderFactory, TTSProviderFactory, VADProviderFactory
from core.metrics import metrics_collector
from core.interfaces import ProcessingContext

# Imports des nouvelles classes avec design patterns
from core.session_manager import SessionManager, SessionCreationError, SessionStartError
from core.configuration_builder import ConfigurationBuilder, AgentConfiguration, ConfigurationError
from core.dependency_container import container
from core.agent_factory import AgentFactory, AgentCreationError

# ============================================================
# CHARGEMENT DE LA CONFIGURATION MODULAIRE ET INJECTION DE DÉPENDANCES
# ============================================================
# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Initialiser le gestionnaire de configuration
config_manager = ConfigManager()
agent_config = config_manager.load_agent_config()

# Configuration du conteneur de dépendances (Dependency Injection)
session_manager = SessionManager()
agent_factory = AgentFactory(session_manager)

# Enregistrer les services dans le conteneur DI
container.register_singleton('session_manager', session_manager)
container.register_singleton('agent_factory', agent_factory)
container.register_singleton('config_manager', config_manager)
container.register_service('agent_config', agent_config)

# Instance globale de l'agent modulaire (legacy)
modular_agent: ModularAgent = None

# ============================================================
# FONCTION PRINCIPALE - Point d'entrée de l'agent modulaire
# ============================================================
async def entrypoint(ctx: JobContext):
    """
    Point d'entrée principal du worker agent vocal - Version refactorisée avec design patterns.
    
    Utilise maintenant:
    - Dependency Injection pour la gestion des services
    - Builder pattern pour la configuration
    - Factory pattern pour la création d'agents
    - SessionManager pour la gestion des sessions
    
    Paramètres:
        ctx (JobContext): Contexte fourni par LiveKit contenant les infos de la room
    """
    session_id = f"{ctx.room.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # ============================================================
    # LOG D'ENTRÉE POUR DIAGNOSTIC - TRÈS VISIBLE
    # ============================================================
    print("🚀🚀🚀 ENTRYPOINT APPELÉ ! 🚀🚀🚀")  # Print visible même sans logging
    logging.info(f"=== ENTRÉE DANS ENTRYPOINT ===")
    logging.info(f"Salle: {ctx.room.name}")
    logging.info(f"Session ID: {session_id}")
    
    # ============================================================
    # ÉTAPE 1 : CONNEXION À LA SALLE LIVEKIT
    # ============================================================
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # ============================================================
    # ÉTAPE 2 : CONFIGURATION SIMPLIFIÉE (inspirée du projet1)
    # ============================================================
    # Configuration avec Builder pattern et Dependency Injection
    try:
        # Récupérer les services via Dependency Injection
        session_manager = container.get('session_manager')
        agent_factory = container.get('agent_factory')
        agent_config_di = container.get('agent_config')
        
        # Créer la configuration avec le Builder pattern
        configuration = agent_factory.get_configuration_from_builder(agent_config_di)
        
        logging.info(f"Configuration: STT={configuration.stt_model}, LLM={configuration.llm_model}, "
                    f"TTS={configuration.tts_model}, VOICE={configuration.tts_voice}")
        logging.info(f"Instructions agent: {configuration.instructions[:100]}...")
        
    except ConfigurationError as e:
        logging.error(f"Erreur de configuration: {e}")
        raise
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation: {e}")
        raise
    
    # ============================================================
    # ÉTAPE 3 : CRÉATION DE L'AGENT ET SESSION AVEC FACTORY PATTERN
    # ============================================================
    try:
        # Créer l'agent avec l'AgentFactory
        agent = agent_factory.create_agent_from_config(configuration)
        
        # Créer la session avec le SessionManager
        session_config = configuration.__dict__
        session, actual_session_id = session_manager.create_session(ctx, session_config, session_id)
        session_id = actual_session_id  # Utiliser l'ID généré par le SessionManager
        
        logging.info("✅ Agent et session créés avec succès")
        
    except (AgentCreationError, SessionCreationError) as e:
        logging.error(f"Erreur création agent/session: {e}")
        raise
    
    # ============================================================
    # ÉTAPE 4 : GESTION DES MÉTRIQUES ET DÉMARRAGE DE SESSION
    # ============================================================
    try:
        logging.info(f"🎯 Démarrage session pour salle: {ctx.room.name} (ID: {session_id})")
        
        # Récupérer les métriques depuis le SessionManager
        local_metrics_collector = session_manager.get_session_metrics(session_id)
        
        # Enregistrer une métrique de connexion réussie si possible
        if local_metrics_collector:
            try:
                local_metrics_collector.record_session_metric(session_id, "connection_success", 1.0, "count")
                logging.info("Métrique de connexion enregistrée")
            except Exception as e:
                logging.warning(f"Impossible d'enregistrer métrique: {e}")
        
        # Démarrer la session directement (LiveKit gère le lifecycle)
        logging.info("⏳ Démarrage de la session...")
        await session.start(agent=agent, room=ctx.room)
        
        logging.info(f"✅ Session terminée pour la salle: {ctx.room.name}")
        
    except Exception as e:
        logging.error(f"Erreur session: {e}")
        
        # Enregistrer une métrique d'erreur si possible
        local_metrics_collector = session_manager.get_session_metrics(session_id)
        if local_metrics_collector:
            try:
                local_metrics_collector.record_session_metric(session_id, "connection_error", 1.0, "count")
            except Exception:
                pass
        raise
    finally:
        # Nettoyage des ressources
        session_manager.cleanup_session(session_id)

# ============================================================
# FONCTIONS UTILITAIRES POUR LA GESTION DYNAMIQUE
# ============================================================
def update_llm_provider(provider_name: str, **kwargs) -> bool:
    """
    Change dynamiquement le provider LLM à la volée.
    
    Args:
        provider_name: Nom du nouveau provider (ex: 'openai', 'anthropic')
        **kwargs: Arguments spécifiques au provider
    
    Returns:
        bool: True si le changement a réussi
    """
    global modular_agent
    if modular_agent:
        try:
            modular_agent.update_llm_provider(provider_name, **kwargs)
            logging.info(f"Provider LLM changé vers: {provider_name}")
            return True
        except Exception as e:
            logging.error(f"Erreur changement provider LLM: {e}")
    return False

def add_plugin_dynamically(plugin_name: str, **kwargs) -> bool:
    """
    Ajoute dynamiquement un plugin à la volée.
    
    Args:
        plugin_name: Nom du plugin à ajouter
        **kwargs: Arguments spécifiques au plugin
    
    Returns:
        bool: True si l'ajout a réussi
    """
    global modular_agent
    if modular_agent:
        return modular_agent.add_plugin(plugin_name, **kwargs)
    return False

def get_metrics_summary(session_id: str = None) -> Dict[str, Any]:
    """
    Récupère un résumé des métriques de performance.
    
    Args:
        session_id: ID de session spécifique (optionnel)
    
    Returns:
        Dict contenant les métriques
    """
    global modular_agent
    if modular_agent:
        return modular_agent.get_metrics_summary(session_id)
    return {}


# ============================================================
# DÉMARRAGE DU WORKER AVEC ARCHITECTURE MODULAIRE
# ============================================================
if __name__ == "__main__":
    # Configurer le système de logs pour afficher les informations
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Logger la configuration chargée (version robuste)
    logging.info("=== DÉMARRAGE DE L'AGENT SIMPLIFIÉ ===")
    try:
        if agent_config and hasattr(agent_config, 'llm'):
            logging.info(f"Configuration LLM: {agent_config.llm.provider}/{agent_config.llm.model}")
            logging.info(f"Configuration STT: {agent_config.stt.provider}/{agent_config.stt.model}")
            logging.info(f"Configuration TTS: {agent_config.tts.provider}/{agent_config.tts.model}")
            logging.info(f"Plugins activés: {agent_config.enabled_plugins}")
        else:
            logging.info("Configuration: Utilisation des variables d'environnement directes")
            logging.info(f"STT_MODEL: {os.getenv('STT_MODEL', 'whisper-1')}")
            logging.info(f"LLM_MODEL: {os.getenv('LLM_MODEL', 'gpt-4o-mini')}")
            logging.info(f"TTS_MODEL: {os.getenv('TTS_MODEL', 'tts-1')}")
    except Exception as e:
        logging.warning(f"Erreur affichage config: {e}")
    logging.info("=====================================")
    
    # Démarrer le worker LiveKit avec la fonction d'entrée modulaire
    # Le CLI LiveKit gère :
    # - La connexion au serveur LiveKit
    # - L'écoute des nouvelles salles/participants
    # - L'invocation de la fonction entrypoint pour chaque job
    # - La gestion du cycle de vie du worker
    
    # Configuration du worker avec connexion LiveKit Cloud explicite
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        # Pas d'agent_name pour permettre le dispatch automatique sur toutes les salles
        ws_url=os.getenv('LIVEKIT_URL', ''),
        api_key=os.getenv('LIVEKIT_API_KEY'),
        api_secret=os.getenv('LIVEKIT_API_SECRET'),
    )
    
    logging.info("Démarrage du worker avec options:")
    logging.info(f"  Entrypoint: {entrypoint.__name__}")
    logging.info(f"  WorkerOptions: {worker_options}")
    
    cli.run_app(worker_options)
