"""
Exemples de plugins d'agent personnalisés.
Montre comment créer des plugins pour ajouter des fonctionnalités spécifiques.
"""
from typing import Dict, Any
import re
import asyncio
from datetime import datetime
from core.interfaces import AgentPlugin


class SentimentAnalysisPlugin(AgentPlugin):
    """Plugin qui ajoute l'analyse de sentiment aux messages."""
    
    def __init__(self, **kwargs):
        self.name = "Sentiment Analysis Plugin"
        self.enabled = kwargs.get('enabled', True)
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Analyse le sentiment du message utilisateur."""
        if not self.is_enabled():
            return message
        
        # Analyse simple du sentiment (dans une vraie implémentation, utiliser une lib comme VADER)
        positive_words = ['bonjour', 'merci', 'super', 'génial', 'parfait', 'excellent']
        negative_words = ['mauvais', 'nul', 'horrible', 'déçu', 'problème']
        
        message_lower = message.lower()
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            context['sentiment'] = 'positive'
            message += " [Sentiment: Positif détecté]"
        elif negative_count > positive_count:
            context['sentiment'] = 'negative'
            message += " [Sentiment: Négatif détecté]"
        else:
            context['sentiment'] = 'neutral'
        
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled


class ProfanityFilterPlugin(AgentPlugin):
    """Plugin qui filtre les propos inappropriés."""
    
    def __init__(self, **kwargs):
        self.name = "Profanity Filter Plugin"
        self.enabled = kwargs.get('enabled', True)
        # Liste simple de mots à filtrer (dans une vraie implémentation, utiliser une lib dédiée)
        self.blocked_words = kwargs.get('blocked_words', ['insulte1', 'insulte2'])
        self.replacement = kwargs.get('replacement', '***')
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Filtre les propos inappropriés."""
        if not self.is_enabled():
            return message
        
        filtered_message = message
        for word in self.blocked_words:
            if word.lower() in message.lower():
                filtered_message = re.sub(r'\b' + re.escape(word) + r'\b', 
                                        self.replacement, filtered_message, flags=re.IGNORECASE)
                context['profanity_filtered'] = True
        
        return filtered_message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled


class ResponseTimerPlugin(AgentPlugin):
    """Plugin qui mesure le temps de réponse et ajoute des métriques."""
    
    def __init__(self, **kwargs):
        self.name = "Response Timer Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.start_time = None
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Démarre le chronomètre pour mesurer le temps de réponse."""
        if not self.is_enabled():
            return message
        
        self.start_time = datetime.now()
        context['response_timer_start'] = self.start_time.isoformat()
        
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled


class ConversationMemoryPlugin(AgentPlugin):
    """Plugin qui maintient une mémoire de conversation."""
    
    def __init__(self, **kwargs):
        self.name = "Conversation Memory Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.max_history = kwargs.get('max_history', 10)
        self.conversation_history = {}
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Ajoute le message à l'historique de conversation."""
        if not self.is_enabled():
            return message
        
        session_id = context.get('session_id', 'default')
        
        # Initialiser l'historique pour cette session si nécessaire
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Ajouter le message à l'historique
        self.conversation_history[session_id].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': 'user'
        })
        
        # Limiter la taille de l'historique
        if len(self.conversation_history[session_id]) > self.max_history:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history:]
        
        # Ajouter l'historique au contexte pour que le LLM puisse l'utiliser
        context['conversation_history'] = self.conversation_history[session_id]
        
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled


class MetricsPlugin(AgentPlugin):
    """Plugin qui collecte des métriques personnalisées."""
    
    def __init__(self, **kwargs):
        self.name = "Metrics Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.message_count = 0
        self.total_chars = 0
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Collecte des métriques sur les messages."""
        if not self.is_enabled():
            return message
        
        self.message_count += 1
        self.total_chars += len(message)
        
        # Ajouter les métriques au contexte
        context['custom_metrics'] = {
            'message_count': self.message_count,
            'total_characters': self.total_chars,
            'average_message_length': self.total_chars / self.message_count if self.message_count > 0 else 0
        }
        
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled


# Exemple d'enregistrement des plugins personnalisés
def register_custom_plugins():
    """Enregistre les plugins personnalisés dans la factory."""
    from core.factories import PluginFactory
    
    PluginFactory.register_plugin("sentiment_analysis", SentimentAnalysisPlugin)
    PluginFactory.register_plugin("profanity_filter", ProfanityFilterPlugin)
    PluginFactory.register_plugin("response_timer", ResponseTimerPlugin)
    PluginFactory.register_plugin("conversation_memory", ConversationMemoryPlugin)
    PluginFactory.register_plugin("metrics", MetricsPlugin)
    
    print("Plugins personnalisés enregistrés:")
    print("- Sentiment Analysis")
    print("- Profanity Filter")
    print("- Response Timer")
    print("- Conversation Memory")
    print("- Metrics")


if __name__ == "__main__":
    register_custom_plugins()
