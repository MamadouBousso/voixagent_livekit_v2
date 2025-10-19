"""
Interfaces abstraites pour l'architecture modulaire de l'agent vocal.
Utilise le design pattern Strategy pour permettre l'interchangeabilité des composants.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MetricData:
    """Données de métrique pour le monitoring des performances."""
    name: str
    value: float
    timestamp: datetime
    unit: str = "ms"
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class LLMProvider(ABC):
    """Interface abstraite pour les fournisseurs de LLM."""
    
    @abstractmethod
    async def generate_response(self, message: str, system_prompt: str = "") -> str:
        """Génère une réponse à partir d'un message utilisateur."""
        pass
    
    @abstractmethod
    async def generate_streaming_response(self, message: str, system_prompt: str = ""):
        """Génère une réponse en streaming."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle."""
        pass


class STTProvider(ABC):
    """Interface abstraite pour les fournisseurs de Speech-to-Text."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcrit l'audio en texte."""
        pass
    
    @abstractmethod
    async def transcribe_streaming(self, audio_stream):
        """Transcrit un flux audio en continu."""
        pass


class TTSProvider(ABC):
    """Interface abstraite pour les fournisseurs de Text-to-Speech."""
    
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str = None) -> bytes:
        """Synthétise le texte en audio."""
        pass
    
    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Retourne la liste des voix disponibles."""
        pass


class VADProvider(ABC):
    """Interface abstraite pour la détection d'activité vocale."""
    
    @abstractmethod
    async def is_speech_detected(self, audio_data: bytes) -> bool:
        """Détecte si l'audio contient de la parole."""
        pass


class MetricsCollector(Protocol):
    """Interface pour le collecteur de métriques."""
    
    def record_metric(self, metric: MetricData) -> None:
        """Enregistre une métrique."""
        pass
    
    def get_metrics(self, name: Optional[str] = None) -> List[MetricData]:
        """Récupère les métriques."""
        pass


class AgentPlugin(ABC):
    """Interface abstraite pour les plugins d'agent personnalisés."""
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Traite un message et retourne une réponse."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom du plugin."""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Vérifie si le plugin est activé."""
        pass


@dataclass
class AgentConfig:
    """Configuration de l'agent."""
    system_instructions: str
    llm_model: str
    stt_model: str
    tts_model: str
    tts_voice: str
    enable_barge_in: bool = False
    min_endpointing_delay: float = 0.5
    max_response_time: float = 30.0
    plugins: List[str] = None


@dataclass
class ProcessingContext:
    """Contexte de traitement d'une requête."""
    session_id: str
    user_id: str
    room_id: str
    start_time: datetime
    metrics: List[MetricData] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = []
