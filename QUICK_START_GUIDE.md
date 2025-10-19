# 🚀 Guide de Démarrage Rapide - Agent Vocal Intelligent

Un guide concis pour démarrer rapidement votre agent vocal modulaire.

## ⚡ Démarrage en 5 Minutes

### 1. **Prérequis**
```bash
# Python 3.8+ requis
python --version

# Services nécessaires:
# - Compte LiveKit Cloud
# - Clé API OpenAI
```

### 2. **Installation Express**
```bash
# Cloner/cloner la structure
git clone <votre-repo> voice-agent
cd voice-agent

# Installation automatique
make install

# Configuration
make setup
```

### 3. **Configuration API**
Éditer le fichier `.env` créé automatiquement :
```bash
nano .env
```

Remplir les clés essentielles :
```env
# LiveKit (obligatoire)
LIVEKIT_URL=wss://your-server.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-secret

# OpenAI (obligatoire)
OPENAI_API_KEY=your-openai-key

# Configuration par défaut
LLM_MODEL=gpt-4o-mini
STT_MODEL=whisper-1
TTS_MODEL=tts-1
TTS_VOICE_ID=alloy
```

### 4. **Démarrage**
```bash
# Démarrer tout le système
make start

# Vérifier que ça marche
make status
```

### 5. **Test**
- Ouvrir http://localhost:8080
- Se connecter avec une room (ex: "test")
- Parler dans le microphone
- Voir la réponse de l'agent !

## 🎛️ Commandes Essentielles

### **Gestion des Services**
```bash
make start          # Démarrer
make stop           # Arrêter
make restart        # Redémarrer
make status         # Statut
```

### **Configuration NO-CODE**
```bash
make config-show    # Voir la config
make change-llm openai gpt-4o     # Changer LLM
make plugins        # Voir les plugins
```

### **Monitoring**
```bash
make metrics        # Voir les métriques
make logs           # Voir les logs
```

## 🔧 Personnalisation Rapide

### **Changer de Modèle LLM**
```bash
# GPT-4o (plus puissant)
make change-llm-openai

# GPT-4o-mini (plus rapide)
make change-llm-mini
```

### **Ajouter des Plugins**
```bash
# Plugin d'analyse des sentiments
make plugin-add-sentiment

# Plugin de filtrage
make plugin-add-filter

# Voir les effets
make plugin-demo
```

### **Configuration Interactive**
```bash
make config-interactive
```

## 🐛 Dépannage

### **Problèmes Courants**

**"Services non accessibles"**
```bash
make status         # Vérifier les services
make logs           # Voir les erreurs
```

**"Configuration invalide"**
```bash
make check-env      # Vérifier .env
make validate-config # Valider la config
```

**"Tests échouent"**
```bash
make test-quick     # Test rapide
make test           # Tests complets
```

## 📊 Vérification du Système

### **Test Complet**
```bash
make full-test      # Test complet système
```

### **Vérification Manuelle**
1. **Serveur** : http://localhost:8080 → Page web s'affiche
2. **Métriques** : `make metrics` → JSON retourné
3. **Agent** : Connecter via client web → Réponse vocale

## 🎯 Exemples d'Usage

### **Agent de Support Client**
```bash
make plugin-add-sentiment
make plugin-add-filter
make change-llm-openai
```

### **Agent Rapide et Économique**
```bash
make change-llm-mini
make plugin-add-memory
```

### **Agent Multilingue** (à venir)
```bash
# Plugins de traduction automatique
make config-interactive
```

## 📚 Documentation Complète

- **Tutoriel complet** : `STEP_BY_STEP_TUTORIAL.md`
- **Architecture** : `CODE_DOCUMENTATION.md`
- **Commandes** : `MAKEFILE_COMMANDS.md`
- **Plugins** : `worker/PLUGINS_GUIDE.md`

## 🆘 Support

### **Aide Intégrée**
```bash
make help           # Aide complète
make test-help      # Aide tests
```

### **Commandes de Debug**
```bash
make debug          # Mode debug complet
make logs           # Logs en temps réel
```

---

## 🎉 Félicitations !

Votre agent vocal intelligent est maintenant opérationnel ! 

**Prochaines étapes** :
1. Tester avec différents modèles LLM
2. Ajouter des plugins personnalisés
3. Configurer votre propre prompt système
4. Déployer en production

**Besoin d'aide ?** Consultez `make help` et la documentation complète ! 🚀
