# Documentation Complète du Code

## Vue d'ensemble du Projet

Ce projet implémente un **agent vocal intelligent** utilisant LiveKit WebRTC, avec une architecture modulaire basée sur des design patterns industriels.

## Structure du Projet

```
projet2/
├── serveur/                    # Serveur FastAPI (token generation, metrics API)
│   ├── main.py                # Point d'entrée du serveur
│   └── requirements.txt       # Dépendances serveur
├── worker/                    # Agent vocal LiveKit
│   ├── app.py                 # Point d'entrée principal du worker
│   ├── manage_agents.py       # CLI pour configuration NO-CODE
│   ├── core/                  # Architecture modulaire
│   │   ├── agent.py           # Agent principal
│   │   ├── config.py          # Gestionnaire de configuration
│   │   ├── factories.py       # Factory patterns (LLM, STT, TTS, Plugins)
│   │   ├── interfaces.py      # Interfaces abstraites
│   │   ├── metrics.py         # Collecteur de métriques
│   │   ├── session_manager.py # Gestionnaire de sessions LiveKit
│   │   ├── configuration_builder.py # Builder pattern
│   │   ├── dependency_container.py  # Injection de dépendances
│   │   ├── dynamic_provider_manager.py # Gestion NO-CODE des providers
│   │   ├── providers/         # Implémentations des providers
│   │   └── plugins/           # Plugins d'extension
│   ├── tests/                 # Suite de tests complète
│   └── requirements.txt       # Dépendances worker
└── client/                    # Interface web
    └── index.html            # Client LiveKit
```

## Architecture et Design Patterns

### 1. **Patterns Architecturaux**

#### **Singleton Pattern**
- `SessionManager`: Instance unique pour gérer toutes les sessions
- `DependencyContainer`: Conteneur global de dépendances

#### **Factory Pattern**
- `LLMProviderFactory`: Création des providers LLM
- `STTProviderFactory`: Création des providers STT
- `TTSProviderFactory`: Création des providers TTS
- `PluginFactory`: Création des plugins

#### **Builder Pattern**
- `ConfigurationBuilder`: Construction flexible de la configuration
- `DynamicProviderManager`: Configuration déclarative

#### **Dependency Injection**
- `DependencyContainer`: Gestion et résolution des dépendances

### 2. **Composants Principaux**

#### **Worker (`worker/app.py`)**
Point d'entrée principal du worker LiveKit.

**Responsabilités:**
- Initialisation des services via DI
- Configuration des providers via `DynamicProviderManager`
- Gestion du cycle de vie des sessions
- Collecte des métriques

**Flux d'exécution:**
1. Chargement de la configuration
2. Initialisation du conteneur DI
3. Connexion à la room LiveKit
4. Création de l'agent et de la session
5. Démarrage de la session avec métriques

#### **Serveur (`serveur/main.py`)**
Serveur FastAPI pour l'authentification et les métriques.

**Endpoints:**
- `GET /token`: Génération de tokens LiveKit
- `GET /metrics`: Métriques complètes
- `GET /metrics/simple`: Métriques simplifiées
- `GET /metrics/sessions`: Sessions actives

#### **DynamicProviderManager (`core/dynamic_provider_manager.py`)**
Système NO-CODE pour gérer les providers.

**Fonctionnalités:**
- Configuration via JSON et variables d'environnement
- Changement dynamique de providers
- Gestion des plugins
- Validation des configurations

## Configuration et Variables d'Environnement

### Variables Principales

```bash
# LiveKit
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# LLM
LLM_PROVIDER=openai|anthropic|cohere
LLM_MODEL=gpt-4o-mini|claude-3-sonnet
OPENAI_API_KEY=your-openai-key

# STT
STT_PROVIDER=openai|google|azure
STT_MODEL=whisper-1

# TTS
TTS_PROVIDER=openai|elevenlabs|azure
TTS_MODEL=tts-1|eleven_turbo_v2
TTS_VOICE_ID=alloy|nova|echo

# Plugins
ENABLED_PLUGINS=example,sentiment_analysis,profanity_filter

# Agent
AGENT_INSTRUCTIONS=Your system prompt here
ENABLE_METRICS=true
```

## API et Endpoints

### Serveur FastAPI

#### **Authentification**
```
GET /token?room={room}&identity={identity}
```
Retourne un token LiveKit pour rejoindre une room.

#### **Métriques**
```
GET /metrics              # Métriques complètes avec historique
GET /metrics/simple       # Métriques simplifiées
GET /metrics/sessions     # Sessions actives
GET /metrics/test         # Génération de métriques de test
```

### Gestion des Providers (NO-CODE)

#### **CLI Commands**
```bash
# Afficher la configuration
python manage_agents.py show

# Lister les providers disponibles
python manage_agents.py list-providers

# Changer de LLM
python manage_agents.py change-llm openai gpt-4o

# Changer de TTS
python manage_agents.py change-tts elevenlabs eleven_turbo_v2 --voice alloy

# Gérer les plugins
python manage_agents.py plugins list
python manage_agents.py plugins add --name sentiment_analysis
python manage_agents.py plugins remove --name example
```

## Système de Plugins

### Interface Plugin
```python
class AgentPlugin(ABC):
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        pass
```

### Plugins Disponibles

1. **`sentiment_analysis`**: Analyse des sentiments utilisateur
2. **`profanity_filter`**: Filtrage du contenu inapproprié
3. **`conversation_memory`**: Mémoire conversationnelle
4. **`example`**: Plugin de démonstration

## Métriques et Monitoring

### Types de Métriques

1. **Performance**:
   - Latence STT (Speech-to-Text)
   - Latence LLM (Large Language Model)
   - Latence TTS (Text-to-Speech)
   - TTFT (Time To First Token)
   - TTFB (Time To First Byte)

2. **Sessions**:
   - Sessions actives
   - Durée des sessions
   - Succès/échecs de connexion

3. **Plugins**:
   - Plugins actifs
   - Métriques par plugin

### Format des Métriques
```json
{
  "sessions": {
    "active_count": 5,
    "sessions": [...]
  },
  "performance": {
    "avg_stt_latency": 150.5,
    "avg_llm_latency": 850.2,
    "avg_tts_latency": 200.1
  },
  "timestamp": "2025-01-19T18:00:00Z"
}
```

## Tests et Validation

### Structure des Tests

```
tests/
├── unit/                    # Tests unitaires
│   ├── test_configuration_builder.py
│   ├── test_session_manager.py
│   └── test_dependency_container.py
├── integration/             # Tests d'intégration
│   └── test_entrypoint.py
└── error_handling/          # Tests de gestion d'erreur
    ├── test_configuration_errors.py
    └── test_connection_errors.py
```

### Commandes de Test
```bash
# Tests complets
python run_tests.py

# Tests unitaires
python -m pytest tests/unit/ -v

# Tests d'intégration
python -m pytest tests/integration/ -v
```

## Gestion d'Erreurs

### Exceptions Personnalisées

1. **`ConfigurationError`**: Erreurs de configuration
2. **`SessionCreationError`**: Échec de création de session
3. **`SessionStartError`**: Échec de démarrage de session
4. **`AgentCreationError`**: Échec de création d'agent
5. **`DependencyNotFoundError`**: Dépendance manquante

### Stratégies de Gestion
- Fallback vers configurations par défaut
- Logs structurés avec niveaux appropriés
- Nettoyage automatique des ressources
- Monitoring des erreurs via métriques

## Déploiement et Production

### Prérequis
- Python 3.8+
- LiveKit Cloud ou serveur auto-hébergé
- Clés API pour les providers choisis

### Variables de Production
```bash
# Sécurité
export LIVEKIT_API_SECRET="production-secret"
export OPENAI_API_KEY="production-key"

# Performance
export ENABLE_METRICS=true
export METRICS_RETENTION_HOURS=168  # 7 jours

# Logging
export LOG_LEVEL=INFO
export DEBUG=false
```

## Extensibilité

### Ajout de Nouveaux Providers

1. Créer une implémentation de l'interface appropriée
2. Enregistrer dans la factory correspondante
3. Ajouter la configuration dans `DynamicProviderManager`

### Ajout de Nouveaux Plugins

1. Implémenter l'interface `AgentPlugin`
2. Enregistrer dans `PluginFactory`
3. Configuration via CLI ou JSON

### Extension des Métriques

1. Ajouter de nouvelles métriques dans `MetricsCollector`
2. Instrumenter le code aux points appropriés
3. Exposer via l'API serveur

## Sécurité

### Bonnes Pratiques
- Validation des inputs utilisateur
- Sanitisation via plugins de filtrage
- Gestion sécurisée des tokens LiveKit
- Rotation des clés API en production

### Isolation
- Chaque plugin s'exécute de manière isolée
- Gestion des erreurs sans impact sur le système principal
- Limitation des ressources par session
