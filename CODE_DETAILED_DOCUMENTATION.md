# Documentation Détaillée du Code

## Fichiers Principaux

### 1. **Worker Principal** (`worker/app.py`)

**Rôle**: Point d'entrée principal du worker LiveKit, orchestrateur de l'architecture modulaire.

#### Structure et Imports

```python
# Architecture modulaire avec design patterns
from core.session_manager import SessionManager, SessionCreationError
from core.configuration_builder import ConfigurationBuilder
from core.dependency_container import container
from core.agent_factory import AgentFactory
```

#### Fonctionnalités Clés

1. **Chargement de Configuration**:
   ```python
   load_dotenv()  # Variables d'environnement
   config_manager = ConfigManager()
   agent_config = config_manager.load_agent_config()
   ```

2. **Injection de Dépendances**:
   ```python
   # Configuration du conteneur DI
   container.register_singleton('session_manager', session_manager)
   container.register_singleton('agent_factory', agent_factory)
   ```

3. **Fonction Entrypoint**:
   ```python
   async def entrypoint(ctx: JobContext):
       """Point d'entrée principal appelé par LiveKit."""
       # Récupération des services via DI
       session_manager = container.get_singleton('session_manager')
       agent_factory = container.get_singleton('agent_factory')
       
       # Construction de la configuration
       config_builder = ConfigurationBuilder()
       agent_config_di = config_builder.build_configuration()
   ```

#### Gestion des Erreurs

- **ConfigurationError**: Erreurs de configuration (variables manquantes, format invalide)
- **SessionCreationError**: Échec de création de session
- **AgentCreationError**: Échec de création d'agent

---

### 2. **Serveur FastAPI** (`serveur/main.py`)

**Rôle**: Serveur web pour l'authentification et l'exposition des métriques.

#### Endpoints Principaux

1. **Authentification** (`GET /token`):
   ```python
   @app.get("/token")
   def create_token(room: str, identity: str):
       """Génère un token JWT pour LiveKit."""
       token = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
       token.with_identity(identity).with_name(identity)
       token.with_grants(grants)
   ```

2. **Métriques** (`GET /metrics`):
   ```python
   @app.get("/metrics")
   def get_metrics():
       """Récupère les métriques depuis le fichier partagé."""
       with open(shared_metrics_file, 'r') as f:
           return JSONResponse(content=json.load(f))
   ```

#### Gestion des Fichiers Statiques

```python
app.mount("/", StaticFiles(directory="client", html=True), name="client")
```

---

### 3. **Gestionnaire de Sessions** (`worker/core/session_manager.py`)

**Rôle**: Gestion centralisée des sessions LiveKit avec pattern Singleton.

#### Classes Principales

```python
class SessionManager:
    """Singleton pour gérer les sessions LiveKit."""
    
    def __init__(self):
        self._active_sessions: Dict[str, AgentSession] = {}
        self._provider_manager = DynamicProviderManager()
    
    def create_session(self, ctx: JobContext, config: Dict[str, Any]) -> Tuple[AgentSession, str]:
        """Crée une nouvelle session avec configuration dynamique."""
```

#### Fonctionnalités

1. **Création Dynamique de Sessions**:
   - Utilisation du `DynamicProviderManager`
   - Configuration basée sur les variables d'environnement
   - Fallback vers configurations par défaut

2. **Gestion des Métriques**:
   ```python
   # Initialiser les métriques pour cette session
   metrics_collector = MetricsCollector()
   metrics_collector.start_session_tracking(session_id)
   ```

---

### 4. **Manager de Providers Dynamiques** (`worker/core/dynamic_provider_manager.py`)

**Rôle**: Système NO-CODE pour gérer les providers LLM, STT, TTS.

#### Configuration

```python
class DynamicProviderManager:
    """Gestionnaire dynamique des providers."""
    
    def load_config(self) -> ProviderConfig:
        """Charge la configuration depuis .env et JSON."""
        return ProviderConfig(
            llm=LLMConfig(
                provider_name=os.getenv('LLM_PROVIDER', 'openai'),
                model=os.getenv('LLM_MODEL', 'gpt-4o-mini')
            ),
            # ... autres providers
        )
```

#### Méthodes Clés

1. **Création de Providers**:
   ```python
   def create_llm_provider(self) -> Any:
       """Crée le provider LLM selon la configuration."""
   
   def create_stt_provider(self) -> Any:
       """Crée le provider STT selon la configuration."""
   ```

2. **Gestion des Plugins**:
   ```python
   def load_plugins(self) -> List[Dict[str, Any]]:
       """Charge la configuration des plugins."""
   ```

---

### 5. **Collecteur de Métriques** (`worker/core/metrics.py`)

**Rôle**: Système de collecte et monitoring des performances.

#### Pattern Observer

```python
class MetricsCollector:
    """Collecteur de métriques avec pattern Observer."""
    
    def __init__(self, max_history: int = 1000):
        self._metrics_history: deque = deque(maxlen=max_history)
        self._observers: List[Callable[[MetricData], None]] = []
    
    def record_metric(self, metric: MetricData) -> None:
        """Enregistre une métrique et notifie les observateurs."""
```

#### Types de Métriques

1. **Performance**:
   - Latence STT, LLM, TTS
   - TTFT, TTFB
   - Latence totale

2. **Sessions**:
   - Sessions actives
   - Durée des sessions
   - Succès/échecs

#### Sauvegarde Partagée

```python
def _update_shared_file(self) -> None:
    """Met à jour le fichier partagé pour le serveur."""
    shared_data = {
        'recent_metrics': self.get_recent_metrics(),
        'active_sessions': self.get_active_sessions(),
        'summary': self.get_metrics_summary()
    }
```

---

### 6. **System de Plugins** (`worker/core/plugins/`)

**Rôle**: Architecture extensible pour ajouter des fonctionnalités sans coder.

#### Interface Plugin

```python
class AgentPlugin(ABC):
    """Interface abstraite pour les plugins d'agent."""
    
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Traite un message et retourne une réponse modifiée."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom du plugin."""
```

#### Plugins Implémentés

1. **SentimentAnalysisPlugin**:
   ```python
   async def process_message(self, message: str, context: Dict[str, Any]) -> str:
       sentiment_score = self._analyze_sentiment(message)
       context['sentiment_analysis'] = {
           'score': sentiment_score,
           'emotion': self._get_emotion_label(sentiment_score)
       }
   ```

2. **ProfanityFilterPlugin**:
   ```python
   async def process_message(self, message: str, context: Dict[str, Any]) -> str:
       if self._contains_inappropriate_content(message):
           return self._get_replacement_message()
   ```

3. **ConversationMemoryPlugin**:
   ```python
   async def process_message(self, message: str, context: Dict[str, Any]) -> str:
       self.conversations[session_id].append({
           'timestamp': datetime.now().isoformat(),
           'message': message
       })
   ```

---

### 7. **CLI de Gestion** (`worker/manage_agents.py`)

**Rôle**: Interface ligne de commande pour la configuration NO-CODE.

#### Commandes Principales

1. **Configuration**:
   ```bash
   python manage_agents.py show                    # Afficher la config
   python manage_agents.py list-providers         # Lister les providers
   python manage_agents.py change-llm openai gpt-4o
   ```

2. **Plugins**:
   ```bash
   python manage_agents.py plugins list
   python manage_agents.py plugins add --name sentiment_analysis
   python manage_agents.py plugins remove --name example
   ```

3. **Interactive**:
   ```bash
   python manage_agents.py interactive
   ```

---

## Architecture des Design Patterns

### 1. **Singleton Pattern**

**Utilisation**: `SessionManager`, `DependencyContainer`, `MetricsCollector`

```python
class SessionManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

### 2. **Factory Pattern**

**Utilisation**: Création des providers (LLM, STT, TTS, Plugins)

```python
class LLMProviderFactory:
    _providers: Dict[str, Type[LLMProvider]] = {
        "openai": OpenAILLMProvider,
        "anthropic": AnthropicLLMProvider,
    }
    
    @classmethod
    def create(cls, provider_name: str, **kwargs) -> LLMProvider:
        if provider_name not in cls._providers:
            raise ValueError(f"Provider non supporté: {provider_name}")
        return cls._providers[provider_name](**kwargs)
```

### 3. **Builder Pattern**

**Utilisation**: `ConfigurationBuilder`, `DynamicProviderManager`

```python
class ConfigurationBuilder:
    def build_configuration(self) -> AgentConfiguration:
        """Construit la configuration étape par étape."""
        config = AgentConfiguration()
        config.llm_model = self._validate_llm_model()
        config.stt_model = self._validate_stt_model()
        return config
```

### 4. **Dependency Injection**

**Utilisation**: `DependencyContainer`, résolution des services

```python
class DependencyContainer:
    def register_singleton(self, name: str, instance: Any):
        """Enregistre un service singleton."""
    
    def get_singleton(self, name: str) -> Any:
        """Récupère une instance singleton."""
```

### 5. **Observer Pattern**

**Utilisation**: `MetricsCollector` pour notifier les changements

```python
class MetricsCollector:
    def record_metric(self, metric: MetricData) -> None:
        """Notifie tous les observateurs."""
        for observer in self._observers:
            observer(metric)
```

---

## Flux de Données et Interactions

### 1. **Démarrage du Système**

```
1. load_dotenv() → Chargement variables d'environnement
2. ConfigManager → Chargement configuration agent
3. DependencyContainer → Enregistrement services
4. SessionManager → Initialisation
5. Worker démarré → Attente connexions LiveKit
```

### 2. **Session Utilisateur**

```
1. Client → /token (FastAPI) → Token JWT
2. Client → LiveKit avec token → Connexion room
3. LiveKit → entrypoint() → Création session
4. SessionManager → create_session() → Agent + Session
5. ModularAgent → Traitement messages → Plugins
6. MetricsCollector → Enregistrement métriques
```

### 3. **Processing d'un Message**

```
1. Message audio → STT Provider → Texte
2. Texte → Plugins (sentiment, filter, memory)
3. Texte + Context → LLM Provider → Réponse
4. Réponse → TTS Provider → Audio
5. Métriques → MetricsCollector → shared_metrics.json
6. Serveur → /metrics → Exposition API
```

---

## Gestion des Erreurs

### 1. **Catégories d'Erreurs**

- **ConfigurationError**: Configuration invalide
- **SessionCreationError**: Échec création session
- **AgentCreationError**: Échec création agent
- **DependencyNotFoundError**: Service manquant

### 2. **Stratégies de Récupération**

```python
try:
    provider = create_provider(config)
except ConfigurationError as e:
    logging.warning(f"Fallback vers config par défaut: {e}")
    provider = create_default_provider()
```

### 3. **Logging Structuré**

```python
logging.info(f"Session créée avec succès: {session_id}")
logging.error(f"Erreur création session {session_id}: {e}")
logging.warning(f"Fallback vers méthode alternative")
```

---

## Tests et Validation

### 1. **Structure des Tests**

```
tests/
├── unit/                    # Tests unitaires par composant
├── integration/            # Tests d'intégration complète
└── error_handling/         # Tests de gestion d'erreur
```

### 2. **Types de Tests**

- **Unit Tests**: Composants isolés (factories, builders, plugins)
- **Integration Tests**: Flux complets (entrypoint, session management)
- **Error Handling Tests**: Gestion des cas d'erreur

### 3. **Commandes de Test**

```bash
make test              # Tous les tests
make test-unit         # Tests unitaires
make test-integration  # Tests d'intégration
make test-quick        # Validation syntaxe rapide
```

Cette documentation détaillée couvre tous les aspects techniques du code, des design patterns utilisés aux flux de données en passant par la gestion des erreurs et les tests.
