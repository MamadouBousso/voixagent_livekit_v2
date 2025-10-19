"""
Gestion de configuration avec validation et types.
"""
import os
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv


@dataclass
class LLMConfig:
    """Configuration pour le LLM."""
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7


@dataclass
class STTConfig:
    """Configuration pour le STT."""
    provider: str = "openai"
    model: str = "whisper-1"
    api_key: Optional[str] = None


@dataclass
class TTSConfig:
    """Configuration pour le TTS."""
    provider: str = "openai"
    model: str = "tts-1"
    voice: str = "alloy"
    api_key: Optional[str] = None


@dataclass
class VADConfig:
    """Configuration pour le VAD."""
    provider: str = "silero"


@dataclass
class AgentConfig:
    """Configuration complète de l'agent."""
    # Instructions système
    system_instructions: str = "You are a friendly, concise assistant. Keep answers short."
    
    # Configurations des composants
    llm: LLMConfig = field(default_factory=LLMConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    vad: VADConfig = field(default_factory=VADConfig)
    
    # Options avancées
    enable_barge_in: bool = False
    min_endpointing_delay: float = 0.5
    max_response_time: float = 30.0
    
    # Plugins activés
    enabled_plugins: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """Valide la configuration."""
        # Validation des fournisseurs supportés
        supported_providers = {
            "llm": ["openai"],
            "stt": ["openai"],
            "tts": ["openai"],
            "vad": ["silero"]
        }
        
        if self.llm.provider not in supported_providers["llm"]:
            raise ValueError(f"Fournisseur LLM non supporté: {self.llm.provider}")
        
        if self.stt.provider not in supported_providers["stt"]:
            raise ValueError(f"Fournisseur STT non supporté: {self.stt.provider}")
        
        if self.tts.provider not in supported_providers["tts"]:
            raise ValueError(f"Fournisseur TTS non supporté: {self.tts.provider}")
        
        if self.vad.provider not in supported_providers["vad"]:
            raise ValueError(f"Fournisseur VAD non supporté: {self.vad.provider}")


class ConfigManager:
    """Gestionnaire de configuration avec chargement depuis l'environnement."""
    
    def __init__(self, env_file: str = ".env"):
        """Initialise le gestionnaire de configuration."""
        self.env_file = env_file
        load_dotenv(env_file)
    
    def load_agent_config(self) -> AgentConfig:
        """Charge la configuration depuis les variables d'environnement."""
        # Configuration LLM
        llm_config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
        
        # Configuration STT
        stt_config = STTConfig(
            provider=os.getenv("STT_PROVIDER", "openai"),
            model=os.getenv("STT_MODEL", "whisper-1"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Configuration TTS
        tts_config = TTSConfig(
            provider=os.getenv("TTS_PROVIDER", "openai"),
            model=os.getenv("TTS_MODEL", "tts-1"),
            voice=os.getenv("TTS_VOICE_ID", "alloy"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Configuration VAD
        vad_config = VADConfig(
            provider=os.getenv("VAD_PROVIDER", "silero")
        )
        
        # Configuration complète
        config = AgentConfig(
            system_instructions=os.getenv("AGENT_INSTRUCTIONS", 
                                        "You are a friendly, concise assistant. Keep answers short."),
            llm=llm_config,
            stt=stt_config,
            tts=tts_config,
            vad=vad_config,
            enable_barge_in=os.getenv("ENABLE_BARGE_IN", "false").lower() == "true",
            min_endpointing_delay=float(os.getenv("MIN_ENDPOINTING_DELAY", "0.5")),
            max_response_time=float(os.getenv("MAX_RESPONSE_TIME", "30.0")),
            enabled_plugins=self._parse_plugins(os.getenv("ENABLED_PLUGINS", ""))
        )
        
        # Validation
        config.validate()
        return config
    
    def _parse_plugins(self, plugins_str: str) -> List[str]:
        """Parse la liste des plugins depuis la variable d'environnement."""
        if not plugins_str:
            return []
        return [plugin.strip() for plugin in plugins_str.split(",") if plugin.strip()]
    
    def update_config(self, config: AgentConfig, updates: Dict[str, Any]) -> AgentConfig:
        """Met à jour la configuration avec de nouveaux paramètres."""
        # Cette méthode permettrait de mettre à jour la config à la volée
        # Implementation simplifiée pour l'exemple
        return config
