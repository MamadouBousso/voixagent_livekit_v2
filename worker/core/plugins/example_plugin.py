"""
Exemple de plugin d'agent personnalisé.
"""
from typing import Dict, Any
from ..interfaces import AgentPlugin


class ExampleAgentPlugin(AgentPlugin):
    """Plugin d'exemple qui ajoute des fonctionnalités personnalisées."""
    
    def __init__(self, **kwargs):
        self.name = "Example Plugin"
        self.enabled = True
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Traite un message et retourne une réponse modifiée."""
        if not self.is_enabled():
            return message
        
        # Exemple de traitement personnalisé
        if "hello" in message.lower():
            return message + " (Processed by Example Plugin!)"
        
        return message
    
    def get_name(self) -> str:
        """Retourne le nom du plugin."""
        return self.name
    
    def is_enabled(self) -> bool:
        """Vérifie si le plugin est activé."""
        return self.enabled
