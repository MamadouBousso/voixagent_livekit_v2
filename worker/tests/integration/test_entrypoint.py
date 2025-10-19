"""
Tests d'intégration pour la fonction entrypoint
Teste les erreurs de connexion et de session documentées
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Mock des imports LiveKit pour les tests
try:
    from livekit.agents import JobContext, Room
except ImportError:
    JobContext = type('JobContext', (), {})
    Room = type('Room', (), {})


class MockJobContext:
    """Mock pour JobContext"""
    def __init__(self, room_name="test-room"):
        self.room = Mock(spec=Room)
        self.room.name = room_name
    
    async def connect(self, auto_subscribe=None):
        """Mock de la connexion"""
        return True


class TestEntrypointIntegration:
    """Tests d'intégration pour entrypoint"""
    
    @pytest.fixture
    def mock_ctx(self):
        """Fixture pour JobContext mocké"""
        return MockJobContext("test-room")
    
    @pytest.mark.asyncio
    async def test_entrypoint_configuration_error(self):
        """Test erreur de configuration dans entrypoint"""
        from core.configuration_builder import ConfigurationError
        
        mock_ctx = MockJobContext()
        
        with patch('worker.app.container') as mock_container:
            with patch('worker.app.agent_factory') as mock_factory:
                # Simuler une erreur de configuration
                mock_factory.get_configuration_from_builder.side_effect = ConfigurationError("Invalid config")
                
                # Import de entrypoint depuis app.py
                from worker.app import entrypoint
                
                with pytest.raises(ConfigurationError):
                    await entrypoint(mock_ctx)
                
                print("✅ Erreur configuration entrypoint détectée")
    
    @pytest.mark.asyncio
    async def test_entrypoint_session_creation_error(self):
        """Test erreur de création de session dans entrypoint"""
        from core.session_manager import SessionCreationError
        
        mock_ctx = MockJobContext()
        
        with patch('worker.app.container') as mock_container:
            with patch('worker.app.agent_factory') as mock_factory:
                with patch('worker.app.session_manager') as mock_session_manager:
                    # Setup des mocks
                    mock_config = Mock()
                    mock_config.instructions = "Test"
                    mock_config.__dict__ = {'instructions': 'Test'}
                    mock_factory.get_configuration_from_builder.return_value = mock_config
                    mock_factory.create_agent_from_config.return_value = Mock()
                    
                    # Simuler erreur création session
                    mock_session_manager.create_session.side_effect = SessionCreationError("Session creation failed")
                    
                    from worker.app import entrypoint
                    
                    with pytest.raises(SessionCreationError):
                        await entrypoint(mock_ctx)
                    
                    print("✅ Erreur création session entrypoint détectée")
    
    @pytest.mark.asyncio
    async def test_entrypoint_successful_flow(self):
        """Test flux réussi de entrypoint"""
        mock_ctx = MockJobContext()
        
        with patch('worker.app.container') as mock_container:
            with patch('worker.app.agent_factory') as mock_factory:
                with patch('worker.app.session_manager') as mock_session_manager:
                    # Setup des mocks pour un flux réussi
                    mock_config = Mock()
                    mock_config.instructions = "Test instructions"
                    mock_config.__dict__ = {
                        'instructions': 'Test instructions',
                        'stt_model': 'whisper-1',
                        'llm_model': 'gpt-4o-mini',
                        'tts_model': 'tts-1',
                        'tts_voice': 'alloy'
                    }
                    
                    mock_agent = Mock()
                    mock_session = AsyncMock()
                    mock_session_id = "test-session-123"
                    
                    mock_factory.get_configuration_from_builder.return_value = mock_config
                    mock_factory.create_agent_from_config.return_value = mock_agent
                    mock_session_manager.create_session.return_value = (mock_session, mock_session_id)
                    mock_session_manager.get_session_metrics.return_value = Mock()
                    
                    from worker.app import entrypoint
                    
                    # Le test devrait réussir
                    await entrypoint(mock_ctx)
                    
                    # Vérifier que les bonnes méthodes ont été appelées
                    mock_ctx.connect.assert_called_once()
                    mock_factory.get_configuration_from_builder.assert_called_once()
                    mock_session_manager.create_session.assert_called_once()
                    mock_session.start.assert_called_once_with(agent=mock_agent, room=mock_ctx.room)
                    
                    print("✅ Flux entrypoint réussi")
    
    @pytest.mark.asyncio
    async def test_entrypoint_session_start_error(self):
        """Test erreur lors du démarrage de session"""
        mock_ctx = MockJobContext()
        
        with patch('worker.app.container') as mock_container:
            with patch('worker.app.agent_factory') as mock_factory:
                with patch('worker.app.session_manager') as mock_session_manager:
                    # Setup des mocks
                    mock_config = Mock()
                    mock_config.instructions = "Test"
                    mock_config.__dict__ = {'instructions': 'Test'}
                    
                    mock_agent = Mock()
                    mock_session = AsyncMock()
                    mock_session.start.side_effect = Exception("Session start failed")
                    mock_session_id = "test-session-123"
                    
                    mock_factory.get_configuration_from_builder.return_value = mock_config
                    mock_factory.create_agent_from_config.return_value = mock_agent
                    mock_session_manager.create_session.return_value = (mock_session, mock_session_id)
                    mock_session_manager.get_session_metrics.return_value = Mock()
                    
                    from worker.app import entrypoint
                    
                    with pytest.raises(Exception, match="Session start failed"):
                        await entrypoint(mock_ctx)
                    
                    # Vérifier que cleanup a été appelé
                    mock_session_manager.cleanup_session.assert_called_with(mock_session_id)
                    print("✅ Erreur démarrage session entrypoint gérée")


if __name__ == "__main__":
    # Exécution directe pour validation rapide
    async def run_tests():
        test_instance = TestEntrypointIntegration()
        
        try:
            print("🧪 Tests d'intégration entrypoint...")
            await test_instance.test_entrypoint_successful_flow(None)  # mock_ctx sera créé dans le test
            print("\n✅ Tests d'intégration entrypoint réussis")
        except Exception as e:
            print(f"\n❌ Échec tests intégration: {e}")
            raise
    
    # Note: Les tests avec pytest.mark.asyncio nécessitent pytest-asyncio
    # Pour l'exécution directe, on peut utiliser asyncio.run
    try:
        asyncio.run(run_tests())
    except ImportError:
        print("⚠️  Tests d'intégration nécessitent pytest-asyncio pour l'exécution complète")
        print("Exécutez avec: pytest tests/integration/test_entrypoint.py -v")
