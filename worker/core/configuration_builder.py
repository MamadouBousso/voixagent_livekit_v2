"""
Configuration Builder - Pattern Builder pour la configuration des agents
Permet une construction flexible et lisible de la configuration
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentConfiguration:
    """Configuration de l'agent avec des valeurs par défaut"""
    instructions: str = "You are a friendly, concise assistant. Keep answers short."
    stt_model: str = "whisper-1"
    llm_model: str = "gpt-4o-mini"
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"


class ConfigurationBuilder:
    """
    Builder pattern pour construire la configuration de l'agent
    Permet une configuration flexible et extensible
    """
    
    def __init__(self):
        self._config = AgentConfiguration()
        self._agent_config = None
    
    def load_from_agent_config(self, agent_config) -> 'ConfigurationBuilder':
        """
        Charge la configuration depuis l'objet agent_config modulaire
        """
        if agent_config:
            self._agent_config = agent_config
            if hasattr(agent_config, 'system_instructions'):
                self._config.instructions = agent_config.system_instructions
            
            if hasattr(agent_config, 'stt') and hasattr(agent_config.stt, 'model'):
                self._config.stt_model = agent_config.stt.model
            
            if hasattr(agent_config, 'llm') and hasattr(agent_config.llm, 'model'):
                self._config.llm_model = agent_config.llm.model
            
            if hasattr(agent_config, 'tts'):
                if hasattr(agent_config.tts, 'model'):
                    self._config.tts_model = agent_config.tts.model
                if hasattr(agent_config.tts, 'voice'):
                    self._config.tts_voice = agent_config.tts.voice
        
        return self
    
    def load_from_env(self) -> 'ConfigurationBuilder':
        """
        Charge la configuration depuis les variables d'environnement
        """
        self._config.instructions = os.getenv("AGENT_INSTRUCTIONS", self._config.instructions)
        self._config.stt_model = os.getenv("STT_MODEL", self._config.stt_model)
        self._config.llm_model = os.getenv("LLM_MODEL", self._config.llm_model)
        self._config.tts_model = os.getenv("TTS_MODEL", self._config.tts_model)
        self._config.tts_voice = os.getenv("TTS_VOICE_ID", self._config.tts_voice)
        
        return self
    
    def with_instructions(self, instructions: str) -> 'ConfigurationBuilder':
        """Définit les instructions de l'agent"""
        self._config.instructions = instructions
        return self
    
    def with_stt_model(self, model: str) -> 'ConfigurationBuilder':
        """Définit le modèle STT"""
        self._config.stt_model = model
        return self
    
    def with_llm_model(self, model: str) -> 'ConfigurationBuilder':
        """Définit le modèle LLM"""
        self._config.llm_model = model
        return self
    
    def with_tts_model(self, model: str, voice: str = None) -> 'ConfigurationBuilder':
        """Définit le modèle et la voix TTS"""
        self._config.tts_model = model
        if voice:
            self._config.tts_voice = voice
        return self
    
    def validate(self) -> None:
        """
        Valide la configuration avant la construction
        """
        if not self._config.instructions.strip():
            raise ConfigurationError("Les instructions de l'agent ne peuvent pas être vides")
        
        if not self._config.stt_model:
            raise ConfigurationError("Le modèle STT doit être défini")
        
        if not self._config.llm_model:
            raise ConfigurationError("Le modèle LLM doit être défini")
        
        if not self._config.tts_model:
            raise ConfigurationError("Le modèle TTS doit être défini")
        
        # Validation spécifique TTS
        valid_tts_models = ['tts-1', 'tts-1-hd']
        if self._config.tts_model not in valid_tts_models:
            raise ConfigurationError(f"Modèle TTS invalide: {self._config.tts_model}. "
                                   f"Modèles valides: {valid_tts_models}")
    
    def build(self) -> AgentConfiguration:
        """
        Construit et retourne la configuration finale
        """
        self.validate()
        return self._config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la configuration en dictionnaire
        """
        return {
            'instructions': self._config.instructions,
            'stt_model': self._config.stt_model,
            'llm_model': self._config.llm_model,
            'tts_model': self._config.tts_model,
            'tts_voice': self._config.tts_voice
        }


class ConfigurationError(Exception):
    """Exception personnalisée pour les erreurs de configuration"""
    pass
