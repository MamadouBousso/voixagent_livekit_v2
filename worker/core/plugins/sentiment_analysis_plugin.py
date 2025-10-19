"""
Plugin d'analyse des sentiments pour l'agent vocal
Détecte automatiquement l'émotion de l'utilisateur et adapte les réponses
"""

import re
from typing import Dict, Any
from ..interfaces import AgentPlugin


class SentimentAnalysisPlugin(AgentPlugin):
    """Plugin simple d'analyse des sentiments basé sur des mots-clés."""
    
    def __init__(self, **kwargs):
        self.name = "Sentiment Analysis Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.threshold = kwargs.get('threshold', 0.5)
        
        # Dictionnaires de sentiment (simplifiés)
        self.positive_words = {
            'merci', 'parfait', 'excellent', 'super', 'génial', 'bien', 'bon',
            'content', 'heureux', 'terrible', 'fantastique', 'magnifique'
        }
        
        self.negative_words = {
            'merde', 'connerie', 'nul', 'mauvais', 'terrible', 'horrible',
            'énervé', 'fâché', 'problème', 'erreur', 'bug', 'casse'
        }
        
        self.urgency_words = {
            'urgent', 'rapidement', 'tout de suite', 'immédiatement',
            'asap', 'help', 'aide', 'sauvé'
        }
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Analyse le sentiment du message et modifie le contexte si nécessaire.
        """
        if not self.is_enabled():
            return message
        
        # Analyser le sentiment
        sentiment_score = self._analyze_sentiment(message)
        
        # Ajouter les informations au contexte
        context['sentiment_analysis'] = {
            'score': sentiment_score,
            'emotion': self._get_emotion_label(sentiment_score),
            'is_urgent': self._is_urgent(message)
        }
        
        # Adapter la réponse selon le sentiment détecté
        if sentiment_score < -self.threshold:  # Négatif
            context['response_prefix'] = "Je comprends votre frustration. "
            context['tone'] = "empathique"
        elif sentiment_score > self.threshold:  # Positif  
            context['response_prefix'] = "Je suis content de vous aider ! "
            context['tone'] = "enthousiaste"
        else:
            context['tone'] = "neutre"
        
        # Si urgent, ajouter un indicateur
        if self._is_urgent(message):
            context['urgency'] = "high"
            context['response_prefix'] = (context.get('response_prefix', '') + 
                                        "Je vais traiter votre demande en priorité. ")
        
        return message
    
    def _analyze_sentiment(self, message: str) -> float:
        """Analyse simple du sentiment basée sur des mots-clés."""
        words = re.findall(r'\w+', message.lower())
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return 0.0  # Neutre
        
        # Score normalisé entre -1 et 1
        score = (positive_count - negative_count) / total_sentiment_words
        return score
    
    def _get_emotion_label(self, score: float) -> str:
        """Retourne un label d'émotion basé sur le score."""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        elif score > 0.1:
            return "slightly_positive"
        elif score < -0.1:
            return "slightly_negative"
        else:
            return "neutral"
    
    def _is_urgent(self, message: str) -> bool:
        """Détecte si le message exprime une urgence."""
        message_lower = message.lower()
        return any(word in message_lower for word in self.urgency_words)
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled
