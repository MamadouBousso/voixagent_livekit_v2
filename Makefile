# Makefile pour le système d'agent vocal intelligent
# Permet de lancer serveur/worker, modifier les providers, voir les métriques, etc.

# Couleurs pour l'affichage
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
CYAN=\033[0;36m
WHITE=\033[1;37m
NC=\033[0m # No Color

# Variables
SHELL := /bin/bash
WORKER_DIR := worker
SERVER_DIR := serveur
CLIENT_DIR := client

# URLs et ports par défaut
SERVER_PORT := 8080
WORKER_LOG := worker.log
SERVER_LOG := serveur.log

# PID files pour gérer les processus
WORKER_PID := worker.pid
SERVER_PID := serveur.pid

.PHONY: help install setup clean start stop restart status logs test metrics

# =============================================================================
# AIDE ET INFORMATIONS
# =============================================================================

help: ## 📋 Afficher cette aide
	@echo "$(WHITE)🤖 SYSTÈME D'AGENT VOCAL INTELLIGENT$(NC)"
	@echo "$(CYAN)===============================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Commandes principales:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "; printf "$(GREEN)%-20s$(NC) %s\n", "make <commande>", "Description"} /^[a-zA-Z_-]+:.*?## / { printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(CYAN)Exemples:$(NC)"
	@echo "  $(WHITE)make start$(NC)          → Démarrer serveur + worker"
	@echo "  $(WHITE)make change-llm$(NC)     → Changer le LLM vers GPT-4"
	@echo "  $(WHITE)make metrics$(NC)        → Afficher les métriques"
	@echo "  $(WHITE)make plugins$(NC)        → Gérer les plugins"
	@echo ""

info: ## ℹ️  Informations sur le système
	@echo "$(BLUE)📊 INFORMATIONS SYSTÈME$(NC)"
	@echo "==============================================="
	@echo "$(YELLOW)Architecture:$(NC) Agent vocal modulaire avec LiveKit"
	@echo "$(YELLOW)Providers:$(NC) OpenAI, Anthropic, ElevenLabs, Google"
	@echo "$(YELLOW)Plugins:$(NC) Sentiment Analysis, Profanity Filter, Memory"
	@echo "$(YELLOW)Design Patterns:$(NC) Factory, Builder, Singleton, DI"
	@echo ""
	@echo "$(YELLOW)Serveur:$(NC) FastAPI (port $(SERVER_PORT))"
	@echo "$(YELLOW)Worker:$(NC) LiveKit Agent"
	@echo "$(YELLOW)Client:$(NC) Interface Web"

# =============================================================================
# INSTALLATION ET CONFIGURATION
# =============================================================================

install: ## 🔧 Installer les dépendances
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	@cd $(WORKER_DIR) && pip install -r requirements.txt
	@cd $(SERVER_DIR) && pip install -r requirements.txt
	@cd $(WORKER_DIR)/tests && pip install -r requirements.txt
	@echo "$(GREEN)✅ Installation terminée$(NC)"

setup: ## ⚙️  Configuration initiale
	@echo "$(BLUE)⚙️  Configuration initiale...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  Création du fichier .env depuis l'exemple...$(NC)"; \
		cp $(WORKER_DIR)/config_example.env .env; \
		echo "$(RED)🔑 Éditez le fichier .env avec vos clés API !$(NC)"; \
	fi
	@cd $(WORKER_DIR) && python manage_agents.py template agent_config.json
	@echo "$(GREEN)✅ Configuration initiale terminée$(NC)"

check-env: ## 🔍 Vérifier les variables d'environnement
	@echo "$(BLUE)🔍 Vérification de l'environnement...$(NC)"
	@if [ -f .env ]; then \
		echo "$(GREEN)✅ Fichier .env trouvé$(NC)"; \
		$(MAKE) -s show-env; \
	else \
		echo "$(RED)❌ Fichier .env manquant - exécutez 'make setup'$(NC)"; \
	fi

show-env: ## 👁️  Afficher les variables d'environnement (masquées)
	@echo "$(YELLOW)Variables d'environnement:$(NC)"
	@if [ -f .env ]; then \
		sed 's/=.*/=***/' .env | head -10; \
		echo "$(CYAN)... (variables masquées pour sécurité)$(NC)"; \
	fi

# =============================================================================
# DÉMARRAGE/ARRÊT DES SERVICES
# =============================================================================

start: stop check-env ## 🚀 Démarrer serveur et worker
	@echo "$(BLUE)🚀 Démarrage des services...$(NC)"
	@$(MAKE) start-server &
	@sleep 3
	@$(MAKE) start-worker &
	@$(MAKE) wait-ready
	@echo "$(GREEN)✅ Services démarrés$(NC)"
	@$(MAKE) status

start-server: ## 🌐 Démarrer le serveur FastAPI uniquement
	@echo "$(CYAN)🌐 Démarrage du serveur FastAPI...$(NC)"
	@cd $(SERVER_DIR) && nohup python main.py > ../$(SERVER_LOG) 2>&1 & echo $$! > ../$(SERVER_PID)
	@sleep 2
	@if curl -s http://localhost:$(SERVER_PORT)/ > /dev/null; then \
		echo "$(GREEN)✅ Serveur démarré sur http://localhost:$(SERVER_PORT)$(NC)"; \
	else \
		echo "$(RED)❌ Erreur démarrage serveur - voir $(SERVER_LOG)$(NC)"; \
	fi

start-worker: ## 🤖 Démarrer le worker LiveKit uniquement
	@echo "$(CYAN)🤖 Démarrage du worker LiveKit...$(NC)"
	@cd $(WORKER_DIR) && nohup python app.py dev > ../$(WORKER_LOG) 2>&1 & echo $$! > ../$(WORKER_PID)
	@sleep 5
	@if pgrep -f "python.*app.py" > /dev/null; then \
		echo "$(GREEN)✅ Worker démarré$(NC)"; \
	else \
		echo "$(RED)❌ Erreur démarrage worker - voir $(WORKER_LOG)$(NC)"; \
	fi

stop: ## 🛑 Arrêter tous les services
	@echo "$(BLUE)🛑 ARRÊT DES SERVICES$(NC)"
	@echo "==============================================="
	@echo "$(YELLOW)Arrêt du serveur FastAPI...$(NC)"
	@pkill -f "python.*main.py" 2>/dev/null || echo "$(CYAN)Serveur déjà arrêté$(NC)"
	@echo "$(YELLOW)Arrêt du worker LiveKit...$(NC)"
	@pkill -f "python.*app.py" 2>/dev/null || echo "$(CYAN)Worker déjà arrêté$(NC)"
	@echo "$(YELLOW)Nettoyage des fichiers PID...$(NC)"
	@rm -f $(SERVER_PID) $(WORKER_PID) 2>/dev/null || true
	@sleep 3
	@echo "$(GREEN)✅ Tous les services arrêtés$(NC)"
	@echo "$(CYAN)Vérification finale...$(NC)"

stop-server: ## 🌐 Arrêter le serveur FastAPI uniquement
	@echo "$(BLUE)🌐 Arrêt du serveur FastAPI...$(NC)"
	@pkill -f "python.*main.py" 2>/dev/null || echo "$(CYAN)Serveur déjà arrêté$(NC)"
	@rm -f $(SERVER_PID) 2>/dev/null || true
	@echo "$(GREEN)✅ Serveur arrêté$(NC)"

stop-worker: ## 🤖 Arrêter le worker LiveKit uniquement
	@echo "$(BLUE)🤖 Arrêt du worker LiveKit...$(NC)"
	@pkill -f "python.*app.py" 2>/dev/null || echo "$(CYAN)Worker déjà arrêté$(NC)"
	@rm -f $(WORKER_PID) 2>/dev/null || true
	@echo "$(GREEN)✅ Worker arrêté$(NC)"

restart: stop start ## 🔄 Redémarrer tous les services

status: ## 📊 Statut des services
	@echo "$(BLUE)📊 STATUS DES SERVICES$(NC)"
	@echo "==============================================="
	@echo -n "$(YELLOW)Serveur FastAPI:$(NC) "
	@if curl -s http://localhost:$(SERVER_PORT)/ > /dev/null 2>&1; then \
		echo "$(GREEN)🟢 ACTIF$(NC) (port $(SERVER_PORT))"; \
	else \
		echo "$(RED)🔴 INACTIF$(NC)"; \
	fi
	@echo -n "$(YELLOW)Worker LiveKit:$(NC) "
	@if pgrep -f "python.*app.py" > /dev/null; then \
		echo "$(GREEN)🟢 ACTIF$(NC)"; \
	else \
		echo "$(RED)🔴 INACTIF$(NC)"; \
	fi
	@echo ""

wait-ready: ## ⏳ Attendre que les services soient prêts
	@echo "$(CYAN)⏳ Attente du démarrage des services...$(NC)"
	@for i in {1..30}; do \
		if curl -s http://localhost:$(SERVER_PORT)/ > /dev/null 2>&1 && pgrep -f "python.*app.py" > /dev/null; then \
			break; \
		fi; \
		sleep 1; \
	done

# =============================================================================
# CONFIGURATION DES PROVIDERS (NO-CODE)
# =============================================================================

config-show: ## 🔍 Afficher la configuration actuelle
	@echo "$(BLUE)🔍 Configuration actuelle:$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py show

config-list: ## 📋 Lister les providers disponibles
	@echo "$(BLUE)📋 Providers disponibles:$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py list-providers

# Changement de LLM
change-llm-openai: ## 🧠 Changer LLM vers OpenAI GPT-4o
	@echo "$(BLUE)🧠 Changement LLM vers OpenAI GPT-4o...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-llm openai gpt-4o
	@echo "$(GREEN)✅ LLM changé vers OpenAI GPT-4o$(NC)"

change-llm-mini: ## 🧠 Changer LLM vers GPT-4o-mini (rapide/économique)
	@echo "$(BLUE)🧠 Changement LLM vers GPT-4o-mini...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-llm openai gpt-4o-mini

change-llm-anthropic: ## 🧠 Changer LLM vers Anthropic Claude
	@echo "$(BLUE)🧠 Changement LLM vers Anthropic Claude...$(NC)"
	@echo "$(YELLOW)⚠️  Assurez-vous d'avoir ANTHROPIC_API_KEY dans .env$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-llm anthropic claude-3-sonnet

# Changement de STT
change-stt-openai: ## 🎤 Changer STT vers OpenAI Whisper
	@echo "$(BLUE)🎤 Changement STT vers OpenAI Whisper...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-stt openai whisper-1
	@echo "$(GREEN)✅ STT changé vers OpenAI Whisper$(NC)"

change-stt-google: ## 🎤 Changer STT vers Google
	@echo "$(BLUE)🎤 Changement STT vers Google...$(NC)"
	@echo "$(YELLOW)⚠️  Assurez-vous d'avoir GOOGLE_API_KEY dans .env$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-stt google whisper

# Changement de TTS
change-tts-openai: ## 🔊 Changer TTS vers OpenAI
	@echo "$(BLUE)🔊 Changement TTS vers OpenAI...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-tts openai tts-1 --voice alloy
	@echo "$(GREEN)✅ TTS changé vers OpenAI$(NC)"

change-tts-elevenlabs: ## 🔊 Changer TTS vers ElevenLabs
	@echo "$(BLUE)🔊 Changement TTS vers ElevenLabs...$(NC)"
	@echo "$(YELLOW)⚠️  Assurez-vous d'avoir ELEVENLABS_API_KEY dans .env$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py change-tts elevenlabs eleven_turbo_v2 --voice alloy

config-interactive: ## 🎛️  Configuration interactive
	@echo "$(BLUE)🎛️  Configuration interactive...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py interactive

# =============================================================================
# GESTION DES PLUGINS
# =============================================================================

plugins: ## 🔌 Afficher les plugins disponibles et actifs
	@echo "$(BLUE)🔌 PLUGINS$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python manage_agents.py plugins list

plugin-add-sentiment: ## 😊 Ajouter plugin d'analyse des sentiments
	@echo "$(BLUE)😊 Ajout plugin analyse des sentiments...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py plugins add --name sentiment_analysis
	@echo "$(GREEN)✅ Plugin sentiment analysis ajouté$(NC)"

plugin-add-filter: ## 🛡️  Ajouter plugin de filtrage de contenu
	@echo "$(BLUE)🛡️  Ajout plugin filtrage de contenu...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py plugins add --name profanity_filter
	@echo "$(GREEN)✅ Plugin profanity filter ajouté$(NC)"

plugin-add-memory: ## 🧠 Ajouter plugin de mémoire conversationnelle
	@echo "$(BLUE)🧠 Ajout plugin mémoire conversationnelle...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py plugins add --name conversation_memory
	@echo "$(GREEN)✅ Plugin conversation memory ajouté$(NC)"

plugin-remove-example: ## 🗑️  Supprimer le plugin exemple
	@echo "$(BLUE)🗑️  Suppression plugin exemple...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py plugins remove --name example
	@echo "$(GREEN)✅ Plugin exemple supprimé$(NC)"

plugin-demo: ## 🎪 Démonstration des plugins
	@echo "$(BLUE)🎪 Démonstration des plugins...$(NC)"
	@cd $(WORKER_DIR) && python demo_plugins.py

# =============================================================================
# MÉTRIQUES ET MONITORING
# =============================================================================

metrics: ## 📊 Afficher les métriques en temps réel
	@echo "$(BLUE)📊 MÉTRIQUES EN TEMPS RÉEL$(NC)"
	@echo "==============================================="
	@curl -s http://localhost:$(SERVER_PORT)/metrics/simple | python -m json.tool 2>/dev/null || echo "$(RED)❌ Serveur non accessible$(NC)"

metrics-detailed: ## 📈 Métriques détaillées avec historique
	@echo "$(BLUE)📈 MÉTRIQUES DÉTAILLÉES$(NC)"
	@echo "==============================================="
	@curl -s http://localhost:$(SERVER_PORT)/metrics | python -m json.tool 2>/dev/null || echo "$(RED)❌ Serveur non accessible$(NC)"

metrics-sessions: ## 👥 Sessions actives
	@echo "$(BLUE)👥 SESSIONS ACTIVES$(NC)"
	@echo "==============================================="
	@curl -s http://localhost:$(SERVER_PORT)/metrics/sessions | python -m json.tool 2>/dev/null || echo "$(RED)❌ Serveur non accessible$(NC)"

metrics-watch: ## 👀 Surveillance continue des métriques
	@echo "$(BLUE)👀 Surveillance continue des métriques...$(NC)"
	@echo "$(YELLOW)Appuyez sur Ctrl+C pour arrêter$(NC)"
	@while true; do \
		clear; \
		echo "$(BLUE)📊 MÉTRIQUES - $(shell date)$(NC)"; \
		echo "==============================================="; \
		curl -s http://localhost:$(SERVER_PORT)/metrics/simple 2>/dev/null | python -m json.tool || echo "$(RED)Serveur non accessible$(NC)"; \
		sleep 5; \
	done

metrics-test: ## 🧪 Générer des métriques de test
	@echo "$(BLUE)🧪 Génération de métriques de test...$(NC)"
	@curl -s http://localhost:$(SERVER_PORT)/metrics/test
	@echo "$(GREEN)✅ Métriques de test générées$(NC)"

# =============================================================================
# LOGS ET DEBUG
# =============================================================================

logs: ## 📋 Afficher les logs des deux services
	@echo "$(BLUE)📋 LOGS COMBINÉS$(NC)"
	@echo "==============================================="
	@if [ -f $(SERVER_LOG) ]; then echo "$(CYAN)🌐 SERVEUR:$(NC)"; tail -10 $(SERVER_LOG); fi
	@echo ""
	@if [ -f $(WORKER_LOG) ]; then echo "$(CYAN)🤖 WORKER:$(NC)"; tail -10 $(WORKER_LOG); fi

logs-server: ## 🌐 Logs du serveur uniquement
	@echo "$(BLUE)🌐 LOGS SERVEUR$(NC)"
	@echo "==============================================="
	@if [ -f $(SERVER_LOG) ]; then tail -f $(SERVER_LOG); else echo "$(RED)❌ Fichier log serveur non trouvé$(NC)"; fi

logs-worker: ## 🤖 Logs du worker uniquement
	@echo "$(BLUE)🤖 LOGS WORKER$(NC)"
	@echo "==============================================="
	@if [ -f $(WORKER_LOG) ]; then tail -f $(WORKER_LOG); else echo "$(RED)❌ Fichier log worker non trouvé$(NC)"; fi

logs-clear: ## 🗑️  Nettoyer les logs
	@echo "$(BLUE)🗑️  Nettoyage des logs...$(NC)"
	@rm -f $(SERVER_LOG) $(WORKER_LOG) 2>/dev/null || true
	@echo "$(GREEN)✅ Logs nettoyés$(NC)"

debug: ## 🐛 Mode debug complet
	@echo "$(BLUE)🐛 MODE DEBUG$(NC)"
	@echo "==============================================="
	@echo "$(YELLOW)Status des services:$(NC)"
	@$(MAKE) status
	@echo ""
	@echo "$(YELLOW)Configuration actuelle:$(NC)"
	@$(MAKE) config-show
	@echo ""
	@echo "$(YELLOW)Logs récents:$(NC)"
	@$(MAKE) logs

# =============================================================================
# TESTS ET VALIDATION
# =============================================================================

test: ## 🧪 Lancer tous les tests (recommandé)
	@echo "$(BLUE)🧪 EXÉCUTION COMPLÈTE DES TESTS$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python run_tests.py

test-all: test ## 🧪 Alias pour tous les tests

test-unit: ## 🔬 Tests unitaires uniquement
	@echo "$(BLUE)🔬 TESTS UNITAIRES$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/unit/ -v --tb=short

test-integration: ## 🔗 Tests d'intégration uniquement
	@echo "$(BLUE)🔗 TESTS D'INTÉGRATION$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/integration/ -v --tb=short

test-errors: ## 🚨 Tests de gestion d'erreur uniquement
	@echo "$(BLUE)🚨 TESTS DE GESTION D'ERREUR$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/error_handling/ -v --tb=short

test-quick: ## ⚡ Test rapide de syntaxe
	@echo "$(BLUE)⚡ TEST RAPIDE DE SYNTAXE$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m py_compile app.py && echo "$(GREEN)✅ app.py OK$(NC)"
	@cd $(SERVER_DIR) && python -m py_compile main.py && echo "$(GREEN)✅ main.py OK$(NC)"
	@cd $(WORKER_DIR) && python -c "import core" && echo "$(GREEN)✅ Imports core OK$(NC)"
	@echo "$(GREEN)✅ Syntaxe correcte$(NC)"

test-coverage: ## 📊 Tests avec couverture de code
	@echo "$(BLUE)📊 TESTS AVEC COUVERTURE$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest --cov=core --cov-report=html --cov-report=term-missing tests/ -v

test-verbose: ## 🔍 Tests avec output détaillé
	@echo "$(BLUE)🔍 TESTS VERBEUX$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/ -v -s --tb=long

test-plugins: ## 🔌 Tests des plugins uniquement
	@echo "$(BLUE)🔌 TESTS DES PLUGINS$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -c "\
from core.plugins.sentiment_analysis_plugin import SentimentAnalysisPlugin; \
from core.plugins.profanity_filter_plugin import ProfanityFilterPlugin; \
from core.plugins.conversation_memory_plugin import ConversationMemoryPlugin; \
print('✅ Import plugins OK')"
	@echo "$(GREEN)✅ Tests des plugins terminés$(NC)"

test-providers: ## 🏭 Tests des providers uniquement
	@echo "$(BLUE)🏭 TESTS DES PROVIDERS$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -c "\
from core.factories import LLMProviderFactory, STTProviderFactory, TTSProviderFactory; \
print('✅ Import providers OK')"
	@echo "$(GREEN)✅ Tests des providers terminés$(NC)"

test-config: ## ⚙️ Tests de configuration
	@echo "$(BLUE)⚙️ TESTS DE CONFIGURATION$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/unit/test_configuration_builder.py -v

test-ci: ## 🚀 Tests pour CI/CD (sans couverture HTML)
	@echo "$(BLUE)🚀 TESTS CI/CD$(NC)"
	@echo "==============================================="
	@cd $(WORKER_DIR) && python -m pytest tests/ --tb=short -q --disable-warnings

validate-all: test-quick validate-config ## ✅ Validation complète (syntaxe + config)

# =============================================================================
# NETTOYAGE ET MAINTENANCE
# =============================================================================

clean: ## 🧹 Nettoyer les fichiers temporaires
	@echo "$(BLUE)🧹 Nettoyage...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f $(SERVER_PID) $(WORKER_PID) 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

clean-all: clean logs-clear ## 🗑️  Nettoyage complet (logs + cache)
	@echo "$(BLUE)🗑️  Nettoyage complet...$(NC)"
	@rm -rf .pytest_cache/ 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage complet terminé$(NC)"

# =============================================================================
# DÉVELOPPEMENT ET OUTILS
# =============================================================================

dev: start metrics-watch ## 🛠️  Mode développement (démarrage + monitoring)

template-config: ## 📄 Créer un template de configuration
	@echo "$(BLUE)📄 Création du template de configuration...$(NC)"
	@cd $(WORKER_DIR) && python manage_agents.py template agent_config.json.template
	@echo "$(GREEN)✅ Template créé: worker/agent_config.json.template$(NC)"

validate-config: ## ✅ Valider la configuration
	@echo "$(BLUE)✅ Validation de la configuration...$(NC)"
	@cd $(WORKER_DIR) && python -c "from core.dynamic_provider_manager import DynamicProviderManager; DynamicProviderManager(); print('✅ Configuration valide')"

open-client: ## 🌐 Ouvrir le client web
	@echo "$(BLUE)🌐 Ouverture du client web...$(NC)"
	@if command -v open >/dev/null; then \
		open http://localhost:$(SERVER_PORT); \
	elif command -v xdg-open >/dev/null; then \
		xdg-open http://localhost:$(SERVER_PORT); \
	else \
		echo "$(YELLOW)Ouvrez manuellement: http://localhost:$(SERVER_PORT)$(NC)"; \
	fi

# =============================================================================
# COMMANDES COMPOSITES
# =============================================================================

demo: setup start plugin-add-sentiment plugin-add-filter metrics ## 🎪 Démonstration complète
	@echo "$(GREEN)🎉 Démonstration complète terminée !$(NC)"
	@echo "$(CYAN)Services démarrés avec plugins d'analyse$(NC)"

production: check-env start metrics ## 🚀 Démarrage en mode production

quick-start: stop start-server start-worker status ## ⚡ Démarrage rapide
	@echo "$(GREEN)⚡ Démarrage rapide terminé$(NC)"

full-test: clean test-quick test restart validate-config ## 🧪 Test complet du système

test-help: ## 📚 Aide pour les tests disponibles
	@echo "$(BLUE)📚 COMMANDES DE TEST DISPONIBLES$(NC)"
	@echo "==============================================="
	@echo "$(YELLOW)Tests principaux:$(NC)"
	@echo "  $(GREEN)make test$(NC)          → Tests complets (recommandé)"
	@echo "  $(GREEN)make test-quick$(NC)    → Test rapide de syntaxe"
	@echo "  $(GREEN)make test-unit$(NC)     → Tests unitaires uniquement"
	@echo "  $(GREEN)make test-integration$(NC) → Tests d'intégration"
	@echo ""
	@echo "$(YELLOW)Tests spécialisés:$(NC)"
	@echo "  $(GREEN)make test-coverage$(NC) → Tests avec couverture"
	@echo "  $(GREEN)make test-verbose$(NC)  → Tests avec détails"
	@echo "  $(GREEN)make test-plugins$(NC)  → Tests des plugins"
	@echo "  $(GREEN)make test-providers$(NC) → Tests des providers"
	@echo "  $(GREEN)make test-config$(NC)   → Tests de configuration"
	@echo ""
	@echo "$(YELLOW)Tests pour CI/CD:$(NC)"
	@echo "  $(GREEN)make test-ci$(NC)       → Tests rapides pour CI"
	@echo "  $(GREEN)make validate-all$(NC)  → Validation complète"

# Commandes par défaut
.DEFAULT_GOAL := help
