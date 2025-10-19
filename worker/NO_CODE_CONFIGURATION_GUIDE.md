# Guide de Configuration NO-CODE

## Vue d'ensemble

Ce système permet de **changer facilement de providers** (STT, TTS, LLM) et d'**ajouter des plugins** **sans coder** ! 

## 🚀 Méthodes de Configuration

### 1. **Via Variables d'Environnement** (`.env`)

Modifiez simplement votre fichier `.env` :

```bash
# Changer de LLM
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet

# Changer de STT  
STT_PROVIDER=google
STT_MODEL=whisper

# Changer de TTS
TTS_PROVIDER=elevenlabs  
TTS_MODEL=eleven_turbo_v2
TTS_VOICE_ID=alloy

# Ajouter des plugins
ENABLED_PLUGINS=example,sentiment_analysis,profanity_filter
```

### 2. **Via Fichier JSON** (`agent_config.json`)

Copiez le template et modifiez-le :

```bash
cp agent_config.json.example agent_config.json
```

Puis éditez `agent_config.json` :

```json
{
  "llm": {
    "provider_name": "anthropic",
    "model": "claude-3-sonnet",
    "api_key": "your-anthropic-key"
  },
  "tts": {
    "provider_name": "elevenlabs",
    "model": "eleven_turbo_v2", 
    "voice_id": "alloy",
    "api_key": "your-elevenlabs-key"
  },
  "enabled_plugins": [
    {"plugin_name": "sentiment_analysis", "enabled": true}
  ]
}
```

### 3. **Via CLI** (Recommandé)

Utilisez le script `manage_agents.py` pour tout gérer facilement :

## 🛠️ Commandes CLI

### Afficher la configuration actuelle
```bash
python manage_agents.py show
```

### Lister les providers disponibles
```bash
python manage_agents.py list-providers
```

### Changer de LLM
```bash
python manage_agents.py change-llm openai gpt-4o --temperature 0.8
python manage_agents.py change-llm anthropic claude-3-sonnet --api-key YOUR_KEY
```

### Changer de STT
```bash
python manage_agents.py change-stt openai whisper-1
python manage_agents.py change-stt google whisper --api-key YOUR_KEY
```

### Changer de TTS
```bash
python manage_agents.py change-tts openai tts-1 --voice alloy
python manage_agents.py change-tts elevenlabs eleven_turbo_v2 --voice alloy
```

### Gérer les plugins
```bash
# Lister les plugins
python manage_agents.py plugins list

# Ajouter un plugin
python manage_agents.py plugins add --name sentiment_analysis

# Supprimer un plugin  
python manage_agents.py plugins remove --name example
```

### Configuration interactive
```bash
python manage_agents.py interactive
```

## 📋 Providers Supportés

### **LLM (Large Language Models)**
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-sonnet`, `claude-3-haiku`
- **Cohere**: `command`, `command-light`

### **STT (Speech-to-Text)**
- **OpenAI**: `whisper-1`
- **Google**: `whisper`, `speech-to-text`
- **Azure**: `speech-to-text`

### **TTS (Text-to-Speech)**
- **OpenAI**: `tts-1`, `tts-1-hd` (voix: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`)
- **ElevenLabs**: `eleven_turbo_v2`, `eleven_multilingual_v2`
- **Azure**: `neural-voices`

### **VAD (Voice Activity Detection)**
- **Silero**: `silero-vad`

## 🔌 Plugins Disponibles

Le système supporte l'ajout de plugins sans coder :

```json
{
  "enabled_plugins": [
    {"plugin_name": "example", "enabled": true},
    {"plugin_name": "sentiment_analysis", "enabled": true, "config": {"threshold": 0.7}},
    {"plugin_name": "profanity_filter", "enabled": true},
    {"plugin_name": "conversation_memory", "enabled": false}
  ]
}
```

## 🎯 Exemples Pratiques

### **Exemple 1 : Changer vers ElevenLabs**

```bash
# 1. Changer le TTS
python manage_agents.py change-tts elevenlabs eleven_turbo_v2 --voice alloy

# 2. Vérifier la config
python manage_agents.py show
```

### **Exemple 2 : Utiliser Anthropic Claude**

```bash
# 1. Changer le LLM
python manage_agents.py change-llm anthropic claude-3-sonnet --api-key YOUR_KEY

# 2. Vérifier
python manage_agents.py show
```

### **Exemple 3 : Configuration complète via JSON**

Créez `agent_config.json` :

```json
{
  "llm": {
    "provider_name": "anthropic",
    "model": "claude-3-sonnet",
    "api_key": "sk-ant-...",
    "temperature": 0.7
  },
  "stt": {
    "provider_name": "openai", 
    "model": "whisper-1",
    "api_key": "sk-..."
  },
  "tts": {
    "provider_name": "elevenlabs",
    "model": "eleven_turbo_v2",
    "voice_id": "alloy", 
    "api_key": "sk_..."
  },
  "enabled_plugins": [
    {"plugin_name": "sentiment_analysis", "enabled": true},
    {"plugin_name": "profanity_filter", "enabled": true}
  ],
  "instructions": "Vous êtes un assistant vocal avancé avec analyse des sentiments."
}
```

## 🔄 Redémarrage

Après modification de la configuration, redémarrez le worker :

```bash
pkill -f "python.*app.py"
cd worker && python app.py dev
```

## 🧪 Test de la Configuration

```bash
# Vérifier que la config est correcte
python manage_agents.py show

# Tester les imports
python -c "from core.dynamic_provider_manager import DynamicProviderManager; print('✅ OK')"
```

## ⚡ Avantages

1. **NO-CODE** : Aucune modification de code requise
2. **TEMPS RÉEL** : Changements appliqués au redémarrage
3. **FLEXIBLE** : Support multi-providers
4. **PLUGINS** : Extensions faciles à ajouter
5. **CLI** : Interface en ligne de commande intuitive
6. **JSON** : Configuration déclarative
7. **ENV** : Variables d'environnement classiques

## 🚨 Dépannage

### Erreur "Provider non supporté"
```bash
python manage_agents.py list-providers
```
Vérifiez que le provider est bien listé.

### Erreur API Key
Assurez-vous que vos clés API sont correctement définies dans le JSON ou .env.

### Plugin non trouvé
```bash  
python manage_agents.py plugins list
```

Le système est maintenant **100% configurable sans coder** ! 🎉
