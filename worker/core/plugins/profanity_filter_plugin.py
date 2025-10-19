"""
Plugin de filtrage de contenu inapproprié
Filtre les messages contenant des mots inappropriés ou du spam
"""

import re
from typing import Dict, Any, Set
from ..interfaces import AgentPlugin


class ProfanityFilterPlugin(AgentPlugin):
    """Plugin pour filtrer le contenu inapproprié."""
    
    def __init__(self, **kwargs):
        self.name = "Profanity Filter Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.strict_mode = kwargs.get('strict', False)
        
        # Liste de mots inappropriés (simplifiée, en français)
        self.bad_words: Set[str] = {
            'merde', 'con', 'connard', 'salope', 'pute', 'putain',
            'enculé', 'bordel', 'nique', 'foutre'
        }
        
        # Messages de remplacement selon le mode
        self.replacement_messages = {
            'strict': [
                "Je préfère ne pas répondre à cela.",
                "Pouvez-vous reformuler votre question de manière plus respectueuse ?",
                "Je ne peux pas traiter ce type de contenu."
            ],
            'soft': [
                "Pouvez-vous reformuler cela plus poliment ?",
                "Je comprends votre frustration, mais pourriez-vous être plus respectueux ?"
            ]
        }
        
        # Patterns de spam
        self.spam_patterns = [
            r'(.)\1{4,}',  # Répétition de caractères (ex: "aaaaa")
            r'\b(?:buy|sell|discount|offer)\b',  # Mots commerciaux
            r'http[s]?://',  # URLs
            r'@\w+',  # Mentions
        ]
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Filtre le message et retourne une version nettoyée ou un message de remplacement.
        """
        if not self.is_enabled() or not message.strip():
            return message
        
        # Vérifier le contenu inapproprié
        if self._contains_inappropriate_content(message):
            context['filtered'] = True
            context['filter_reason'] = 'inappropriate_content'
            return self._get_replacement_message()
        
        # Vérifier le spam
        if self._is_spam(message):
            context['filtered'] = True
            context['filter_reason'] = 'spam'
            return "Votre message semble être du spam. Pouvez-vous poser une question plus pertinente ?"
        
        # Nettoyer le message si nécessaire
        cleaned_message = self._clean_message(message)
        if cleaned_message != message:
            context['cleaned'] = True
            context['original_message'] = message
            context['filtered_message'] = cleaned_message
        
        return cleaned_message
    
    def _contains_inappropriate_content(self, message: str) -> bool:
        """Vérifie si le message contient du contenu inapproprié."""
        message_lower = message.lower()
        words = re.findall(r'\w+', message_lower)
        
        # Vérifier la présence de mots inappropriés
        for word in words:
            if word in self.bad_words:
                return True
        
        # Vérifier les patterns d'insultes
        insult_patterns = [
            r'fils de \w+',
            r'espèce de \w+',
            r'\w+ de merde',
        ]
        
        for pattern in insult_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _is_spam(self, message: str) -> bool:
        """Détecte si le message est probablement du spam."""
        message_lower = message.lower()
        
        # Vérifier les patterns de spam
        spam_score = 0
        
        for pattern in self.spam_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                spam_score += 1
        
        # Si le message est très court avec des patterns de spam
        if len(message.split()) < 3 and spam_score > 0:
            return True
        
        # Si plusieurs patterns sont détectés
        if spam_score >= 2:
            return True
        
        return False
    
    def _clean_message(self, message: str) -> str:
        """Nettoie le message en masquant les mots inappropriés."""
        if self.strict_mode:
            return message  # En mode strict, on rejette plutôt que nettoyer
        
        words = message.split()
        cleaned_words = []
        
        for word in words:
            if word.lower() in self.bad_words:
                # Remplacer par des astérisques
                cleaned_words.append('*' * len(word))
            else:
                cleaned_words.append(word)
        
        return ' '.join(cleaned_words)
    
    def _get_replacement_message(self) -> str:
        """Retourne un message de remplacement approprié."""
        import random
        
        mode = 'strict' if self.strict_mode else 'soft'
        messages = self.replacement_messages[mode]
        
        return random.choice(messages)
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled
