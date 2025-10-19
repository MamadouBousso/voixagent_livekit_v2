# 🛠️ Guide des Commandes Makefile

Ce guide répertorie toutes les commandes disponibles dans le Makefile pour gérer le système d'agent vocal.

## 📋 Navigation et Aide

```bash
make help                    # 📋 Afficher l'aide complète avec toutes les commandes
make info                    # ℹ️  Informations sur l'architecture du système
```

## 🔧 Installation et Configuration

### Initialisation
```bash
make install                 # 🔧 Installer les dépendances (serveur + worker)
make setup                   # ⚙️  Configuration initiale (.env, templates)
```

### Vérification
```bash
make check-env              # 🔍 Vérifier les variables d'environnement
make show-env               # 👁️  Afficher les variables (masquées pour sécurité)
make validate-config        # ✅ Valider la configuration actuelle
```

## 🚀 Gestion des Services

### Démarrage/Arrêt
```bash
make start                  # 🚀 Démarrer serveur + worker (recommandé)
make start-server           # 🌐 Démarrer uniquement le serveur FastAPI
make start-worker           # 🤖 Démarrer uniquement le worker LiveKit
make stop                   # 🛑 Arrêter tous les services
make stop-server            # 🌐 Arrêter uniquement le serveur FastAPI
make stop-worker            # 🤖 Arrêter uniquement le worker LiveKit
make restart                # 🔄 Redémarrer tous les services
make quick-start            # ⚡ Démarrage rapide (sans vérifications)
```

### Monitoring des Services
```bash
make status                 # 📊 Afficher le statut des services
make wait-ready             # ⏳ Attendre que les services soient prêts
```

## ⚙️ Configuration NO-CODE des Providers

### Affichage et Liste
```bash
make config-show            # 🔍 Afficher la configuration actuelle
make config-list            # 📋 Lister tous les providers disponibles
make config-interactive     # 🎛️  Configuration interactive guidée
```

### Changement de LLM (Large Language Model)
```bash
make change-llm-openai      # 🧠 Changer vers OpenAI GPT-4o (le plus avancé)
make change-llm-mini        # 🧠 Changer vers GPT-4o-mini (rapide/économique)
make change-llm-anthropic   # 🧠 Changer vers Anthropic Claude-3-sonnet
```

### Changement de STT (Speech-to-Text)
```bash
make change-stt-openai      # 🎤 Changer vers OpenAI Whisper
make change-stt-google      # 🎤 Changer vers Google Speech
```

### Changement de TTS (Text-to-Speech)
```bash
make change-tts-openai      # 🔊 Changer vers OpenAI TTS
make change-tts-elevenlabs  # 🔊 Changer vers ElevenLabs (qualité vocale)
```

## 🔌 Gestion des Plugins

### Affichage et Information
```bash
make plugins                # 🔌 Afficher plugins disponibles et actifs
make plugin-demo            # 🎪 Démonstration des effets des plugins
```

### Ajout de Plugins
```bash
make plugin-add-sentiment   # 😊 Ajouter analyse des sentiments utilisateur
make plugin-add-filter      # 🛡️  Ajouter filtrage contenu inapproprié
make plugin-add-memory      # 🧠 Ajouter mémoire conversationnelle
```

### Suppression de Plugins
```bash
make plugin-remove-example  # 🗑️  Supprimer le plugin exemple
```

## 📊 Métriques et Monitoring

### Consultation des Métriques
```bash
make metrics                # 📊 Métriques simples en temps réel
make metrics-detailed       # 📈 Métriques détaillées avec historique
make metrics-sessions       # 👥 Sessions actives et statistiques
```

### Surveillance Active
```bash
make metrics-watch          # 👀 Surveillance continue des métriques
make metrics-test           # 🧪 Générer des métriques de test
```

## 📋 Logs et Debug

### Consultation des Logs
```bash
make logs                   # 📋 Logs combinés (serveur + worker)
make logs-server            # 🌐 Logs du serveur FastAPI uniquement
make logs-worker            # 🤖 Logs du worker LiveKit uniquement
```

### Debug et Diagnostic
```bash
make debug                  # 🐛 Mode debug complet (status + config + logs)
make logs-clear             # 🗑️  Nettoyer les fichiers de logs
```

## 🧪 Tests et Validation

### Tests Principaux
```bash
make test                   # 🧪 Lancer tous les tests (recommandé)
make test-all               # 🧪 Alias pour tous les tests
make test-quick             # ⚡ Test rapide de syntaxe
make test-unit              # 🔬 Tests unitaires uniquement
make test-integration       # 🔗 Tests d'intégration uniquement
make test-errors            # 🚨 Tests de gestion d'erreur uniquement
```

### Tests Spécialisés
```bash
make test-coverage          # 📊 Tests avec couverture de code
make test-verbose           # 🔍 Tests avec output détaillé
make test-plugins           # 🔌 Tests des plugins uniquement
make test-providers         # 🏭 Tests des providers uniquement
make test-config            # ⚙️ Tests de configuration
```

### Tests pour CI/CD
```bash
make test-ci                # 🚀 Tests rapides pour CI/CD
make validate-all           # ✅ Validation complète (syntaxe + config)
make full-test              # 🧪 Test complet du système (clean + tests + validation)
make test-help              # 📚 Aide pour les tests disponibles
```

## 🧹 Maintenance et Nettoyage

### Nettoyage
```bash
make clean                  # 🧹 Nettoyer fichiers temporaires et cache Python
make clean-all              # 🗑️  Nettoyage complet (logs + cache + cache tests)
```

### Configuration et Templates
```bash
make template-config        # 📄 Créer un template de configuration
```

## 🛠️ Développement et Outils

### Mode Développement
```bash
make dev                    # 🛠️  Mode développement (start + metrics-watch)
```

### Accès Client
```bash
make open-client            # 🌐 Ouvrir le client web dans le navigateur
```

## 🎯 Commandes Composites (Scénarios)

### Démonstration Complète
```bash
make demo                   # 🎪 Démo complète (setup + start + plugins + metrics)
```

### Mode Production
```bash
make production             # 🚀 Démarrage en mode production (check + start + metrics)
```

## 🔥 Flux de Travail Recommandés

### Premier Démarrage
```bash
make install                # Installer les dépendances
make setup                  # Configuration initiale
make check-env              # Vérifier la configuration
make start                  # Démarrer les services
make status                 # Vérifier que tout fonctionne
```

### Changement de Provider
```bash
make config-show            # Voir la config actuelle
make change-llm-openai      # Changer le LLM
make restart                # Redémarrer pour appliquer
make config-show            # Vérifier le changement
```

### Ajout de Plugin
```bash
make plugins                # Voir les plugins disponibles
make plugin-add-sentiment   # Ajouter un plugin
make restart                # Redémarrer pour activer
make plugin-demo            # Tester les effets
```

### Surveillance en Production
```bash
make start                  # Démarrer les services
make metrics-watch          # Surveillance continue
```

### Debug d'un Problème
```bash
make status                 # État des services
make debug                  # Informations complètes
make logs                   # Logs récents
```

## ⚠️ Notes Importantes

1. **Variables d'Environnement**: Assurez-vous d'avoir un fichier `.env` correct avant de démarrer
2. **Redémarrage**: Après changement de configuration, utilisez `make restart`
3. **Logs**: Les logs sont gardés dans `serveur.log` et `worker.log`
4. **PID Files**: Les processus sont gérés via des fichiers PID pour un arrêt propre

## 🎨 Exemples d'Usage Courants

### Configuration d'un Agent de Support
```bash
make plugin-add-sentiment   # Détection clients mécontents
make plugin-add-filter      # Filtrage contenu
make plugin-add-memory      # Mémoire conversations
make change-llm-openai      # LLM performant
```

### Configuration d'un Agent Éducatif
```bash
make plugin-add-memory      # Suivi des progrès
make change-llm-mini        # LLM économique
make restart
```

### Monitoring en Production
```bash
make production
make metrics-watch
```

Ce Makefile offre une interface complète et intuitive pour gérer tous les aspects du système d'agent vocal sans avoir besoin de comprendre la configuration complexe sous-jacente ! 🚀
