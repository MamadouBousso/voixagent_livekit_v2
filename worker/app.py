# ============================================================
# IMPORTS - Bibliothèques pour l'agent vocal LiveKit
# ============================================================
import os, logging
from dotenv import load_dotenv                              # Chargement des variables d'environnement
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, AutoSubscribe, cli
# - Agent: classe principale pour créer un agent conversationnel
# - AgentSession: session qui gère le pipeline complet (VAD, STT, LLM, TTS)
# - JobContext: contexte d'exécution fourni par LiveKit
# - WorkerOptions: configuration du worker
# - AutoSubscribe: options d'abonnement automatique aux flux
# - cli: utilitaire en ligne de commande pour démarrer le worker

from livekit.plugins import openai, silero
# - openai: plugin pour utiliser Whisper (STT), GPT (LLM) et TTS
# - silero: plugin pour la détection d'activité vocale (VAD)
# Note: On utilise OpenAI TTS au lieu d'ElevenLabs pour éviter les problèmes de connexion

# ============================================================
# CHARGEMENT DE LA CONFIGURATION
# ============================================================
# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Instructions système pour l'agent IA (personnalité et comportement)
INSTR = os.getenv("AGENT_INSTRUCTIONS", "You are a friendly, concise assistant. Keep answers short.")

# Configuration des modèles d'IA
STT = os.getenv("STT_MODEL", "whisper-1")                # Speech-to-Text: modèle Whisper d'OpenAI
LLM = os.getenv("LLM_MODEL", "gpt-4o-mini")              # Large Language Model: GPT-4o-mini pour la compréhension
TTS_MODEL = os.getenv("TTS_MODEL", "tts-1")              # Text-to-Speech: modèle OpenAI TTS (plus stable)
TTS_VOICE = os.getenv("TTS_VOICE_ID", "alloy")           # Voix OpenAI (alloy, echo, fable, onyx, nova, shimmer)

# ============================================================
# INITIALISATION DU VAD (Voice Activity Detection)
# ============================================================
# Charger le modèle Silero VAD pour détecter quand l'utilisateur parle
# VAD = Voice Activity Detection (détection d'activité vocale)
# Permet de savoir quand commencer/arrêter la transcription
VAD = silero.VAD.load()  # Modèle léger et à faible latence

# ============================================================
# FONCTION PRINCIPALE - Point d'entrée de l'agent
# ============================================================
# Cette fonction est appelée chaque fois qu'un participant rejoint une salle
async def entrypoint(ctx: JobContext):
    """
    Point d'entrée principal du worker agent vocal.
    
    Cette fonction est invoquée automatiquement par LiveKit quand :
    - Un nouveau participant rejoint une salle configurée
    - Le worker est assigné à gérer cette interaction
    
    Paramètres:
        ctx (JobContext): Contexte fourni par LiveKit contenant les infos de la room
    """
    
    # ============================================================
    # ÉTAPE 1 : CONNEXION À LA SALLE LIVEKIT
    # ============================================================
    # Se connecter à la salle où le client vient d'arriver
    # AutoSubscribe.AUDIO_ONLY = s'abonner uniquement aux flux audio (pas de vidéo)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # ============================================================
    # ÉTAPE 2 : CRÉATION DE L'AGENT
    # ============================================================
    # Créer l'instance de l'agent avec ses instructions système
    # Ces instructions définissent la personnalité et le comportement de l'IA
    agent = Agent(instructions=INSTR)

    # ============================================================
    # ÉTAPE 3 : CONFIGURATION DE LA SESSION (PIPELINE COMPLET)
    # ============================================================
    # AgentSession orchestre tout le pipeline de conversation :
    # Audio utilisateur → VAD → STT → LLM → TTS → Audio agent
    session = AgentSession(
        vad=VAD,                                        # Détection d'activité vocale (quand l'utilisateur parle)
        stt=openai.STT(model=STT),                     # Speech-to-Text: convertir la parole en texte (Whisper)
        llm=openai.LLM(model=LLM),                     # Large Language Model: comprendre et générer des réponses (GPT)
        tts=openai.TTS(model=TTS_MODEL, voice=TTS_VOICE),  # Text-to-Speech: OpenAI TTS (plus stable qu'ElevenLabs)
        # Options avancées (selon la version du SDK) :
        # enable_barge_in=True,   # Permet à l'utilisateur d'interrompre l'agent
        # min_endpointing_delay=0.5,  # Délai avant de considérer que l'utilisateur a fini de parler
    )

    # ============================================================
    # ÉTAPE 4 : DÉMARRAGE DE LA SESSION
    # ============================================================
    # Démarrer la session interactive dans la room
    # À partir de ce moment, l'agent écoute et répond automatiquement
    await session.start(agent=agent, room=ctx.room)

# ============================================================
# DÉMARRAGE DU WORKER
# ============================================================
# Point d'entrée du script quand il est exécuté directement
if __name__ == "__main__":
    # Configurer le système de logs pour afficher les informations
    logging.basicConfig(level=logging.INFO)
    
    # Démarrer le worker LiveKit avec la fonction d'entrée configurée
    # Le CLI LiveKit gère :
    # - La connexion au serveur LiveKit
    # - L'écoute des nouvelles salles/participants
    # - L'invocation de la fonction entrypoint pour chaque job
    # - La gestion du cycle de vie du worker
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
