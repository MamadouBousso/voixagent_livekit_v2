"""
Dynamic Provider Manager - Gestion dynamique des providers sans coder
Permet de changer STT, TTS, LLM et d'ajouter des plugins via configuration
"""

import os
import json
import importlib
from typing import Dict, Any, Optional, List, Type
from pathlib import Path
from dataclasses import dataclass, asdict
from .interfaces import LLMProvider, STTProvider, TTSProvider, VADProvider, AgentPlugin
from .factories import LLMProviderFactory, STTProviderFactory, TTSProviderFactory, VADProviderFactory, PluginFactory


@dataclass
class ProviderConfig:
    """Configuration d'un provider"""
    provider_name: str
    model: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    voice_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    extra_params: Optional[Dict[str, Any]] = None


@dataclass
class PluginConfig:
    """Configuration d'un plugin"""
    plugin_name: str
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None


@dataclass
class DynamicAgentConfig:
    """Configuration dynamique complète de l'agent"""
    # Providers
    llm: ProviderConfig
    stt: ProviderConfig
    tts: ProviderConfig
    vad: ProviderConfig
    
    # Plugins
    enabled_plugins: List[PluginConfig]
    
    # Agent settings
    instructions: str
    enable_barge_in: bool = False
    min_endpointing_delay: float = 0.5
    max_response_time: float = 30.0
    
    # Metrics
    enable_metrics: bool = True
    metrics_retention_hours: int = 24


class DynamicProviderManager:
    """
    Gestionnaire dynamique des providers - NO-CODE configuration
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self._config: Optional[DynamicAgentConfig] = None
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Retourne le chemin par défaut du fichier de configuration"""
        return os.path.join(os.path.dirname(__file__), '..', 'agent_config.json')
    
    def _load_config(self) -> None:
        """Charge la configuration depuis le fichier et l'environnement"""
        # 1. Charger depuis le fichier JSON (si existe)
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self._config = self._dict_to_config(config_data)
        else:
            # 2. Créer depuis les variables d'environnement
            self._config = self._load_from_environment()
    
    def _load_from_environment(self) -> DynamicAgentConfig:
        """Charge la configuration depuis les variables d'environnement"""
        
        # Configuration LLM
        llm_config = ProviderConfig(
            provider_name=os.getenv("LLM_PROVIDER", "openai"),
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
        )
        
        # Configuration STT
        stt_config = ProviderConfig(
            provider_name=os.getenv("STT_PROVIDER", "openai"),
            model=os.getenv("STT_MODEL", "whisper-1"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        )
        
        # Configuration TTS
        tts_config = ProviderConfig(
            provider_name=os.getenv("TTS_PROVIDER", "openai"),
            model=os.getenv("TTS_MODEL", "tts-1"),
            voice_id=os.getenv("TTS_VOICE_ID", "alloy"),
            api_key=os.getenv("OPENAI_API_KEY") or os.getenv("ELEVENLABS_API_KEY"),
        )
        
        # Configuration VAD
        vad_config = ProviderConfig(
            provider_name=os.getenv("VAD_PROVIDER", "silero"),
            model="silero-vad",  # Silero n'a pas de modèle configurable
        )
        
        # Configuration plugins
        enabled_plugins_list = os.getenv("ENABLED_PLUGINS", "example").split(',')
        enabled_plugins = [
            PluginConfig(plugin_name=name.strip(), enabled=True)
            for name in enabled_plugins_list if name.strip()
        ]
        
        return DynamicAgentConfig(
            llm=llm_config,
            stt=stt_config,
            tts=tts_config,
            vad=vad_config,
            enabled_plugins=enabled_plugins,
            instructions=os.getenv("AGENT_INSTRUCTIONS", "You are a friendly, concise assistant. Keep answers short."),
            enable_barge_in=os.getenv("ENABLE_BARGE_IN", "false").lower() == "true",
            min_endpointing_delay=float(os.getenv("MIN_ENDPOINTING_DELAY", "0.5")),
            max_response_time=float(os.getenv("MAX_RESPONSE_TIME", "30.0")),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            metrics_retention_hours=int(os.getenv("METRICS_RETENTION_HOURS", "24")),
        )
    
    def _dict_to_config(self, data: Dict[str, Any]) -> DynamicAgentConfig:
        """Convertit un dictionnaire en DynamicAgentConfig"""
        return DynamicAgentConfig(
            llm=ProviderConfig(**data['llm']),
            stt=ProviderConfig(**data['stt']),
            tts=ProviderConfig(**data['tts']),
            vad=ProviderConfig(**data['vad']),
            enabled_plugins=[PluginConfig(**plugin) for plugin in data['enabled_plugins']],
            instructions=data['instructions'],
            enable_barge_in=data.get('enable_barge_in', False),
            min_endpointing_delay=data.get('min_endpointing_delay', 0.5),
            max_response_time=data.get('max_response_time', 30.0),
            enable_metrics=data.get('enable_metrics', True),
            metrics_retention_hours=data.get('metrics_retention_hours', 24),
        )
    
    def get_config(self) -> DynamicAgentConfig:
        """Retourne la configuration actuelle"""
        return self._config
    
    def update_provider(self, provider_type: str, new_config: ProviderConfig) -> None:
        """
        Met à jour un provider sans redémarrer l'application
        
        Args:
            provider_type: 'llm', 'stt', 'tts', ou 'vad'
            new_config: Nouvelle configuration du provider
        """
        if provider_type == 'llm':
            self._config.llm = new_config
        elif provider_type == 'stt':
            self._config.stt = new_config
        elif provider_type == 'tts':
            self._config.tts = new_config
        elif provider_type == 'vad':
            self._config.vad = new_config
        else:
            raise ValueError(f"Type de provider invalide: {provider_type}")
        
        # Sauvegarder la configuration
        self.save_config()
    
    def add_plugin(self, plugin_config: PluginConfig) -> None:
        """Ajoute un plugin à la configuration"""
        # Vérifier si le plugin existe déjà
        existing = [p for p in self._config.enabled_plugins if p.plugin_name == plugin_config.plugin_name]
        if existing:
            # Mettre à jour la configuration existante
            existing[0].enabled = plugin_config.enabled
            existing[0].config = plugin_config.config
        else:
            # Ajouter un nouveau plugin
            self._config.enabled_plugins.append(plugin_config)
        
        self.save_config()
    
    def remove_plugin(self, plugin_name: str) -> None:
        """Supprime un plugin de la configuration"""
        self._config.enabled_plugins = [
            p for p in self._config.enabled_plugins if p.plugin_name != plugin_name
        ]
        self.save_config()
    
    def save_config(self) -> None:
        """Sauvegarde la configuration dans le fichier JSON"""
        config_dict = asdict(self._config)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
    
    def create_llm_provider(self) -> LLMProvider:
        """Crée le provider LLM selon la configuration"""
        config = self._config.llm
        kwargs = {
            'model': config.model,
            'api_key': config.api_key,
        }
        if config.temperature is not None:
            kwargs['temperature'] = config.temperature
        if config.max_tokens is not None:
            kwargs['max_tokens'] = config.max_tokens
        if config.extra_params:
            kwargs.update(config.extra_params)
        
        return LLMProviderFactory.create(config.provider_name, **kwargs)
    
    def create_stt_provider(self) -> STTProvider:
        """Crée le provider STT selon la configuration"""
        config = self._config.stt
        kwargs = {
            'model': config.model,
            'api_key': config.api_key,
        }
        if config.extra_params:
            kwargs.update(config.extra_params)
        
        return STTProviderFactory.create(config.provider_name, **kwargs)
    
    def create_tts_provider(self) -> TTSProvider:
        """Crée le provider TTS selon la configuration"""
        config = self._config.tts
        kwargs = {
            'model': config.model,
            'api_key': config.api_key,
        }
        if config.voice_id:
            kwargs['voice'] = config.voice_id
        if config.extra_params:
            kwargs.update(config.extra_params)
        
        return TTSProviderFactory.create(config.provider_name, **kwargs)
    
    def create_vad_provider(self) -> VADProvider:
        """Crée le provider VAD selon la configuration"""
        config = self._config.vad
        kwargs = {}
        if config.extra_params:
            kwargs.update(config.extra_params)
        
        return VADProviderFactory.create(config.provider_name, **kwargs)
    
    def get_active_plugins(self) -> List[AgentPlugin]:
        """Retourne la liste des plugins actifs"""
        active_plugins = []
        for plugin_config in self._config.enabled_plugins:
            if plugin_config.enabled:
                try:
                    kwargs = plugin_config.config or {}
                    plugin = PluginFactory.create(plugin_config.plugin_name, **kwargs)
                    active_plugins.append(plugin)
                except ValueError as e:
                    print(f"Warning: Plugin {plugin_config.plugin_name} non disponible: {e}")
        
        return active_plugins
    
    def list_available_providers(self) -> Dict[str, List[str]]:
        """Liste tous les providers disponibles"""
        return {
            'llm': list(LLMProviderFactory._providers.keys()),
            'stt': list(STTProviderFactory._providers.keys()),
            'tts': list(TTSProviderFactory._providers.keys()),
            'vad': list(VADProviderFactory._providers.keys()),
        }
    
    def list_available_plugins(self) -> List[str]:
        """Liste tous les plugins disponibles"""
        return PluginFactory.list_available_plugins()
    
    def create_config_template(self, output_file: str) -> None:
        """Crée un fichier de configuration template"""
        template_config = {
            "llm": {
                "provider_name": "openai",
                "model": "gpt-4o-mini",
                "api_key": "your-openai-api-key",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "stt": {
                "provider_name": "openai",
                "model": "whisper-1",
                "api_key": "your-openai-api-key"
            },
            "tts": {
                "provider_name": "openai",
                "model": "tts-1",
                "voice_id": "alloy",
                "api_key": "your-openai-api-key"
            },
            "vad": {
                "provider_name": "silero",
                "model": "silero-vad"
            },
            "enabled_plugins": [
                {
                    "plugin_name": "example",
                    "enabled": True,
                    "config": {}
                }
            ],
            "instructions": "You are a friendly, concise assistant. Keep answers short and helpful.",
            "enable_barge_in": False,
            "min_endpointing_delay": 0.5,
            "max_response_time": 30.0,
            "enable_metrics": True,
            "metrics_retention_hours": 24
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(template_config, f, indent=2, ensure_ascii=False)
