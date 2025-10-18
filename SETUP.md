# 🔧 Configuration de l'Agent Vocal LiveKit

## ❌ Problème identifié

L'agent ne répond pas car les **variables d'environnement** ne sont pas configurées.
**Erreur 401** : Le worker ne peut pas s'authentifier avec LiveKit.

## ✅ Solution : Configuration des clés API

### 1. **Clés LiveKit** (obligatoires)
Vous devez obtenir vos clés depuis votre compte LiveKit :

```bash
# Dans votre terminal, définissez ces variables :
export LIVEKIT_URL="wss://testaivoice-nosioku8.livekit.cloud"
export LIVEKIT_API_KEY="votre_vraie_clé_api_livekit"
export LIVEKIT_API_SECRET="votre_vrai_secret_livekit"
```

### 2. **Clé OpenAI** (obligatoire pour STT/LLM/TTS)
```bash
export OPENAI_API_KEY="votre_vraie_clé_api_openai"
```

### 3. **⚠️ IMPORTANT : Remplacez les valeurs par vos vraies clés**
Les valeurs actuelles sont des placeholders :
- `your_livekit_api_key_here` → votre vraie clé API LiveKit
- `your_livekit_api_secret_here` → votre vrai secret LiveKit  
- `your_openai_api_key_here` → votre vraie clé API OpenAI

### 3. **Créer un fichier .env** (recommandé)
Créez un fichier `.env` dans le dossier `worker/` :

```env
# Configuration LiveKit
LIVEKIT_URL=wss://testaivoice-nosioku8.livekit.cloud
LIVEKIT_API_KEY=votre_clé_api_livekit
LIVEKIT_API_SECRET=votre_secret_livekit

# Configuration OpenAI
OPENAI_API_KEY=votre_clé_api_openai

# Configuration de l'agent (optionnel)
AGENT_INSTRUCTIONS=You are a friendly, concise assistant. Keep answers short and helpful.
STT_MODEL=whisper-1
LLM_MODEL=gpt-4o-mini
TTS_MODEL=tts-1
TTS_VOICE_ID=alloy
```

## 🚀 Redémarrage après configuration

1. **Arrêtez le worker** : `Ctrl+C` dans le terminal du worker
2. **Redémarrez le worker** :
   ```bash
   cd worker
   python app.py dev
   ```
3. **Testez l'application** : Rejoignez la room et parlez à l'agent

## 🔍 Vérification

Pour vérifier que les variables sont bien définies :
```bash
echo $LIVEKIT_URL
echo $OPENAI_API_KEY
```

## 📝 Notes importantes

- **Sans ces clés**, l'agent ne peut pas :
  - Se connecter à LiveKit (LIVEKIT_API_KEY/SECRET)
  - Transcrire votre voix (OPENAI_API_KEY)
  - Générer des réponses (OPENAI_API_KEY)
  - Synthétiser la voix (OPENAI_API_KEY)

- **Le fichier .env** est ignoré par Git pour la sécurité
- **Gardez vos clés secrètes** et ne les partagez jamais
