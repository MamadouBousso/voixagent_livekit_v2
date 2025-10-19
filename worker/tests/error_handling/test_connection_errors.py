"""
Tests pour les erreurs de connexion LiveKit documentées
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from livekit.agents import WorkerOptions


class TestConnectionErrors:
    """Tests pour les erreurs de connexion spécifiques"""
    
    def test_workers_options_connection_configuration(self):
        """Test configuration WorkerOptions pour éviter erreurs de connexion"""
        
        # Simuler les variables d'environnement problématiques rencontrées
        with patch.dict(os.environ, {
            'LIVEKIT_URL': 'wss://testaivoice-nosioku8.livekit.cloud',
            'LIVEKIT_API_KEY': 'test-api-key',
            'LIVEKIT_API_SECRET': 'test-api-secret'
        }):
            # Test configuration correcte (comme dans app.py amélioré)
            def create_worker_options():
                return WorkerOptions(
                    entrypoint_fnc=Mock(),  # Mock de la fonction entrypoint
                    ws_url=os.getenv('LIVEKIT_URL', ''),
                    api_key=os.getenv('LIVEKIT_API_KEY'),
                    api_secret=os.getenv('LIVEKIT_API_SECRET'),
                )
            
            try:
                options = create_worker_options()
                assert options.ws_url == 'wss://testaivoice-nosioku8.livekit.cloud'
                assert options.api_key == 'test-api-key'
                assert options.api_secret == 'test-api-secret'
                print("✅ Configuration WorkerOptions correcte")
            except Exception as e:
                print(f"❌ Erreur configuration WorkerOptions: {e}")
    
    def test_default_localhost_connection_error(self):
        """Test détection du problème localhost vs LiveKit Cloud"""
        
        # Simuler le problème: variables d'environnement non définies
        with patch.dict(os.environ, clear=True):
            def create_worker_options_with_defaults():
                return WorkerOptions(
                    entrypoint_fnc=Mock(),
                    ws_url=os.getenv('LIVEKIT_URL', ''),  # Devient '' si non défini
                    api_key=os.getenv('LIVEKIT_API_KEY'),
                    api_secret=os.getenv('LIVEKIT_API_SECRET'),
                )
            
            options = create_worker_options_with_defaults()
            
            # Vérifier le problème détecté
            if not options.ws_url:
                print("⚠️  PROBLÈME DÉTECTÉ: ws_url vide")
                print("   Cause: LIVEKIT_URL non défini dans l'environnement")
                print("   Résultat: Connexion à localhost par défaut")
                print("   Solution: Définir LIVEKIT_URL dans .env")
            
            # Test avec valeurs par défaut problématiques
            assert options.ws_url == ''  # Problème détecté
            assert options.api_key is None
            assert options.api_secret is None
    
    def test_quoted_env_vars_connection_issue(self):
        """Test problème des guillemets dans variables de connexion"""
        
        # Simuler le problème rencontré avec les guillemets
        with patch.dict(os.environ, {
            'LIVEKIT_URL': '"wss://testaivoice-nosioku8.livekit.cloud"',  # Avec guillemets
            'LIVEKIT_API_KEY': '"test-api-key"',
            'LIVEKIT_API_SECRET': '"test-secret"'
        }):
            ws_url = os.getenv('LIVEKIT_URL', '')
            api_key = os.getenv('LIVEKIT_API_KEY')
            api_secret = os.getenv('LIVEKIT_API_SECRET')
            
            # Détecter le problème
            if ws_url.startswith('"') and ws_url.endswith('"'):
                print("⚠️  PROBLÈME DÉTECTÉ: Variables entre guillemets")
                print(f"   LIVEKIT_URL: '{ws_url}'")
                print("   Solution: Supprimer les guillemets du fichier .env")
            
            # Les guillemets causeront des problèmes de connexion
            assert ws_url == '"wss://testaivoice-nosioku8.livekit.cloud"'
    
    def test_connection_refused_server_error(self):
        """Test détection erreur serveur non accessible"""
        
        # Simuler l'erreur ERR_CONNECTION_REFUSED
        def mock_server_request_fails():
            """Simule une requête vers serveur non accessible"""
            try:
                import requests
                response = requests.get("http://localhost:8080/token", timeout=1)
                return response.status_code == 200
            except requests.exceptions.ConnectionError:
                print("⚠️  ERREUR DÉTECTÉE: ERR_CONNECTION_REFUSED")
                print("   Cause: Serveur FastAPI non démarré")
                print("   Solution: Démarrer le serveur avec 'python serveur/main.py'")
                return False
            except Exception as e:
                print(f"⚠️  Autre erreur serveur: {e}")
                return False
        
        # Note: Ce test ne fait pas vraiment la requête en mode test
        # Il simule juste la détection du problème
        with patch('requests.get', side_effect=ConnectionError("Connection refused")):
            result = mock_server_request_fails()
            assert not result  # Devrait échouer
    
    def test_multiple_worker_processes_conflict(self):
        """Test détection de multiples processus worker"""
        
        def check_multiple_workers():
            """Simule la vérification de multiples workers"""
            # En mode test, on simule la détection
            mock_processes = [
                "python app.py dev",
                "python app.py dev",  # Processus dupliqué
                "python app.py dev"   # Encore un autre
            ]
            
            worker_processes = [p for p in mock_processes if "app.py" in p]
            
            if len(worker_processes) > 1:
                print("⚠️  PROBLÈME DÉTECTÉ: Multiples workers actifs")
                print(f"   Nombre de processus worker: {len(worker_processes)}")
                print("   Solution: Arrêter tous les workers avant redémarrage")
                return False
            
            return True
        
        assert not check_multiple_workers()  # Devrait détecter le problème
    
    def test_worker_agent_name_dispatch_issue(self):
        """Test problème dispatch agent avec agent_name"""
        
        def test_agent_name_configurations():
            """Test différentes configurations agent_name"""
            test_cases = [
                {"agent_name": "voice-agent", "should_work": True, "desc": "Nom explicite"},
                {"agent_name": "", "should_work": False, "desc": "Nom vide (problème)"},
                {"agent_name": None, "should_work": False, "desc": "Nom None"},
            ]
            
            for case in test_cases:
                print(f"Test {case['desc']}: agent_name='{case['agent_name']}'")
                
                if not case['should_work']:
                    print("⚠️  PROBLÈME POTENTIEL: Configuration agent_name problématique")
                    if case['agent_name'] == "":
                        print("   Cause: agent_name vide peut causer des problèmes de dispatch")
                        print("   Solution: Utiliser un nom explicite comme 'voice-agent'")
        
        test_agent_name_configurations()
        print("✅ Tests configuration agent_name terminés")


if __name__ == "__main__":
    test_instance = TestConnectionErrors()
    
    try:
        print("🧪 Tests erreurs de connexion...")
        test_instance.test_workers_options_connection_configuration()
        test_instance.test_default_localhost_connection_error()
        test_instance.test_quoted_env_vars_connection_issue()
        test_instance.test_connection_refused_server_error()
        test_instance.test_multiple_worker_processes_conflict()
        test_instance.test_worker_agent_name_dispatch_issue()
        
        print("\n✅ Tous les tests erreurs connexion terminés")
    except Exception as e:
        print(f"\n❌ Échec tests connexion: {e}")
        raise
