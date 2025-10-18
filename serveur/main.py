# ============================================================
# IMPORTS - Bibliothèques nécessaires
# ============================================================
import os
from fastapi import FastAPI, HTTPException      # Framework web moderne et rapide
from fastapi.staticfiles import StaticFiles     # Pour servir les fichiers statiques (HTML, JS, CSS)
from fastapi.responses import JSONResponse      # Pour renvoyer des réponses JSON
from dotenv import load_dotenv                  # Pour charger les variables d'environnement depuis .env
from livekit import api as lk_api               # SDK LiveKit pour générer les tokens d'authentification

# ============================================================
# CHARGEMENT DE LA CONFIGURATION
# ============================================================
# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les identifiants LiveKit depuis les variables d'environnement
LIVEKIT_URL = os.getenv("LIVEKIT_URL")              # URL du serveur LiveKit (ex: wss://votre-serveur.livekit.cloud)
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")     # Clé API fournie par LiveKit
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")  # Secret API pour signer les tokens

# ============================================================
# INITIALISATION DE L'APPLICATION FASTAPI
# ============================================================
app = FastAPI()

# ============================================================
# ROUTE API - Génération de tokens d'authentification LiveKit
# ============================================================
# Cette route est appelée par le client web pour obtenir un token
# permettant de se connecter à une salle LiveKit de manière sécurisée
@app.get("/token")
def create_token(room: str, identity: str):
    """
    Génère un token JWT pour authentifier un utilisateur sur LiveKit.
    
    Paramètres:
        room (str): Nom de la salle à rejoindre
        identity (str): Identité/nom de l'utilisateur
    
    Retourne:
        JSON avec le token d'authentification et l'URL du serveur LiveKit
    """
    # Vérifier que toutes les variables d'environnement LiveKit sont configurées
    if not (LIVEKIT_URL and LIVEKIT_API_KEY and LIVEKIT_API_SECRET):
        raise HTTPException(500, "LIVEKIT env non définies")

    # ============================================================
    # CRÉATION DU TOKEN D'ACCÈS
    # ============================================================
    # Créer un objet AccessToken avec les identifiants API
    at = lk_api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    
    # Configurer le token avec les permissions et l'identité
    at = at.with_identity(identity).with_grants(lk_api.VideoGrants(
        room=room,              # Nom de la salle spécifique
        room_join=True,         # Permission de rejoindre la salle
        room_create=False,      # Pas de permission de créer des salles
        can_publish=True,       # Permission de publier audio/vidéo
        can_subscribe=True      # Permission de recevoir les flux des autres
    ))
    
    # Générer le token JWT (JSON Web Token) signé
    token = at.to_jwt()
    
    # Retourner le token et l'URL du serveur au client
    return JSONResponse({"token": token, "url": LIVEKIT_URL})

# ============================================================
# MONTAGE DES FICHIERS STATIQUES (APRÈS LES ROUTES API)
# ============================================================
# IMPORTANT : Monter StaticFiles APRÈS avoir défini les routes API
# Sinon, le mount("/", ...) intercepte toutes les requêtes
# Monter le répertoire "client" pour servir les fichiers statiques (index.html, etc.)
# Tous les fichiers du dossier "client" seront accessibles via l'URL racine "/"
# Le dossier client est à la racine du projet, donc on remonte d'un niveau
app.mount("/", StaticFiles(directory="../client", html=True), name="client")
