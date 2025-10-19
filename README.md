# 🤖 Système d'Agent Vocal Intelligent

Un système d'agent vocal modulaire basé sur LiveKit WebRTC avec architecture industrielle, plugins extensibles et configuration NO-CODE.

## 🚀 Démarrage Rapide

### ⚡ **5 Minutes** - Guide Express
Voir **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** pour un démarrage ultra-rapide.

### 🏗️ **Construction Complète** - Tutoriel Détaillé  
Voir **[STEP_BY_STEP_TUTORIAL.md](STEP_BY_STEP_TUTORIAL.md)** pour construire l'application depuis zéro.

### **Démarrage Standard**
```bash
# Installer et configurer
make install
make setup

# Démarrer le système complet
make start

# Voir les métriques
make metrics
```

## 📋 Commandes Principales

### 🎛️ Gestion des Services
```bash
make start              # Démarrer serveur + worker
make stop               # Arrêter tous les services
make stop-server        # Arrêter uniquement le serveur
make stop-worker        # Arrêter uniquement le worker
make restart            # Redémarrer les services
make status             # Statut des services
```

### ⚙️ Configuration NO-CODE
```bash
make config-show                     # Voir la configuration
make change-llm-openai              # Changer vers GPT-4o
make change-tts-elevenlabs          # Changer vers ElevenLabs
make config-interactive             # Configuration interactive
```

### 🔌 Gestion des Plugins
```bash
make plugins                        # Lister les plugins
make plugin-add-sentiment           # Ajouter analyse sentiments
make plugin-add-filter              # Ajouter filtre contenu
make plugin-demo                    # Démonstration plugins
```

### 📊 Monitoring
```bash
make metrics                        # Métriques temps réel
make metrics-detailed               # Métriques détaillées
make logs                           # Logs des services
make debug                          # Mode debug complet
```

## 🏗️ Architecture

### Design Patterns
- **Factory**: Création des providers (LLM, STT, TTS)
- **Singleton**: Gestionnaire de sessions
- **Builder**: Construction de configuration
- **Dependency Injection**: Résolution des services
- **Observer**: Collecte des métriques

### Composants
```
serveur/          # FastAPI (tokens, métriques)
worker/           # Agent LiveKit modulaire  
client/           # Interface web
├── core/         # Architecture modulaire
├── plugins/      # Extensions (sentiment, filtrage, mémoire)
└── tests/        # Suite de tests complète
```

## 🔧 Providers Supportés

### LLM (Large Language Model)
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Anthropic**: Claude-3-sonnet

### STT (Speech-to-Text)  
- **OpenAI**: Whisper-1
- **Google**: Google Speech

### TTS (Text-to-Speech)
- **OpenAI**: TTS-1, TTS-1-HD (voix: alloy, nova, echo)
- **ElevenLabs**: Eleven_turbo_v2

### VAD (Voice Activity Detection)
- **Silero**: Silero VAD

## 🔌 Plugins Disponibles

### Analyse des Sentiments
```bash
make plugin-add-sentiment
```
- Détection automatique de l'émotion utilisateur
- Adaptation du ton de réponse
- Escalade pour clients mécontents

### Filtrage de Contenu
```bash
make plugin-add-filter
```
- Protection contre contenu inapproprié
- Détection et blocage du spam
- Messages de remplacement polis

### Mémoire Conversationnelle
```bash
make plugin-add-memory
```
- Mémorisation du contexte des conversations
- Persistance des sessions
- Recommandations contextuelles

## 📊 Métriques et Monitoring

### Types de Métriques
- **Performance**: Latence STT/LLM/TTS, TTFT, TTFB
- **Sessions**: Sessions actives, durée, succès/échecs
- **Plugins**: Métriques par plugin

### Visualisation
```bash
make metrics          # Métriques simples
make metrics-watch    # Surveillance continue
make metrics-sessions # Sessions actives
```

## 🧪 Tests et Validation

### Tests Principaux
```bash
make test           # Tous les tests (recommandé)
make test-quick     # Test rapide de syntaxe
make test-unit      # Tests unitaires uniquement
make test-help      # Aide pour tous les tests disponibles
```

### Tests Spécialisés
```bash
make test-coverage  # Tests avec couverture de code
make test-plugins   # Tests des plugins uniquement
make test-providers # Tests des providers uniquement
make test-ci        # Tests rapides pour CI/CD
make full-test      # Test système complet
```

## 🔐 Configuration

### Variables d'Environnement
Créer un fichier `.env` basé sur `worker/config_example.env`:

```bash
# LiveKit
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-secret

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your-openai-key

# STT/TTS
STT_PROVIDER=openai
STT_MODEL=whisper-1
TTS_PROVIDER=openai
TTS_MODEL=tts-1-hd
TTS_VOICE_ID=nova
```

### Configuration via CLI
```bash
make config-interactive    # Configuration guidée
make config-show          # Vérifier la configuration
```

## 📚 Documentation

### **🚀 Guides de Démarrage**
- **[Guide Express (5 min)](QUICK_START_GUIDE.md)**: Démarrage ultra-rapide
- **[Tutoriel Complet](STEP_BY_STEP_TUTORIAL.md)**: Construction depuis zéro

### **📖 Documentation Technique**
- **[Documentation du Code](CODE_DOCUMENTATION.md)**: Vue d'ensemble architecturale
- **[Documentation Détaillée](CODE_DETAILED_DOCUMENTATION.md)**: Détails techniques complets
- **[Guide des Plugins](worker/PLUGINS_GUIDE.md)**: Utilisation et création de plugins
- **[Configuration NO-CODE](worker/NO_CODE_CONFIGURATION_GUIDE.md)**: Guide de configuration sans coder

## 🎯 Cas d'Usage

### Support Client
```bash
make plugin-add-sentiment
make plugin-add-filter  
make plugin-add-memory
```
→ Agent qui détecte les clients mécontents et escalade automatiquement

### Agent Éducatif
```bash
make plugin-add-memory
make change-llm-anthropic
```
→ Agent qui mémorise les progrès et adapte les leçons

### Agent Multilingue
```bash
# Configuration avec plugins de traduction
make config-interactive
```
→ Agent avec détection automatique de langue

## 🛠️ Développement

### Mode Développement
```bash
make dev          # Démarrage + monitoring continu
make logs         # Logs en temps réel
make debug        # Mode debug complet
```

### Ajout de Nouveaux Plugins
1. Implémenter l'interface `AgentPlugin`
2. Enregistrer dans `PluginFactory`
3. Configuration via CLI

### Ajout de Nouveaux Providers
1. Implémenter l'interface appropriée (LLM/STT/TTS)
2. Enregistrer dans la factory correspondante
3. Configuration dans `DynamicProviderManager`

## 📞 Support et Maintenance

### Commandes Utiles
```bash
make help          # Aide complète
make debug         # Diagnostic système
make clean         # Nettoyage fichiers temporaires
make validate-config # Validation configuration
```

### Logs et Debug
```bash
make logs          # Logs combinés
make logs-server   # Logs serveur uniquement
make logs-worker   # Logs worker uniquement
```

## 🎉 Exemples d'Usage

### Démarrage Complet
```bash
make demo          # Démarrage avec plugins d'exemple
```

### Changement de Provider
```bash
make change-llm-openai     # Changer vers OpenAI
make change-tts-elevenlabs # Changer vers ElevenLabs
```

### Monitoring en Production
```bash
make production    # Démarrage production
make metrics-watch # Surveillance continue
```

---

## 🏆 Fonctionnalités Clés

✅ **Architecture Modulaire** - Design patterns industriels  
✅ **Configuration NO-CODE** - Changement de providers via CLI  
✅ **Plugins Extensibles** - Ajout de fonctionnalités sans coder  
✅ **Monitoring Complet** - Métriques temps réel et historique  
✅ **Tests Complets** - Suite de tests unitaires et d'intégration  
✅ **Documentation Exhaustive** - Guide complet pour développeurs  

**Prêt pour la production avec une approche NO-CODE !** 🚀