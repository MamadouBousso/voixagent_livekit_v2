# 🚀 Tutoriel Pas à Pas - Construction d'un Agent Vocal Intelligent

Ce tutoriel vous guide étape par étape pour construire un système d'agent vocal modulaire avec LiveKit WebRTC, des design patterns industriels et une configuration NO-CODE.

## 📋 Table des Matières

1. [Prérequis](#-prérequis)
2. [Architecture du Projet](#-architecture-du-projet)
3. [Initialisation du Projet](#-initialisation-du-projet)
4. [Configuration de l'Environnement](#-configuration-de-lenvironnement)
5. [Installation des Dépendances](#-installation-des-dépendances)
6. [Création de l'Architecture Modulaire](#-création-de-larchitecture-modulaire)
7. [Implémentation des Providers](#-implémentation-des-providers)
8. [Système de Plugins](#-système-de-plugins)
9. [Collecte de Métriques](#-collecte-de-métriques)
10. [Serveur FastAPI](#-serveur-fastapi)
11. [Client Web](#-client-web)
12. [Configuration NO-CODE](#-configuration-no-code)
13. [Tests et Validation](#-tests-et-validation)
14. [Makefile et Automation](#-makefile-et-automation)
15. [Déploiement](#-déploiement)

---

## 🎯 Prérequis

### Logiciels Requis
- **Python 3.8+** (recommandé: Python 3.11+)
- **Git** pour le contrôle de version
- **Node.js** (optionnel, pour outils frontend)

### Services Externes
- **Compte LiveKit Cloud** ou serveur LiveKit auto-hébergé
- **Compte OpenAI** (pour LLM, STT, TTS)
- **Compte ElevenLabs** (optionnel, pour TTS avancé)

---

## 🏗️ Architecture du Projet

Notre système sera composé de 3 composants principaux :

```
projet2/
├── serveur/              # FastAPI (authentification + métriques)
├── worker/               # Agent vocal LiveKit modulaire
└── client/               # Interface web
```

---

## 🚀 Étape 1: Initialisation du Projet

### 1.1 Créer la Structure de Base

```bash
# Créer le répertoire du projet
mkdir voice-agent-project
cd voice-agent-project

# Créer la structure des dossiers
mkdir -p serveur worker client worker/core worker/core/providers worker/core/plugins worker/tests
```

### 1.2 Initialiser Git

```bash
git init
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.log" >> .gitignore
echo ".pytest_cache/" >> .gitignore
```

---

## 🔧 Étape 2: Configuration de l'Environnement

### 2.1 Créer le Fichier de Configuration

Créer `worker/config_example.env` :

```bash
# ============================================================
# CONFIGURATION LIVEKIT
# ============================================================
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# ============================================================
# CONFIGURATION LLM
# ============================================================
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-api-key

# ============================================================
# CONFIGURATION STT/TTS
# ============================================================
STT_PROVIDER=openai
STT_MODEL=whisper-1
TTS_PROVIDER=openai
TTS_MODEL=tts-1
TTS_VOICE_ID=alloy

# ============================================================
# CONFIGURATION AGENT
# ============================================================
AGENT_INSTRUCTIONS=You are a friendly, concise assistant.

# ============================================================
# PLUGINS
# ============================================================
ENABLED_PLUGINS=example,sentiment_analysis

ENABLE_METRICS=true
```

### 2.2 Copier la Configuration

```bash
cp worker/config_example.env .env
# Éditer .env avec vos vraies clés API
```

---

## 📦 Étape 3: Installation des Dépendances

### 3.1 Dépendances Worker

Créer `worker/requirements.txt` :

```txt
livekit-agents
livekit-plugins-openai
livekit-plugins-elevenlabs
livekit-plugins-silero
python-dotenv
uvicorn[standard]
pytest
pytest-asyncio
```

### 3.2 Dépendances Serveur

Créer `serveur/requirements.txt` :

```txt
fastapi
uvicorn[standard]
python-dotenv
livekit
```

### 3.3 Installation

```bash
# Installer les dépendances
pip install -r worker/requirements.txt
pip install -r serveur/requirements.txt
```

---

## 🏛️ Étape 4: Création de l'Architecture Modulaire

### 4.1 Interfaces Abstraites

Créer `worker/core/interfaces.py` :

```python
"""
Interfaces abstraites pour l'architecture modulaire.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MetricData:
    """Données de métrique pour le monitoring."""
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
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations du modèle."""
        pass

class STTProvider(ABC):
    """Interface abstraite pour Speech-to-Text."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcrit l'audio en texte."""
        pass

class TTSProvider(ABC):
    """Interface abstraite pour Text-to-Speech."""
    
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str = None) -> bytes:
        """Synthétise le texte en audio."""
        pass

class AgentPlugin(ABC):
    """Interface abstraite pour les plugins d'agent."""
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Traite un message et retourne une réponse modifiée."""
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
```

### 4.2 Gestionnaire de Configuration

Créer `worker/core/config.py` :

```python
"""
Gestionnaire de configuration avec chargement depuis .env.
"""
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from .interfaces import AgentConfig

class ConfigManager:
    """Gestionnaire centralisé de la configuration."""
    
    def __init__(self):
        load_dotenv()
        self._config_cache = None
    
    def load_agent_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis les variables d'environnement."""
        config = {
            'system_instructions': os.getenv('AGENT_INSTRUCTIONS', 'You are a helpful assistant.'),
            'llm_model': os.getenv('LLM_MODEL', 'gpt-4o-mini'),
            'stt_model': os.getenv('STT_MODEL', 'whisper-1'),
            'tts_model': os.getenv('TTS_MODEL', 'tts-1'),
            'tts_voice': os.getenv('TTS_VOICE_ID', 'alloy'),
            'enable_barge_in': os.getenv('ENABLE_BARGE_IN', 'false').lower() == 'true',
            'min_endpointing_delay': float(os.getenv('MIN_ENDPOINTING_DELAY', '0.5')),
            'max_response_time': float(os.getenv('MAX_RESPONSE_TIME', '30.0')),
            'enabled_plugins': os.getenv('ENABLED_PLUGINS', '').split(',') if os.getenv('ENABLED_PLUGINS') else []
        }
        
        self._config_cache = config
        return config
```

### 4.3 Conteneur de Dépendances

Créer `worker/core/dependency_container.py` :

```python
"""
Conteneur d'injection de dépendances (pattern Singleton).
"""
from typing import Any, Dict, Type, TypeVar

T = TypeVar('T')

class DependencyContainer:
    """Conteneur simple pour l'injection de dépendances."""
    
    _instance = None
    _services: Dict[str, Any] = {}
    _singletons: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_service(self, name: str, service: Any) -> None:
        """Enregistre un service."""
        self._services[name] = service
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """Enregistre une instance singleton."""
        self._singletons[name] = instance
    
    def get_service(self, name: str) -> Any:
        """Récupère un service."""
        return self._services.get(name)
    
    def get_singleton(self, name: str) -> Any:
        """Récupère une instance singleton."""
        return self._singletons.get(name)

# Instance globale
container = DependencyContainer()
```

---

## 🏭 Étape 5: Implémentation des Providers

### 5.1 Factory des Providers

Créer `worker/core/factories.py` :

```python
"""
Factories pour créer les providers (pattern Factory).
"""
from typing import Dict, Type
from .interfaces import LLMProvider, STTProvider, TTSProvider, AgentPlugin

class LLMProviderFactory:
    """Factory pour créer les providers LLM."""
    
    _providers: Dict[str, Type[LLMProvider]] = {
        # Sera rempli avec les implémentations
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> LLMProvider:
        """Crée une instance du provider spécifié."""
        if provider_name not in cls._providers:
            raise ValueError(f"Provider LLM non supporté: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(**kwargs)
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """Enregistre un nouveau provider."""
        cls._providers[name] = provider_class

class PluginFactory:
    """Factory pour créer les plugins d'agent."""
    
    _plugins: Dict[str, Type[AgentPlugin]] = {}
    
    @classmethod
    def create(cls, plugin_name: str, **kwargs) -> AgentPlugin:
        """Crée une instance du plugin spécifié."""
        if plugin_name not in cls._plugins:
            raise ValueError(f"Plugin non supporté: {plugin_name}")
        
        plugin_class = cls._plugins[plugin_name]
        return plugin_class(**kwargs)
    
    @classmethod
    def register_plugin(cls, name: str, plugin_class: Type[AgentPlugin]):
        """Enregistre un nouveau plugin."""
        cls._plugins[name] = plugin_class
    
    @classmethod
    def list_available_plugins(cls) -> list[str]:
        """Retourne la liste des plugins disponibles."""
        return list(cls._plugins.keys())
```

### 5.2 Provider OpenAI

Créer `worker/core/providers/openai_provider.py` :

```python
"""
Implémentation du provider OpenAI pour LLM, STT, TTS.
"""
from typing import Dict, Any
import openai
from ..interfaces import LLMProvider, STTProvider, TTSProvider

class OpenAILLMProvider(LLMProvider):
    """Provider OpenAI pour LLM."""
    
    def __init__(self, model: str = "gpt-4o-mini", **kwargs):
        self.model = model
        self.client = openai.OpenAI()
    
    async def generate_response(self, message: str, system_prompt: str = "") -> str:
        """Génère une réponse avec OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Erreur génération réponse OpenAI: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les infos du modèle."""
        return {
            "provider": "openai",
            "model": self.model,
            "type": "llm"
        }

class OpenAISTTProvider(STTProvider):
    """Provider OpenAI pour STT."""
    
    def __init__(self, model: str = "whisper-1", **kwargs):
        self.model = model
        self.client = openai.OpenAI()
    
    async def transcribe(self, audio_data: bytes) -> str:
        """Transcrit l'audio avec Whisper."""
        try:
            transcript = await self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_data
            )
            return transcript.text
        except Exception as e:
            raise Exception(f"Erreur transcription OpenAI: {e}")

class OpenAITTSProvider(TTSProvider):
    """Provider OpenAI pour TTS."""
    
    def __init__(self, model: str = "tts-1", voice: str = "alloy", **kwargs):
        self.model = model
        self.voice = voice
        self.client = openai.OpenAI()
    
    async def synthesize(self, text: str, voice_id: str = None) -> bytes:
        """Synthétise le texte en audio."""
        voice_to_use = voice_id or self.voice
        try:
            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice_to_use,
                input=text
            )
            return response.content
        except Exception as e:
            raise Exception(f"Erreur synthèse OpenAI: {e}")
```

### 5.3 Enregistrement des Providers

Mettre à jour `worker/core/factories.py` :

```python
# ... imports précédents ...
from .providers.openai_provider import OpenAILLMProvider, OpenAISTTProvider, OpenAITTSProvider

class LLMProviderFactory:
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAILLMProvider,
    }
    # ... reste du code ...

class STTProviderFactory:
    _providers: Dict[str, Type[STTProvider]] = {
        "openai": OpenAISTTProvider,
    }

class TTSProviderFactory:
    _providers: Dict[str, Type[TTSProvider]] = {
        "openai": OpenAITTSProvider,
    }
```

---

## 🔌 Étape 6: Système de Plugins

### 6.1 Plugin d'Exemple

Créer `worker/core/plugins/example_plugin.py` :

```python
"""
Plugin d'exemple pour démontrer le système de plugins.
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
        
        # Exemple de traitement simple
        if "hello" in message.lower():
            return message + " (Processed by Example Plugin!)"
        
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled
```

### 6.2 Plugin d'Analyse des Sentiments

Créer `worker/core/plugins/sentiment_analysis_plugin.py` :

```python
"""
Plugin d'analyse des sentiments pour l'agent vocal.
"""
import re
from typing import Dict, Any
from ..interfaces import AgentPlugin

class SentimentAnalysisPlugin(AgentPlugin):
    """Plugin simple d'analyse des sentiments."""
    
    def __init__(self, **kwargs):
        self.name = "Sentiment Analysis Plugin"
        self.enabled = kwargs.get('enabled', True)
        self.threshold = kwargs.get('threshold', 0.5)
        
        self.positive_words = {'merci', 'parfait', 'excellent', 'super', 'bien'}
        self.negative_words = {'nul', 'mauvais', 'problème', 'erreur', 'énervé'}
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Analyse le sentiment du message."""
        if not self.is_enabled():
            return message
        
        sentiment_score = self._analyze_sentiment(message)
        
        context['sentiment_analysis'] = {
            'score': sentiment_score,
            'emotion': self._get_emotion_label(sentiment_score)
        }
        
        if sentiment_score < -self.threshold:
            context['response_prefix'] = "Je comprends votre frustration. "
        elif sentiment_score > self.threshold:
            context['response_prefix'] = "Je suis content de vous aider ! "
        
        return message
    
    def _analyze_sentiment(self, message: str) -> float:
        """Analyse simple du sentiment."""
        words = re.findall(r'\w+', message.lower())
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _get_emotion_label(self, score: float) -> str:
        """Retourne un label d'émotion."""
        if score > 0.3:
            return "positive"
        elif score < -0.3:
            return "negative"
        else:
            return "neutral"
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return self.enabled
```

### 6.3 Enregistrement des Plugins

Mettre à jour `worker/core/factories.py` :

```python
from .plugins.example_plugin import ExampleAgentPlugin
from .plugins.sentiment_analysis_plugin import SentimentAnalysisPlugin

class PluginFactory:
    _plugins: Dict[str, Type[AgentPlugin]] = {
        "example": ExampleAgentPlugin,
        "sentiment_analysis": SentimentAnalysisPlugin,
    }
    # ... reste du code ...
```

---

## 📊 Étape 7: Collecte de Métriques

### 7.1 Collecteur de Métriques

Créer `worker/core/metrics.py` :

```python
"""
Système de collecte et monitoring des métriques (pattern Observer).
"""
import json
import os
import threading
from collections import deque
from datetime import datetime
from typing import Callable, List, Optional, Dict, Any
from .interfaces import MetricData

class MetricsCollector:
    """Collecteur de métriques avec pattern Observer."""
    
    def __init__(self, max_history: int = 1000):
        self._metrics_history: deque = deque(maxlen=max_history)
        self._observers: List[Callable[[MetricData], None]] = []
        self._session_metrics: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Fichier partagé pour le serveur
        self._shared_file = os.path.join(os.path.dirname(__file__), '..', 'shared_metrics.json')
    
    def record_metric(self, metric: MetricData) -> None:
        """Enregistre une métrique et notifie les observateurs."""
        with self._lock:
            self._metrics_history.append(metric)
            
            # Notifier les observateurs
            for observer in self._observers:
                try:
                    observer(metric)
                except Exception as e:
                    print(f"Erreur dans l'observateur: {e}")
            
            # Sauvegarder dans le fichier partagé
            try:
                self._update_shared_file()
            except Exception as e:
                print(f"Erreur sauvegarde métrique: {e}")
    
    def add_observer(self, observer: Callable[[MetricData], None]) -> None:
        """Ajoute un observateur."""
        self._observers.append(observer)
    
    def get_recent_metrics(self, count: int = 100) -> List[MetricData]:
        """Retourne les métriques récentes."""
        with self._lock:
            return list(self._metrics_history)[-count:]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des métriques."""
        with self._lock:
            if not self._metrics_history:
                return {}
            
            recent_metrics = list(self._metrics_history)[-100:]
            
            return {
                'total_metrics': len(self._metrics_history),
                'recent_count': len(recent_metrics),
                'sessions_active': len(self._session_metrics),
                'last_update': datetime.now().isoformat()
            }
    
    def _update_shared_file(self) -> None:
        """Met à jour le fichier partagé."""
        data = {
            'recent_metrics': [
                {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'unit': m.unit
                } for m in self.get_recent_metrics(50)
            ],
            'summary': self.get_metrics_summary(),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(self._shared_file, 'w') as f:
            json.dump(data, f, indent=2)

# Instance globale
metrics_collector = MetricsCollector()
```

---

## 🌐 Étape 8: Serveur FastAPI

### 8.1 Serveur Principal

Créer `serveur/main.py` :

```python
"""
Serveur FastAPI pour l'authentification et les métriques.
"""
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import livekit.api as lk_api

load_dotenv()

app = FastAPI()

# Variables d'environnement
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

@app.get("/token")
def create_token(room: str, identity: str):
    """Génère un token JWT pour LiveKit."""
    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise HTTPException(status_code=500, detail="Configuration LiveKit manquante")
    
    token = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    token.with_identity(identity).with_name(identity)
    
    grants = lk_api.VideoGrants(
        room_join=True,
        room=room,
        can_publish=True,
        can_subscribe=True,
    )
    token.with_grants(grants)
    
    return {
        "url": LIVEKIT_URL,
        "token": token.to_jwt()
    }

@app.get("/metrics")
def get_metrics():
    """Récupère les métriques du worker."""
    shared_file = os.path.join(os.path.dirname(__file__), '..', 'worker', 'shared_metrics.json')
    
    try:
        with open(shared_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Metrics file not found"}
    except Exception as e:
        return {"error": f"Error reading metrics: {e}"}

# Servir les fichiers statiques
app.mount("/", StaticFiles(directory="../client", html=True), name="client")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## 🎨 Étape 9: Client Web

### 9.1 Interface Client

Créer `client/index.html` :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Vocal Intelligent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 8px;
            cursor: pointer;
            margin: 10px 5px;
        }
        button:hover {
            background: #45a049;
        }
        button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Agent Vocal Intelligent</h1>
        
        <div class="status" id="status">
            <strong>Statut:</strong> <span id="statusText">Déconnecté</span>
        </div>
        
        <div>
            <input type="text" id="roomInput" placeholder="Nom de la salle" value="test-room">
            <input type="text" id="nameInput" placeholder="Votre nom" value="web-client">
            <button id="connectBtn" onclick="connect()">Se Connecter</button>
            <button id="disconnectBtn" onclick="disconnect()" disabled>Se Déconnecter</button>
        </div>
        
        <div id="controls" style="display: none;">
            <h3>Contrôles</h3>
            <button id="micBtn" onclick="toggleMic()">🎤 Microphone Activé</button>
            <button onclick="testAgent()">🧪 Tester l'Agent</button>
        </div>
        
        <div id="metrics" style="margin-top: 20px;">
            <h3>📊 Métriques</h3>
            <div id="metricsDisplay">Chargement...</div>
        </div>
    </div>

    <script src="https://unpkg.com/livekit-client@latest/dist/livekit-client.umd.js"></script>
    <script>
        let room = null;
        let isMicEnabled = true;

        async function connect() {
            const roomName = document.getElementById('roomInput').value;
            const identity = document.getElementById('nameInput').value;
            
            if (!roomName || !identity) {
                alert('Veuillez saisir le nom de la salle et votre identité');
                return;
            }

            try {
                // Obtenir un token
                const tokenResponse = await fetch(`/token?room=${roomName}&identity=${identity}`);
                const { url, token } = await tokenResponse.json();

                // Créer la connexion LiveKit
                room = new LiveKitClient.Room();
                
                room.on(LiveKitClient.RoomEvent.Connected, () => {
                    updateStatus('Connecté');
                    document.getElementById('connectBtn').disabled = true;
                    document.getElementById('disconnectBtn').disabled = false;
                    document.getElementById('controls').style.display = 'block';
                    loadMetrics();
                });

                room.on(LiveKitClient.RoomEvent.Disconnected, () => {
                    updateStatus('Déconnecté');
                    document.getElementById('connectBtn').disabled = false;
                    document.getElementById('disconnectBtn').disabled = true;
                    document.getElementById('controls').style.display = 'none';
                });

                await room.connect(url, token);
                
            } catch (error) {
                console.error('Erreur de connexion:', error);
                updateStatus('Erreur de connexion');
            }
        }

        async function disconnect() {
            if (room) {
                await room.disconnect();
                room = null;
            }
        }

        async function toggleMic() {
            if (room) {
                const micBtn = document.getElementById('micBtn');
                if (isMicEnabled) {
                    await room.localParticipant.setMicrophoneEnabled(false);
                    micBtn.textContent = '🎤 Microphone Désactivé';
                    isMicEnabled = false;
                } else {
                    await room.localParticipant.setMicrophoneEnabled(true);
                    micBtn.textContent = '🎤 Microphone Activé';
                    isMicEnabled = true;
                }
            }
        }

        async function testAgent() {
            if (room) {
                console.log('Test de l\'agent...');
                // Ici vous pouvez ajouter la logique de test
            }
        }

        function updateStatus(status) {
            document.getElementById('statusText').textContent = status;
        }

        async function loadMetrics() {
            try {
                const response = await fetch('/metrics');
                const metrics = await response.json();
                
                const display = document.getElementById('metricsDisplay');
                if (metrics.error) {
                    display.innerHTML = `<p>Erreur: ${metrics.error}</p>`;
                } else {
                    display.innerHTML = `
                        <p><strong>Métriques récentes:</strong> ${metrics.summary?.recent_count || 0}</p>
                        <p><strong>Sessions actives:</strong> ${metrics.summary?.sessions_active || 0}</p>
                        <p><strong>Dernière mise à jour:</strong> ${metrics.timestamp || 'N/A'}</p>
                    `;
                }
            } catch (error) {
                console.error('Erreur chargement métriques:', error);
            }
        }

        // Charger les métriques au démarrage
        loadMetrics();
        setInterval(loadMetrics, 5000); // Actualiser toutes les 5 secondes
    </script>
</body>
</html>
```

---

## ⚙️ Étape 10: Agent Principal et Configuration

### 10.1 Agent Principal

Créer `worker/app.py` :

```python
"""
Point d'entrée principal de l'agent vocal modulaire.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

from livekit.agents import JobContext, WorkerOptions, cli
from livekit.plugins import openai, silero

# Imports de l'architecture modulaire
from core.config import ConfigManager
from core.dependency_container import container
from core.factories import LLMProviderFactory, PluginFactory

load_dotenv()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation des services
config_manager = ConfigManager()
agent_config = config_manager.load_agent_config()

# Enregistrement dans le conteneur DI
container.register_singleton('config_manager', config_manager)
container.register_service('agent_config', agent_config)

async def entrypoint(ctx: JobContext):
    """Point d'entrée principal de l'agent."""
    logger.info(f"=== AGENT DÉMARRÉ - Room: {ctx.room.name} ===")
    
    try:
        # Charger la configuration
        config = container.get_service('agent_config')
        
        # Créer les providers
        stt = openai.STT(model=config['stt_model'])
        llm = openai.LLM(model=config['llm_model'])
        tts = openai.TTS(
            model=config['tts_model'],
            voice=config['tts_voice']
        )
        vad = silero.VAD.load()
        
        # Créer la session agent
        from livekit.agents import AgentSession
        session = AgentSession(
            vad=vad,
            stt=stt,
            llm=llm,
            tts=tts
        )
        
        # Charger les plugins
        plugins = []
        for plugin_name in config.get('enabled_plugins', []):
            if plugin_name.strip():
                try:
                    plugin = PluginFactory.create(plugin_name)
                    plugins.append(plugin)
                    logger.info(f"Plugin chargé: {plugin.get_name()}")
                except Exception as e:
                    logger.warning(f"Erreur chargement plugin {plugin_name}: {e}")
        
        # Démarrer la session
        await session.start(agent=None, room=ctx.room)
        
        logger.info("=== SESSION TERMINÉE ===")
        
    except Exception as e:
        logger.error(f"Erreur dans entrypoint: {e}")
        raise

if __name__ == "__main__":
    # Lancer l'agent
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

---

## 🔧 Étape 11: Configuration NO-CODE

### 11.1 Gestionnaire de Configuration Dynamique

Créer `worker/core/dynamic_provider_manager.py` :

```python
"""
Gestionnaire dynamique des providers et plugins (NO-CODE).
"""
import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration des providers."""
    provider_name: str
    model: str
    api_key: str = None
    voice_id: str = None

@dataclass
class SystemConfig:
    """Configuration système complète."""
    llm: ProviderConfig
    stt: ProviderConfig
    tts: ProviderConfig
    enabled_plugins: List[str]

class DynamicProviderManager:
    """Gestionnaire de configuration dynamique."""
    
    def __init__(self):
        self._config = self.load_config()
    
    def load_config(self) -> SystemConfig:
        """Charge la configuration depuis .env."""
        return SystemConfig(
            llm=ProviderConfig(
                provider_name=os.getenv('LLM_PROVIDER', 'openai'),
                model=os.getenv('LLM_MODEL', 'gpt-4o-mini'),
                api_key=os.getenv('OPENAI_API_KEY', '')
            ),
            stt=ProviderConfig(
                provider_name=os.getenv('STT_PROVIDER', 'openai'),
                model=os.getenv('STT_MODEL', 'whisper-1')
            ),
            tts=ProviderConfig(
                provider_name=os.getenv('TTS_PROVIDER', 'openai'),
                model=os.getenv('TTS_MODEL', 'tts-1'),
                voice_id=os.getenv('TTS_VOICE_ID', 'alloy')
            ),
            enabled_plugins=os.getenv('ENABLED_PLUGINS', '').split(',') if os.getenv('ENABLED_PLUGINS') else []
        )
    
    def get_config(self) -> SystemConfig:
        """Retourne la configuration actuelle."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Met à jour la configuration."""
        # Logique de mise à jour
        pass
```

### 11.2 CLI de Gestion

Créer `worker/manage_agents.py` :

```python
#!/usr/bin/env python3
"""
CLI pour la gestion NO-CODE des agents.
"""
import argparse
import json
import os
from core.dynamic_provider_manager import DynamicProviderManager
from core.factories import PluginFactory

def show_config():
    """Affiche la configuration actuelle."""
    manager = DynamicProviderManager()
    config = manager.get_config()
    
    print("🔧 Configuration actuelle:")
    print("=" * 50)
    print(f"LLM: {config.llm.provider_name}/{config.llm.model}")
    print(f"STT: {config.stt.provider_name}/{config.stt.model}")
    print(f"TTS: {config.tts.provider_name}/{config.tts.model}")
    
    print("\n🔌 Plugins actifs:")
    for plugin in config.enabled_plugins:
        if plugin.strip():
            print(f"  ✅ {plugin}")

def list_providers():
    """Liste les providers disponibles."""
    print("📋 Providers disponibles:")
    print("=" * 50)
    print("LLM: openai, anthropic (bientôt)")
    print("STT: openai, google (bientôt)")
    print("TTS: openai, elevenlabs (bientôt)")

def change_llm(provider: str, model: str):
    """Change le provider LLM."""
    print(f"🧠 Changement LLM vers {provider}/{model}")
    # Logique de changement (mise à jour .env)

def plugins_list():
    """Liste les plugins disponibles."""
    available = PluginFactory.list_available_plugins()
    print("🔌 Plugins disponibles:")
    print("=" * 50)
    for plugin in available:
        print(f"  • {plugin}")

def main():
    parser = argparse.ArgumentParser(description="Gestion des agents")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    subparsers.add_parser('show', help='Afficher la configuration')
    subparsers.add_parser('list-providers', help='Lister les providers')
    
    llm_parser = subparsers.add_parser('change-llm', help='Changer le LLM')
    llm_parser.add_argument('provider', help='Nom du provider')
    llm_parser.add_argument('model', help='Nom du modèle')
    
    subparsers.add_parser('plugins', help='Lister les plugins')
    
    args = parser.parse_args()
    
    if args.command == 'show':
        show_config()
    elif args.command == 'list-providers':
        list_providers()
    elif args.command == 'change-llm':
        change_llm(args.provider, args.model)
    elif args.command == 'plugins':
        plugins_list()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

## 🧪 Étape 12: Tests et Validation

### 12.1 Tests Unitaires

Créer `worker/tests/unit/test_config.py` :

```python
"""
Tests unitaires pour le gestionnaire de configuration.
"""
import unittest
from unittest.mock import patch
import os
from core.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    """Tests pour ConfigManager."""
    
    def test_load_agent_config(self):
        """Test du chargement de configuration."""
        with patch.dict(os.environ, {
            'AGENT_INSTRUCTIONS': 'Test instructions',
            'LLM_MODEL': 'test-model',
            'STT_MODEL': 'test-stt'
        }):
            manager = ConfigManager()
            config = manager.load_agent_config()
            
            self.assertEqual(config['system_instructions'], 'Test instructions')
            self.assertEqual(config['llm_model'], 'test-model')
            self.assertEqual(config['stt_model'], 'test-stt')

if __name__ == '__main__':
    unittest.main()
```

### 12.2 Script de Tests

Créer `worker/run_tests.py` :

```python
#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests.
"""
import subprocess
import sys
import os

def run_tests():
    """Exécute tous les tests."""
    os.chdir(os.path.dirname(__file__))
    
    print("🧪 Exécution des tests...")
    
    # Tests unitaires
    result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', 'tests'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tous les tests ont réussi!")
    else:
        print("❌ Certains tests ont échoué:")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
```

---

## 🛠️ Étape 13: Makefile et Automation

### 13.1 Makefile Complet

Créer `Makefile` :

```makefile
# Makefile pour l'agent vocal intelligent

SHELL := /bin/bash
WORKER_DIR := worker
SERVER_DIR := serveur

.PHONY: help install start stop test

help: ## 📋 Afficher cette aide
	@echo "🤖 AGENT VOCAL INTELLIGENT"
	@echo "=========================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "\033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install: ## 🔧 Installer les dépendances
	@echo "📦 Installation des dépendances..."
	cd $(WORKER_DIR) && pip install -r requirements.txt
	cd $(SERVER_DIR) && pip install -r requirements.txt
	@echo "✅ Installation terminée"

setup: ## ⚙️ Configuration initiale
	@if [ ! -f .env ]; then \
		cp $(WORKER_DIR)/config_example.env .env; \
		echo "🔑 Éditez le fichier .env avec vos clés API!"; \
	fi
	@echo "✅ Configuration initiale terminée"

start: ## 🚀 Démarrer les services
	@echo "🚀 Démarrage des services..."
	cd $(SERVER_DIR) && python main.py &
	sleep 3
	cd $(WORKER_DIR) && python app.py dev &
	@echo "✅ Services démarrés"

stop: ## 🛑 Arrêter les services
	@pkill -f "python.*main.py" 2>/dev/null || true
	@pkill -f "python.*app.py" 2>/dev/null || true
	@echo "✅ Services arrêtés"

test: ## 🧪 Lancer les tests
	cd $(WORKER_DIR) && python run_tests.py

config-show: ## 🔍 Afficher la configuration
	cd $(WORKER_DIR) && python manage_agents.py show

change-llm: ## 🧠 Changer le LLM
	cd $(WORKER_DIR) && python manage_agents.py change-llm $(PROVIDER) $(MODEL)

plugins: ## 🔌 Lister les plugins
	cd $(WORKER_DIR) && python manage_agents.py plugins

metrics: ## 📊 Afficher les métriques
	curl -s http://localhost:8080/metrics | python -m json.tool
```

---

## 🚀 Étape 14: Déploiement et Utilisation

### 14.1 Démarrage Rapide

```bash
# 1. Installation et configuration
make install
make setup

# 2. Éditer .env avec vos clés API
nano .env

# 3. Démarrer le système
make start

# 4. Ouvrir http://localhost:8080
```

### 14.2 Configuration des Providers

```bash
# Voir la configuration actuelle
make config-show

# Changer le LLM
make change-llm openai gpt-4o

# Lister les plugins
make plugins
```

### 14.3 Monitoring

```bash
# Voir les métriques
make metrics

# Lancer les tests
make test
```

---

## 🎯 Résumé et Prochaines Étapes

### ✅ Ce que nous avons construit :

1. **Architecture Modulaire** - Design patterns industriels
2. **Providers Extensibles** - LLM, STT, TTS configurables
3. **Système de Plugins** - Extensibilité sans code
4. **Métriques et Monitoring** - Observabilité complète
5. **Configuration NO-CODE** - Gestion via CLI
6. **Tests Automatisés** - Suite de tests complète
7. **Interface Web** - Client LiveKit moderne

### 🚀 Améliorations Possibles :

1. **Providers Additionnels** - Anthropic, Google, ElevenLabs
2. **Plugins Avancés** - Traduction, DB, APIs externes
3. **Interface Admin** - Dashboard web complet
4. **Déploiement** - Docker, CI/CD
5. **Monitoring** - Grafana, Prometheus
6. **Sécurité** - Authentification, autorisation

### 📚 Documentation Complète :

- `README.md` - Guide principal
- `CODE_DOCUMENTATION.md` - Architecture détaillée
- `MAKEFILE_COMMANDS.md` - Guide des commandes
- `PLUGINS_GUIDE.md` - Guide des plugins

**Votre agent vocal intelligent est maintenant prêt ! 🎉**

Utilisez `make help` pour voir toutes les commandes disponibles et commencez à construire votre assistant vocal personnalisé !
