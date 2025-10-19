"""
Plugin de mémoire conversationnelle
Garde en mémoire les conversations pour améliorer les réponses contextuelles
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from ..interfaces import AgentPlugin


class ConversationMemoryPlugin(AgentPlugin):
    """Plugin pour gérer la mémoire des conversations."""
    
    def __init__(self, **kwargs):
        self.name = "Conversation Memory Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.memory_size = kwargs.get('memory_size', 10)
        self.persist_sessions = kwargs.get('persist_sessions', False)
        
        # Stockage en mémoire (en production, utiliser une DB)
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configuration du fichier de persistance
        self.data_dir = kwargs.get('data_dir', os.path.join(os.path.dirname(__file__), '..', 'data'))
        self.storage_file = os.path.join(self.data_dir, 'conversations.json')
        
        if self.persist_sessions:
            self._load_conversations()
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """
        Ajoute le message à la mémoire et enrichit le contexte avec l'historique.
        """
        if not self.is_enabled():
            return message
        
        session_id = context.get('session_id', 'default')
        user_id = context.get('user_id', 'anonymous')
        
        # Initialiser la conversation si nécessaire
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        # Ajouter le message actuel à l'historique
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'message': message,
            'message_type': 'user_input'
        }
        
        self.conversations[session_id].append(conversation_entry)
        
        # Limiter la taille de la mémoire
        self._limit_memory_size(session_id)
        
        # Enrichir le contexte avec l'historique récent
        recent_history = self._get_recent_history(session_id, max_messages=5)
        context['conversation_history'] = recent_history
        context['session_context'] = self._analyze_session_context(session_id)
        
        # Ajouter des recommandations basées sur l'historique
        context['memory_insights'] = self._generate_insights(session_id)
        
        if self.persist_sessions:
            self._save_conversations()
        
        return message
    
    def _get_recent_history(self, session_id: str, max_messages: int = 5) -> List[Dict[str, Any]]:
        """Retourne l'historique récent de la conversation."""
        if session_id not in self.conversations:
            return []
        
        # Retourner les derniers messages
        return self.conversations[session_id][-max_messages:] if max_messages else self.conversations[session_id]
    
    def _limit_memory_size(self, session_id: str):
        """Limite la taille de la mémoire pour éviter l'accumulation."""
        if session_id in self.conversations:
            if len(self.conversations[session_id]) > self.memory_size:
                # Garder seulement les messages les plus récents
                self.conversations[session_id] = self.conversations[session_id][-self.memory_size:]
    
    def _analyze_session_context(self, session_id: str) -> Dict[str, Any]:
        """Analyse le contexte de la session pour fournir des insights."""
        if session_id not in self.conversations or not self.conversations[session_id]:
            return {'session_length': 0, 'topics': [], 'user_mood': 'unknown'}
        
        conversation = self.conversations[session_id]
        
        # Analyser les sujets abordés
        all_messages = ' '.join([entry['message'] for entry in conversation])
        
        # Extraction simple de mots-clés (en production, utiliser NLP)
        words = all_messages.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignorer les mots courts
                word_freq[word] = word_freq.get(word, 0) + 1
        
        top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'session_length': len(conversation),
            'topics': [topic for topic, freq in top_topics],
            'duration_minutes': self._calculate_session_duration(session_id),
            'last_activity': conversation[-1]['timestamp'] if conversation else None
        }
    
    def _calculate_session_duration(self, session_id: str) -> float:
        """Calcule la durée de la session en minutes."""
        if session_id not in self.conversations or len(self.conversations[session_id]) < 2:
            return 0.0
        
        conversation = self.conversations[session_id]
        first_message = datetime.fromisoformat(conversation[0]['timestamp'])
        last_message = datetime.fromisoformat(conversation[-1]['timestamp'])
        
        duration = last_message - first_message
        return duration.total_seconds() / 60  # Convertir en minutes
    
    def _generate_insights(self, session_id: str) -> Dict[str, Any]:
        """Génère des insights basés sur l'historique de la conversation."""
        if session_id not in self.conversations:
            return {}
        
        conversation = self.conversations[session_id]
        context = self._analyze_session_context(session_id)
        
        insights = {
            'is_returning_user': len(conversation) > 5,
            'conversation_trend': self._analyze_trend(conversation),
            'suggested_actions': self._suggest_actions(context, conversation)
        }
        
        return insights
    
    def _analyze_trend(self, conversation: List[Dict[str, Any]]) -> str:
        """Analyse la tendance de la conversation."""
        if len(conversation) < 3:
            return 'neutral'
        
        # Analyser la longueur des messages
        lengths = [len(entry['message']) for entry in conversation[-5:]]
        
        if len(lengths) >= 3:
            if lengths[-1] > sum(lengths[:-1]) / (len(lengths) - 1) * 1.5:
                return 'increasing_engagement'
            elif lengths[-1] < sum(lengths[:-1]) / (len(lengths) - 1) * 0.5:
                return 'decreasing_engagement'
        
        return 'stable'
    
    def _suggest_actions(self, context: Dict[str, Any], conversation: List[Dict[str, Any]]) -> List[str]:
        """Suggère des actions basées sur le contexte."""
        suggestions = []
        
        if context['session_length'] > 10:
            suggestions.append("L'utilisateur semble engagé - proposer une conversation plus approfondie")
        
        if context['duration_minutes'] > 30:
            suggestions.append("Session longue détectée - vérifier si l'utilisateur a besoin d'aide spécifique")
        
        if context['topics'] and 'help' in ' '.join(context['topics']).lower():
            suggestions.append("Demander des clarifications sur le type d'aide nécessaire")
        
        return suggestions
    
    def _load_conversations(self):
        """Charge les conversations depuis le fichier."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Convertir les timestamps en datetime et nettoyer les anciennes données
                    cutoff_time = datetime.now() - timedelta(hours=24)  # Garder 24h
                    
                    for session_id, conversation in data.items():
                        filtered_conversation = []
                        for entry in conversation:
                            try:
                                entry_time = datetime.fromisoformat(entry['timestamp'])
                                if entry_time > cutoff_time:
                                    filtered_conversation.append(entry)
                            except (ValueError, KeyError):
                                continue
                        
                        if filtered_conversation:
                            self.conversations[session_id] = filtered_conversation
        
        except Exception as e:
            print(f"Erreur lors du chargement des conversations: {e}")
    
    def _save_conversations(self):
        """Sauvegarde les conversations dans le fichier."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des conversations: {e}")
    
    def get_conversation_history(self, session_id: str, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retourne l'historique complet d'une session (méthode publique)."""
        return self._get_recent_history(session_id, max_messages)
    
    def clear_session_memory(self, session_id: str) -> bool:
        """Efface la mémoire d'une session spécifique."""
        if session_id in self.conversations:
            del self.conversations[session_id]
            if self.persist_sessions:
                self._save_conversations()
            return True
        return False
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled
