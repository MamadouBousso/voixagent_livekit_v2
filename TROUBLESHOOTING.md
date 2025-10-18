# 🔧 Guide de Dépannage - VoiceAgent LiveKit

Ce document répertorie toutes les erreurs courantes rencontrées lors de l'installation et du lancement de l'application VoiceAgent LiveKit, ainsi que leurs solutions.

## 📋 Table des matières

1. [Erreurs d'installation des dépendances](#erreurs-dinstallation-des-dépendances)
2. [Erreurs de configuration](#erreurs-de-configuration)
3. [Erreurs de serveur](#erreurs-de-serveur)
4. [Erreurs de worker](#erreurs-de-worker)
5. [Erreurs de client web](#erreurs-de-client-web)
6. [Erreurs de connexion](#erreurs-de-connexion)

---

## 🚨 Erreurs d'installation des dépendances

### ❌ Erreur : `ERROR: Could not find a version that satisfies the requirement livekit-server-sdk`

**Message d'erreur complet :**
```
ERROR: Could not find a version that satisfies the requirement livekit-server-sdk (from versions: none)
ERROR: No matching distribution found for livekit-server-sdk
```

**🔍 Cause :** Le nom du package dans `requirements.txt` est incorrect.

**✅ Solution :**
1. Ouvrir le fichier `serveur/requirements.txt`
2. Remplacer `livekit-server-sdk` par `livekit`
3. Relancer l'installation :
   ```bash
   cd serveur
   pip install -r requirements.txt
   ```

**📝 Explication :** Le package officiel s'appelle `livekit`, pas `livekit-server-sdk`.

---

### ❌ Erreur : `ImportError: cannot import name 'rtc' from 'livekit'`

**Message d'erreur complet :**
```
ImportError: cannot import name 'rtc' from 'livekit' (unknown location)
```

**🔍 Cause :** Le package `livekit` de base n'est pas installé, seul `livekit-agents` l'est.

**✅ Solution :**
```bash
cd worker
pip install livekit
```

**📝 Explication :** Le worker a besoin du package `livekit` de base en plus de `livekit-agents`.

---

## ⚙️ Erreurs de configuration

### ❌ Erreur : `RuntimeError: Directory 'client' does not exist`

**Message d'erreur complet :**
```
RuntimeError: Directory 'client' does not exist
```

**🔍 Cause :** Le serveur cherche le dossier `client` dans le répertoire `serveur/`, mais il est à la racine du projet.

**✅ Solution :**
1. Ouvrir `serveur/main.py`
2. Modifier la ligne :
   ```python
   # AVANT (incorrect)
   app.mount("/", StaticFiles(directory="client", html=True), name="client")
   
   # APRÈS (correct)
   app.mount("/", StaticFiles(directory="../client", html=True), name="client")
   ```

**📝 Explication :** Le chemin relatif doit remonter d'un niveau (`../`) pour accéder au dossier `client` depuis `serveur/`.

---

### ❌ Erreur : `LIVEKIT env non définies`

**Message d'erreur complet :**
```
HTTPException(500, "LIVEKIT env non définies")
```

**🔍 Cause :** Les variables d'environnement LiveKit ne sont pas définies ou le fichier `.env` n'est pas au bon endroit.

**✅ Solution :**
1. Vérifier que le fichier `.env` existe dans `serveur/` et `worker/`
2. Si le fichier `.env` est à la racine, le copier :
   ```bash
   cp .env serveur/.env
   cp .env worker/.env
   ```
3. Vérifier le contenu du fichier `.env` :
   ```bash
   # Variables requises
   LIVEKIT_URL=wss://votre-projet.livekit.cloud
   LIVEKIT_API_KEY=votre_api_key
   LIVEKIT_API_SECRET=votre_api_secret
   ```

---

## 🖥️ Erreurs de serveur

### ❌ Erreur : `AttributeError: 'AccessToken' object has no attribute 'add_grant'`

**Message d'erreur complet :**
```
AttributeError: 'AccessToken' object has no attribute 'add_grant'
```

**🔍 Cause :** L'API LiveKit a changé. La méthode `add_grant()` n'existe plus dans les versions récentes.

**✅ Solution :**
1. Ouvrir `serveur/main.py`
2. Remplacer l'ancien code :
   ```python
   # AVANT (ancienne API)
   at = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
   at.add_grant(lk_api.VideoGrants(...))
   at.identity = identity
   ```
   
   Par le nouveau code :
   ```python
   # APRÈS (nouvelle API)
   at = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
   at = at.with_identity(identity).with_grants(lk_api.VideoGrants(...))
   ```

**📝 Explication :** LiveKit a migré vers une API plus fluide avec `with_grants()` et `with_identity()`.

---

### ❌ Erreur : `{"detail":"Not Found"}` sur `/token`

**Message d'erreur complet :**
```
curl http://localhost:8000/token?room=test&identity=test
{"detail":"Not Found"}
```

**🔍 Cause :** L'ordre des routes dans FastAPI est incorrect. Le montage des fichiers statiques intercepte les routes API.

**✅ Solution :**
1. Ouvrir `serveur/main.py`
2. Déplacer la définition des routes API **AVANT** le montage des fichiers statiques :
   ```python
   # CORRECT : Routes API d'abord
   @app.get("/token")
   def create_token(room: str, identity: str):
       # ... code de la route
   
   # PUIS montage des fichiers statiques
   app.mount("/", StaticFiles(directory="../client", html=True), name="client")
   ```

**📝 Explication :** FastAPI traite les routes dans l'ordre de définition. Le `mount("/", ...)` intercepte toutes les requêtes s'il est défini en premier.

---

## 🤖 Erreurs de worker

### ❌ Erreur : `ModuleNotFoundError: No module named 'livekit.agents'`

**Message d'erreur complet :**
```
ModuleNotFoundError: No module named 'livekit.agents'
```

**🔍 Cause :** Le package `livekit-agents` n'est pas installé.

**✅ Solution :**
```bash
cd worker
pip install livekit-agents
```

**📝 Explication :** Le worker nécessite le package `livekit-agents` pour fonctionner.

---

### ❌ Erreur : Worker ne se connecte pas à LiveKit

**Message d'erreur complet :**
```
Connection failed to LiveKit server
```

**🔍 Cause :** Problème de configuration ou de réseau.

**✅ Solution :**
1. Vérifier les variables d'environnement dans `worker/.env`
2. Vérifier que l'URL LiveKit commence par `wss://`
3. Vérifier que les clés API sont correctes
4. Tester la connexion :
   ```bash
   cd worker
   python -c "
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print('URL:', os.getenv('LIVEKIT_URL'))
   print('API Key:', 'SET' if os.getenv('LIVEKIT_API_KEY') else 'NOT SET')
   "
   ```

---

## 🌐 Erreurs de client web

### ❌ Erreur : "Rien ne se passe" quand on clique sur "Rejoindre"

**🔍 Cause :** Plusieurs causes possibles :
1. L'endpoint `/token` ne fonctionne pas
2. Les variables d'environnement ne sont pas configurées
3. L'ordre des routes est incorrect

**✅ Solution :**
1. **Tester l'endpoint manuellement :**
   ```bash
   curl "http://localhost:8000/token?room=demo-sn&identity=web-client-1"
   ```
   
2. **Vérifier la console du navigateur :**
   - Ouvrir les outils de développement (F12)
   - Aller dans l'onglet "Console"
   - Chercher les erreurs JavaScript

3. **Vérifier les logs du serveur :**
   - Regarder le terminal où uvicorn est lancé
   - Chercher les erreurs 500 ou autres

---

### ❌ Erreur : `Failed to fetch` dans la console du navigateur

**Message d'erreur complet :**
```
Failed to fetch /token?room=demo-sn&identity=web-client-1
```

**🔍 Cause :** Le serveur n'est pas accessible ou l'endpoint n'existe pas.

**✅ Solution :**
1. Vérifier que le serveur fonctionne :
   ```bash
   curl http://localhost:8000/
   ```
   
2. Vérifier que l'endpoint `/token` existe :
   ```bash
   curl http://localhost:8000/token?room=test&identity=test
   ```

---

### ❌ Erreur : `The requested module does not provide an export named 'CreateLocalTracksOptions'`

**Message d'erreur complet :**
```
Uncaught SyntaxError: The requested module 'https://cdn.jsdelivr.net/npm/livekit-client/+esm' does not provide an export named 'CreateLocalTracksOptions'
```

**🔍 Cause :** L'export `CreateLocalTracksOptions` n'existe plus dans les versions récentes du SDK LiveKit Client.

**✅ Solution :**
1. Ouvrir le fichier `client/index.html`
2. Modifier l'import :
   ```javascript
   // AVANT (incorrect)
   import { connect, Room, RoomEvent, CreateLocalTracksOptions, Track } from 'https://cdn.jsdelivr.net/npm/livekit-client/+esm';
   
   // APRÈS (correct)
   import { connect, Room, RoomEvent, Track } from 'https://cdn.jsdelivr.net/npm/livekit-client/+esm';
   ```

**📝 Explication :** `CreateLocalTracksOptions` n'est plus nécessaire dans les versions récentes. Les options de configuration audio sont passées directement comme objet.

---

### ❌ Erreur : `The requested module does not provide an export named 'connect'`

**Message d'erreur complet :**
```
Uncaught SyntaxError: The requested module 'https://cdn.jsdelivr.net/npm/livekit-client/+esm' does not provide an export named 'connect'
```

**🔍 Cause :** L'export `connect` n'existe plus dans les versions récentes du SDK LiveKit Client.

**✅ Solution :**
1. Ouvrir le fichier `client/index.html`
2. Modifier l'import :
   ```javascript
   // AVANT (incorrect)
   import { connect, Room, RoomEvent, Track } from 'https://cdn.jsdelivr.net/npm/livekit-client/+esm';
   
   // APRÈS (correct)
   import { Room, RoomEvent, Track } from 'https://cdn.jsdelivr.net/npm/livekit-client/+esm';
   ```

**📝 Explication :** La fonction `connect` n'est plus exportée. La connexion se fait maintenant directement via `room.connect(url, token)`.

---

### ❌ Erreur : `Room.createLocalTracks is not a function`

**Message d'erreur complet :**
```
Erreur join: Room.createLocalTracks is not a function
```

**🔍 Cause :** L'API `Room.createLocalTracks()` n'existe plus dans les versions récentes du SDK LiveKit Client.

**✅ Solution :**
1. Ouvrir le fichier `client/index.html`
2. Remplacer l'ancien code :
   ```javascript
   // AVANT (ancienne API)
   const localTracks = await Room.createLocalTracks(audioOpts);
   const micTrack = localTracks.find(t => t.kind === Track.Kind.Audio);
   await room.localParticipant.publishTrack(micTrack, { name: 'micro' });
   ```
   
   Par le nouveau code :
   ```javascript
   // APRÈS (nouvelle API)
   await room.localParticipant.setMicrophoneEnabled(true, audioOpts);
   ```

3. Pour le mode push-to-talk, remplacer :
   ```javascript
   // AVANT
   micTrack.muted = true/false;
   
   // APRÈS
   await room.localParticipant.setMicrophoneEnabled(false/true);
   ```

**📝 Explication :** LiveKit a simplifié l'API en utilisant `setMicrophoneEnabled()` au lieu de gérer manuellement les tracks.

---

### ❌ Erreur : `Cannot read properties of undefined (reading 'size')`

**Message d'erreur complet :**
```
Erreur join: Cannot read properties of undefined (reading 'size')
```

**🔍 Cause :** L'objet `room.participants` peut être `undefined` si la connexion n'est pas encore complètement établie.

**✅ Solution :**
1. Ouvrir le fichier `client/index.html`
2. Remplacer le code qui accède à `room.participants.size` :
   ```javascript
   // AVANT (peut causer une erreur)
   log(`Micro activé (Opus). Participants: ${room.participants.size + 1}`);
   
   // APRÈS (sécurisé)
   const participantCount = room.participants ? room.participants.size + 1 : 1;
   log(`Micro activé (Opus). Participants: ${participantCount}`);
   ```

**📝 Explication :** Il faut toujours vérifier que `room.participants` existe avant d'accéder à ses propriétés, car la connexion peut ne pas être complètement établie.

---

### ❌ Erreur : `publishing rejected as engine not connected within timeout`

**Message d'erreur complet :**
```
Erreur join: publishing rejected as engine not connected within timeout
```

**🔍 Cause :** Le worker n'est pas correctement connecté ou la connexion n'est pas stable au moment de publier le microphone.

**✅ Solution :**
1. **Améliorer la configuration de la Room** dans `client/index.html` :
   ```javascript
   room = new Room({
     adaptiveStream: false,
     dynacast: false,
     publishDefaults: { 
       dtx: true,
       stopMicOnMute: false
     },
     audioCaptureDefaults: { 
       autoGainControl: false
     },
     reconnectPolicy: {
       nextRetryDelayInMs: (context) => Math.min(context.retryCount * 1000, 5000)
     }
   });
   ```

2. **Ajouter un délai avant la publication** :
   ```javascript
   await room.connect(url, token);
   // Attendre que la connexion soit stable
   await new Promise(resolve => setTimeout(resolve, 1000));
   await room.localParticipant.setMicrophoneEnabled(true, audioOpts);
   ```

3. **Ajouter une gestion d'erreur avec retry** :
   ```javascript
   try {
     await room.localParticipant.setMicrophoneEnabled(true, audioOpts);
   } catch (micError) {
     // Réessayer après un délai
     await new Promise(resolve => setTimeout(resolve, 2000));
     await room.localParticipant.setMicrophoneEnabled(true, audioOpts);
   }
   ```

**📝 Explication :** Cette erreur indique un problème de synchronisation entre le client et le worker. Les délais et la gestion d'erreur permettent d'attendre que la connexion soit stable.

---

### ❌ Erreur : `"[object Object]" is not valid JSON` dans content.js

**Message d'erreur complet :**
```
Uncaught (in promise) SyntaxError: "[object Object]" is not valid JSON
    at JSON.parse (<anonymous>)
    at l._storageChangeDispatcher (content.js:2:898238)
```

**🔍 Cause :** Cette erreur provient d'une extension de navigateur qui interfère avec le localStorage/sessionStorage, pas de votre code.

**✅ Solution :**
1. **Mode incognito (recommandé)** :
   - Ouvrir une fenêtre de navigation privée
   - Naviguer vers `http://localhost:8000`
   - Tester l'application

2. **Désactiver les extensions temporairement** :
   - Chrome : `chrome://extensions/` → Désactiver toutes
   - Firefox : `about:addons` → Désactiver les extensions
   - Edge : `edge://extensions/` → Désactiver les extensions

3. **Nettoyer le storage** (dans la console F12) :
   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload();
   ```

**📝 Explication :** L'erreur `content.js` indique qu'elle vient d'une extension de navigateur, pas de votre application. Le mode incognito permet de tester sans extensions.

---

## 🔗 Erreurs de connexion

### ❌ Erreur : `WebSocket connection failed`

**Message d'erreur complet :**
```
WebSocket connection failed: wss://...
```

**🔍 Cause :** Problème de connexion au serveur LiveKit.

**✅ Solution :**
1. Vérifier l'URL LiveKit dans le fichier `.env`
2. Vérifier que l'URL commence par `wss://`
3. Tester la connectivité :
   ```bash
   ping votre-serveur.livekit.cloud
   ```

---

### ❌ Erreur : `Token expired` ou `Invalid token`

**Message d'erreur complet :**
```
Token expired
Invalid token
```

**🔍 Cause :** Le token JWT généré est invalide ou expiré.

**✅ Solution :**
1. Vérifier que les clés API LiveKit sont correctes
2. Vérifier que l'horloge système est synchronisée
3. Regénérer un nouveau token en actualisant la page

---

## 🛠️ Solutions générales

### Vérification complète de l'installation

```bash
# 1. Vérifier la structure des fichiers
ls -la
ls -la serveur/
ls -la worker/
ls -la client/

# 2. Vérifier les fichiers .env
ls -la serveur/.env worker/.env

# 3. Tester les dépendances
cd serveur && python -c "import fastapi, uvicorn, dotenv, livekit; print('✅ Serveur OK')"
cd worker && python -c "import livekit.agents; print('✅ Worker OK')"

# 4. Tester les endpoints
curl http://localhost:8000/
curl http://localhost:8000/token?room=test&identity=test
```

### Commandes de diagnostic

```bash
# Vérifier les processus en cours
ps aux | grep uvicorn
ps aux | grep python

# Vérifier les ports utilisés
lsof -i :8000

# Vérifier les logs en temps réel
tail -f /var/log/syslog  # Sur Linux
# ou regarder directement les terminaux
```

---

## 📞 Support

Si vous rencontrez d'autres erreurs non listées ici :

1. **Vérifiez les logs** dans les terminaux du serveur et du worker
2. **Consultez la console du navigateur** (F12 → Console)
3. **Vérifiez la documentation LiveKit** : https://docs.livekit.io/
4. **Vérifiez les versions des packages** :
   ```bash
   pip list | grep livekit
   ```

---

## 📝 Notes importantes

- **Toujours utiliser des environnements virtuels** pour éviter les conflits de dépendances
- **Vérifier les versions** des packages dans `requirements.txt`
- **Garder les fichiers `.env` à jour** avec les bonnes clés API
- **Tester chaque composant individuellement** avant de lancer l'application complète

---

*Dernière mise à jour : Octobre 2024*
