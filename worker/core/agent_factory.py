"""
Agent Factory - Factory pattern pour la création d'agents
Centralise la création d'agents avec différentes configurations
"""

import logging
from typing import Dict, Any, Optional
from livekit.agents import Agent
from .configuration_builder import AgentConfiguration, ConfigurationBuilder
from .session_manager import SessionManager, SessionCreationError


class AgentFactory:
    """
    Factory pour créer des agents avec différentes configurations
    Utilise le pattern Factory avec Builder
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        self.session_manager = session_manager or SessionManager()
    
    def create_agent_from_config(
        self, 
        config: AgentConfiguration
    ) -> Agent:
        """
        Crée un agent à partir d'une configuration
        
        Args:
            config: Configuration de l'agent
            
        Returns:
            Agent: Agent configuré
        """
        try:
            agent = Agent(instructions=config.instructions)
            logging.info(f"Agent créé avec instructions: {config.instructions[:100]}...")
            return agent
            
        except Exception as e:
            logging.error(f"Erreur création agent: {e}")
            raise AgentCreationError(f"Impossible de créer l'agent: {e}")
    
    def create_agent_from_builder(self, agent_config: Any = None) -> Agent:
        """
        Crée un agent en utilisant le ConfigurationBuilder
        
        Args:
            agent_config: Configuration modulaire optionnelle
            
        Returns:
            Agent: Agent configuré
        """
        builder = ConfigurationBuilder()
        
        if agent_config:
            builder.load_from_agent_config(agent_config)
        
        builder.load_from_env()
        
        config = builder.build()
        return self.create_agent_from_config(config)
    
    def get_configuration_from_builder(
        self, 
        agent_config: Any = None
    ) -> AgentConfiguration:
        """
        Récupère la configuration complète depuis le builder
        
        Args:
            agent_config: Configuration modulaire optionnelle
            
        Returns:
            AgentConfiguration: Configuration complète
        """
        builder = ConfigurationBuilder()
        
        if agent_config:
            builder.load_from_agent_config(agent_config)
        
        builder.load_from_env()
        
        return builder.build()


class AgentCreationError(Exception):
    """Exception levée lors de la création d'agent"""
    pass
