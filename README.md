# 🎤 VoiceAgent LiveKit v2 - Agent Vocal IA

![LiveKit](https://img.shields.io/badge/LiveKit-v2.0-blue?style=flat-square&logo=livekit)
![OpenAI](https://img.shields.io/badge/OpenAI-Integration-green?style=flat-square&logo=openai)
![FastAPI](https://img.shields.io/badge/FastAPI-Server-red?style=flat-square&logo=fastapi)
![Version](https://img.shields.io/badge/Version-2.0-gold?style=flat-square)

Application d'agent vocal en temps réel utilisant LiveKit, OpenAI pour la reconnaissance vocale, traitement du langage naturel et synthèse vocale. Version 2 avec améliorations et optimisations.

## 🏗️ Architecture

Le projet est composé de 3 parties :

1. **Client** (`client/`) : Interface web HTML/JavaScript
2. **Serveur** (`serveur/`) : API FastAPI pour générer les tokens d'authentification
3. **Worker** (`worker/`) : Agent vocal IA qui traite les conversations

## 📋 Prérequis

- Python 3.9 ou supérieur
- Compte LiveKit (gratuit sur [livekit.cloud](https://livekit.cloud))
- Clé API OpenAI (pour STT, LLM et TTS)
- Git (pour cloner le repository)

## 🚀 Installation rapide

### 1. Cloner le repository

```bash
git clone https://github.com/MamadouBousso/voixagent_livekit_v2.git
cd voixagent_livekit_v2
```

### 2. Configuration LiveKit

Créez un compte gratuit sur [livekit.cloud](https://livekit.cloud) et récupérez :
- L'URL de votre projet (ex: `wss://votre-projet.livekit.cloud`)
- La clé API (API Key)
- Le secret API (API Secret)

### 2. Installation du serveur

```bash
cd serveur

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\\Scripts\\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos vraies valeurs
```

### 3. Installation du worker

```bash
cd worker

# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\\Scripts\\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos vraies valeurs
```

## ▶️ Lancement de l'application

### Terminal 1 : Démarrer le serveur

```bash
cd serveur
source venv/bin/activate  # Activer l'environnement virtuel
uvicorn main:app --reload --port 8000
```

Le serveur sera accessible sur : `http://localhost:8000`

### Terminal 2 : Démarrer le worker

```bash
cd worker
source venv/bin/activate  # Activer l'environnement virtuel
python app.py dev
```

Le worker se connecte à LiveKit et attend les participants.

### Utiliser l'interface web

1. Ouvrez votre navigateur sur : `http://localhost:8000`
2. Entrez un nom de salle (ex: `demo-sn`)
3. Entrez votre identité (ex: `web-client-1`)
4. Cliquez sur "Rejoindre"
5. Autorisez l'accès au microphone
6. Commencez à parler avec l'agent vocal !

## 🔧 Configuration avancée

### Configuration des variables d'environnement

**Serveur** (`serveur/.env` ou variables d'environnement) :
```env
LIVEKIT_URL=wss://votre-projet.livekit.cloud
LIVEKIT_API_KEY=votre_clé_api_livekit
LIVEKIT_API_SECRET=votre_secret_livekit
```

**Worker** (`worker/.env` ou variables d'environnement) :
```env
LIVEKIT_URL=wss://votre-projet.livekit.cloud
LIVEKIT_API_KEY=votre_clé_api_livekit
LIVEKIT_API_SECRET=votre_secret_livekit
OPENAI_API_KEY=votre_clé_api_openai
AGENT_INSTRUCTIONS=You are a friendly, concise assistant.
STT_MODEL=whisper-1
LLM_MODEL=gpt-4o-mini
TTS_MODEL=tts-1
TTS_VOICE_ID=alloy
```

## 🎯 Fonctionnalités

- ✅ Conversation vocale en temps réel avec WebRTC
- ✅ Reconnaissance vocale automatique (OpenAI Whisper)
- ✅ Réponses intelligentes (OpenAI GPT-4o-mini)
- ✅ Synthèse vocale naturelle (OpenAI TTS)
- ✅ Détection d'activité vocale (VAD) avec Silero
- ✅ Mode push-to-talk optionnel
- ✅ Interface web responsive et moderne
- ✅ Configuration flexible via variables d'environnement

## 🐛 Dépannage

Pour une aide détaillée, consultez le fichier [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

### Problèmes courants

**Le serveur ne démarre pas :**
- Vérifiez que le fichier `.env` existe dans `serveur/`
- Vérifiez que toutes les variables d'environnement sont définies

**Le worker ne se connecte pas (erreur 401) :**
- Vérifiez les identifiants LiveKit dans `worker/.env`
- Assurez-vous que l'URL commence par `wss://`
- Vérifiez que vos clés API LiveKit sont correctes

**L'agent ne répond pas :**
- Vérifiez votre clé API OpenAI
- Consultez les logs du worker pour les erreurs
- Assurez-vous que le microphone est autorisé

**Pas de son :**
- Vérifiez l'autorisation du microphone dans le navigateur
- Vérifiez que le lecteur audio n'est pas muet
- Ouvrez la console du navigateur pour voir les erreurs

## 📚 Documentation

- [LiveKit Documentation](https://docs.livekit.io/)
- [LiveKit Agents SDK](https://docs.livekit.io/agents/)
- [OpenAI API](https://platform.openai.com/docs)
- [Configuration détaillée](SETUP.md) - Guide de configuration des clés API
- [Dépannage](TROUBLESHOOTING.md) - Solutions aux problèmes courants

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs via les Issues
- Proposer des améliorations
- Soumettre des Pull Requests

## 📝 Licence

Ce projet est un exemple éducatif de voixagent avec LiveKit.

---

**Version 2.0** - Développé par [MamadouBousso](https://github.com/MamadouBousso)

> 🔄 **Migration depuis v1** : Ce repository est une version améliorée de [voixagent_livekit_v1](https://github.com/MamadouBousso/voixagent_livekit_v1.git)

