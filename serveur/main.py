# ============================================================
# IMPORTS - Bibliothèques nécessaires
# ============================================================
import os
import sys
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException      # Framework web moderne et rapide
from fastapi.staticfiles import StaticFiles     # Pour servir les fichiers statiques (HTML, JS, CSS)
from fastapi.responses import JSONResponse      # Pour renvoyer des réponses JSON
from dotenv import load_dotenv                  # Pour charger les variables d'environnement depuis .env
from livekit import api as lk_api               # SDK LiveKit pour générer les tokens d'authentification

# Ajouter le chemin vers le worker pour importer les métriques
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'worker'))

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
# ROUTE API - Métriques de Performance
# ============================================================
@app.get("/metrics")
def get_metrics():
    """
    Retourne les métriques de performance de l'agent.
    Note: Cette route fonctionne si le worker est en cours d'exécution.
    """
    try:
        # Lire les métriques depuis le fichier partagé du worker
        worker_path = os.path.join(os.path.dirname(__file__), '..', 'worker')
        shared_metrics_file = os.path.join(worker_path, 'shared_metrics.json')
        
        if os.path.exists(shared_metrics_file):
            with open(shared_metrics_file, 'r', encoding='utf-8') as f:
                shared_data = json.load(f)
            
            return JSONResponse(
                content={
                    "status": "success",
                    "recent_metrics": shared_data.get("recent_metrics", []),
                    "active_sessions": shared_data.get("active_sessions", {}),
                    "summary": shared_data.get("summary", {}),
                    "last_updated": shared_data.get("last_updated"),
                    "timestamp": datetime.now().isoformat()
                },
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        else:
            # Fallback vers l'ancienne méthode
            import sys
            if worker_path not in sys.path:
                sys.path.insert(0, worker_path)
            
            from core.metrics import metrics_collector
            recent_metrics = metrics_collector.get_metrics()
            
            metrics_data = []
            for metric in recent_metrics[-20:]:
                metrics_data.append({
                    "name": metric.name,
                    "value": metric.value,
                    "unit": metric.unit,
                    "timestamp": metric.timestamp.isoformat()
                })
            
            return JSONResponse(
                content={
                    "status": "success",
                    "recent_metrics": metrics_data,
                    "total_metrics_count": len(recent_metrics),
                    "timestamp": datetime.now().isoformat()
                },
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
    except (ImportError, ModuleNotFoundError):
        return JSONResponse(
            content={
                "status": "worker_not_connected", 
                "message": "Worker non connecté ou métriques non disponibles",
                "available_methods": [
                    "1. Voir les logs du worker en temps réel",
                    "2. Utiliser: curl http://localhost:8080/metrics/simple",
                    "3. Accéder aux métriques via les logs du terminal"
                ],
                "timestamp": datetime.now().isoformat()
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Erreur lors de la récupération des métriques: {str(e)}"
        })

@app.get("/metrics/test")
def create_test_metrics():
    """
    Crée des métriques de test pour démontrer le système.
    """
    try:
        # Essayer d'ajouter des métriques de test directement
        worker_path = os.path.join(os.path.dirname(__file__), '..', 'worker')
        shared_metrics_file = os.path.join(worker_path, 'shared_metrics.json')
        
        # Lire le fichier existant
        if os.path.exists(shared_metrics_file):
            with open(shared_metrics_file, 'r', encoding='utf-8') as f:
                shared_data = json.load(f)
        else:
            shared_data = {
                "last_updated": None,
                "recent_metrics": [],
                "active_sessions": {},
                "summary": {"total_metrics_count": 0, "connection_success": 0, "connection_errors": 0}
            }
        
        # Ajouter des métriques de test complètes
        import random
        session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Métriques réalistes
        stt_latency = round(random.uniform(120, 300), 2)
        llm_latency = round(random.uniform(800, 1500), 2)
        tts_latency = round(random.uniform(400, 800), 2)
        ttft = round(random.uniform(600, 1200), 2)
        ttfb = round(stt_latency + llm_latency + random.uniform(200, 400), 2)
        total_latency = round(ttfb + tts_latency, 2)
        
        test_metrics = [
            {
                "name": "connection_success",
                "value": 1.0,
                "unit": "count",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "stt_latency",
                "value": stt_latency,
                "unit": "ms",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "llm_latency", 
                "value": llm_latency,
                "unit": "ms",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "tts_latency",
                "value": tts_latency,
                "unit": "ms", 
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "ttft",
                "value": ttft,
                "unit": "ms",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "ttfb",
                "value": ttfb,
                "unit": "ms",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            },
            {
                "name": "total_latency",
                "value": total_latency,
                "unit": "ms",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "session_id": session_id}
            }
        ]
        
        # Ajouter aussi aux sessions actives
        if session_id not in shared_data["active_sessions"]:
            shared_data["active_sessions"][session_id] = {
                "ttfb": ttfb,
                "ttft": ttft,
                "total_latency": total_latency,
                "stt_latency": stt_latency,
                "llm_latency": llm_latency,
                "tts_latency": tts_latency,
                "audio_duration": None,
                "response_length": None
            }
        
        shared_data["recent_metrics"].extend(test_metrics)
        shared_data["recent_metrics"] = shared_data["recent_metrics"][-50:]  # Garder les 50 dernières
        shared_data["last_updated"] = datetime.now().isoformat()
        shared_data["summary"]["total_metrics_count"] = len(shared_data["recent_metrics"])
        shared_data["summary"]["connection_success"] = len([m for m in shared_data["recent_metrics"] if m["name"] == "connection_success"])
        
        # Sauvegarder
        with open(shared_metrics_file, 'w', encoding='utf-8') as f:
            json.dump(shared_data, f, indent=2, ensure_ascii=False)
        
        return JSONResponse(
            content={
                "status": "success",
                "message": "Métriques de test créées",
                "metrics_added": len(test_metrics),
                "total_metrics": len(shared_data["recent_metrics"])
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/metrics/simple")
def get_simple_metrics():
    """
    Interface simple pour voir les métriques sans dépendances complexes.
    Version robuste qui évite les erreurs JSON.
    """
    try:
        response_data = {
            "status": "available",
            "message": "Pour voir les métriques en temps réel:",
            "methods": {
                "1_logs": "Regardez les logs du worker (terminal) - cherchez 'Métrique [nom]: valeur'",
                "2_test_session": "Lancez une session vocale et observez les métriques dans les logs",
                "3_metrics_types": [
                    "connection_success: Connexion réussie (count)",
                    "stt_latency: Latence STT/Speech-to-Text (ms)", 
                    "llm_latency: Latence LLM/Language Model (ms)",
                    "tts_latency: Latence TTS/Text-to-Speech (ms)",
                    "total_latency: Latence totale (ms)",
                    "ttft: Time To First Token (ms)",
                    "ttfb: Time To First Byte (ms)"
                ]
            },
            "currently_active": "Le worker collecte automatiquement ces métriques pendant les sessions vocales",
            "timestamp": datetime.now().isoformat()
        }
        
        # S'assurer que la réponse est en JSON valide
        return JSONResponse(
            content=response_data,
            status_code=200,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        return JSONResponse(
            content={"error": "Erreur serveur", "message": str(e)},
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/metrics/sessions")
def get_active_sessions():
    """
    Retourne les sessions actives et leurs métriques.
    """
    try:
        # Import depuis le chemin du worker
        import sys
        import os
        worker_path = os.path.join(os.path.dirname(__file__), '..', 'worker')
        if worker_path not in sys.path:
            sys.path.insert(0, worker_path)
        
        from core.metrics import metrics_collector
        
        sessions = metrics_collector.get_active_sessions()
        sessions_data = []
        
        for session_id, session_metrics in sessions.items():
            sessions_data.append({
                "session_id": session_id,
                "ttfb": session_metrics.ttfb if session_metrics.ttfb is not None else 0,
                "ttft": session_metrics.ttft if session_metrics.ttft is not None else 0,
                "total_latency": session_metrics.total_latency if session_metrics.total_latency is not None else 0,
                "stt_latency": session_metrics.stt_latency if session_metrics.stt_latency is not None else 0,
                "llm_latency": session_metrics.llm_latency if session_metrics.llm_latency is not None else 0,
                "tts_latency": session_metrics.tts_latency if session_metrics.tts_latency is not None else 0,
                "audio_duration": session_metrics.audio_duration if session_metrics.audio_duration is not None else 0,
                "response_length": session_metrics.response_length if session_metrics.response_length is not None else 0
            })
        
        return JSONResponse(
            content={
                "status": "success",
                "active_sessions": len(sessions_data),
                "sessions": sessions_data,
                "timestamp": datetime.now().isoformat()
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except (ImportError, ModuleNotFoundError) as e:
        return JSONResponse(
            content={
                "status": "worker_not_connected",
                "message": f"Worker non connecté: {str(e)}",
                "active_sessions": 0,
                "sessions": []
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error", 
                "message": str(e),
                "active_sessions": 0,
                "sessions": []
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

# ============================================================
# MONTAGE DES FICHIERS STATIQUES (APRÈS LES ROUTES API)
# ============================================================
# IMPORTANT : Monter StaticFiles APRÈS avoir défini les routes API
# Sinon, le mount("/", ...) intercepte toutes les requêtes
# Monter le répertoire "client" pour servir les fichiers statiques (index.html, etc.)
# Tous les fichiers du dossier "client" seront accessibles via l'URL racine "/"
# Le dossier client est à la racine du projet, donc on remonte d'un niveau
app.mount("/", StaticFiles(directory="../client", html=True), name="client")
