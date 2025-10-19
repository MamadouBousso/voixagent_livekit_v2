"""
Tests unitaires pour SessionManager
Teste les erreurs de session documentées
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.session_manager import SessionManager, SessionCreationError, SessionStartError

# Mock des imports LiveKit pour les tests
try:
    from livekit.agents import JobContext, AgentSession
    from livekit import Room
except ImportError:
    # En cas d'import échoué, créer des mocks
    JobContext = type('JobContext', (), {})
    AgentSession = type('AgentSession', (), {})
    Room = type('Room', (), {})


class TestSessionManager:
    """Tests pour la classe SessionManager"""
    
    def setup_method(self):
        """Setup pour chaque test"""
        # Reset singleton instance
        SessionManager._instance = None
        SessionManager._initialized = False
        self.session_manager = SessionManager()
    
    def test_singleton_pattern(self):
        """Test pattern Singleton"""
        manager1 = SessionManager()
        manager2 = SessionManager()
        
        assert manager1 is manager2
        print("✅ Pattern Singleton fonctionne")
    
    def test_create_session_success(self):
        """Test création de session réussie"""
        # Mock objects
        mock_ctx = Mock(spec=JobContext)
        mock_room = Mock(spec=Room)
        mock_room.name = "test-room"
        mock_ctx.room = mock_room
        
        config = {
            'instructions': 'Test instructions',
            'stt_model': 'whisper-1',
            'llm_model': 'gpt-4o-mini',
            'tts_model': 'tts-1',
            'tts_voice': 'alloy'
        }
        
        with patch('core.session_manager.AgentSession') as mock_session_class:
            with patch('core.session_manager.silero.VAD.load') as mock_vad:
                with patch('core.session_manager.openai.STT') as mock_stt:
                    with patch('core.session_manager.openai.LLM') as mock_llm:
                        with patch('core.session_manager.openai.TTS') as mock_tts:
                            # Setup mocks
                            mock_vad.return_value = Mock()
                            mock_stt.return_value = Mock()
                            mock_llm.return_value = Mock()
                            mock_tts.return_value = Mock()
                            mock_session_class.return_value = Mock(spec=AgentSession)
                            
                            session, session_id = self.session_manager.create_session(mock_ctx, config)
                            
                            assert session is not None
                            assert session_id.startswith("test-room_")
                            assert len(session_id) > len("test-room_") + 10  # Date format
                            print("✅ Création de session réussie")
    
    def test_create_session_with_custom_id(self):
        """Test création avec session_id personnalisé"""
        mock_ctx = Mock(spec=JobContext)
        mock_room = Mock(spec=Room)
        mock_room.name = "test-room"
        mock_ctx.room = mock_room
        
        config = {'instructions': 'Test'}
        custom_session_id = "custom-session-123"
        
        with patch('core.session_manager.AgentSession'):
            with patch('core.session_manager.silero.VAD.load'):
                with patch('core.session_manager.openai.STT'):
                    with patch('core.session_manager.openai.LLM'):
                        with patch('core.session_manager.openai.TTS'):
                            session, actual_id = self.session_manager.create_session(
                                mock_ctx, config, custom_session_id
                            )
                            
                            assert actual_id == custom_session_id
                            print("✅ Session ID personnalisé accepté")
    
    def test_create_session_error_handling(self):
        """Test gestion d'erreur lors de la création"""
        mock_ctx = Mock(spec=JobContext)
        mock_ctx.room = Mock()
        mock_ctx.room.name = "test-room"
        
        config = {'instructions': 'Test'}
        
        with patch('core.session_manager.AgentSession', side_effect=Exception("Creation failed")):
            with pytest.raises(SessionCreationError) as exc_info:
                self.session_manager.create_session(mock_ctx, config)
            
            assert "Impossible de créer la session" in str(exc_info.value)
            print("✅ Erreur création session gérée")
    
    @pytest.mark.asyncio
    async def test_start_session_success(self):
        """Test démarrage de session réussi"""
        mock_session = AsyncMock(spec=AgentSession)
        mock_agent = Mock()
        mock_room = Mock()
        
        await self.session_manager.start_session(mock_session, mock_agent, mock_room)
        
        mock_session.start.assert_called_once_with(agent=mock_agent, room=mock_room)
        print("✅ Démarrage session réussi")
    
    @pytest.mark.asyncio
    async def test_start_session_error(self):
        """Test erreur lors du démarrage de session"""
        mock_session = AsyncMock(spec=AgentSession)
        mock_session.start.side_effect = Exception("Start failed")
        mock_agent = Mock()
        mock_room = Mock()
        
        with pytest.raises(SessionStartError) as exc_info:
            await self.session_manager.start_session(mock_session, mock_agent, mock_room)
        
        assert "Impossible de démarrer la session" in str(exc_info.value)
        print("✅ Erreur démarrage session gérée")
    
    def test_get_session_metrics(self):
        """Test récupération des métriques de session"""
        # Simuler l'ajout d'une session avec métriques
        session_id = "test-session-123"
        mock_metrics = Mock()
        
        self.session_manager._session_metrics[session_id] = mock_metrics
        
        retrieved_metrics = self.session_manager.get_session_metrics(session_id)
        assert retrieved_metrics is mock_metrics
        
        # Test session inexistante
        non_existent = self.session_manager.get_session_metrics("non-existent")
        assert non_existent is None
        
        print("✅ Récupération métriques fonctionne")
    
    def test_cleanup_session(self):
        """Test nettoyage des ressources de session"""
        session_id = "test-session-123"
        mock_session = Mock(spec=AgentSession)
        mock_metrics = Mock()
        
        # Ajouter session et métriques
        self.session_manager._active_sessions[session_id] = mock_session
        self.session_manager._session_metrics[session_id] = mock_metrics
        
        # Nettoyer
        self.session_manager.cleanup_session(session_id)
        
        # Vérifier suppression
        assert session_id not in self.session_manager._active_sessions
        assert session_id not in self.session_manager._session_metrics
        print("✅ Nettoyage session fonctionne")
    
    def test_multiple_sessions_management(self):
        """Test gestion de plusieurs sessions simultanées"""
        mock_ctx = Mock(spec=JobContext)
        mock_room = Mock(spec=Room)
        mock_ctx.room = mock_room
        mock_ctx.room.name = "test-room"
        
        config = {'instructions': 'Test'}
        
        with patch('core.session_manager.AgentSession'):
            with patch('core.session_manager.silero.VAD.load'):
                with patch('core.session_manager.openai.STT'):
                    with patch('core.session_manager.openai.LLM'):
                        with patch('core.session_manager.openai.TTS'):
                            # Créer plusieurs sessions
                            session1, id1 = self.session_manager.create_session(mock_ctx, config)
                            session2, id2 = self.session_manager.create_session(mock_ctx, config)
                            
                            assert id1 != id2
                            assert len(self.session_manager._active_sessions) == 2
                            
                            # Nettoyer une session
                            self.session_manager.cleanup_session(id1)
                            assert len(self.session_manager._active_sessions) == 1
                            assert id2 in self.session_manager._active_sessions
                            
                            print("✅ Gestion multiple sessions fonctionne")


if __name__ == "__main__":
    # Exécution directe pour validation rapide
    import asyncio
    
    test_instance = TestSessionManager()
    
    try:
        print("🧪 Tests SessionManager...")
        test_instance.setup_method()
        test_instance.test_singleton_pattern()
        test_instance.setup_method()
        test_instance.test_create_session_success()
        test_instance.setup_method()
        test_instance.test_create_session_error_handling()
        
        # Test async
        async def run_async_tests():
            test_instance.setup_method()
            await test_instance.test_start_session_success()
            await test_instance.test_start_session_error()
        
        asyncio.run(run_async_tests())
        
        test_instance.setup_method()
        test_instance.test_get_session_metrics()
        test_instance.test_cleanup_session()
        
        print("\n✅ Tous les tests SessionManager réussis")
    except Exception as e:
        print(f"\n❌ Échec test SessionManager: {e}")
        raise
