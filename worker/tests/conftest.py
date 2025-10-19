"""
Configuration pytest pour les tests
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire worker au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_livekit_environment():
    """Fixture pour simuler un environnement LiveKit"""
    with patch('livekit.agents.Agent'):
        with patch('livekit.agents.AgentSession'):
            with patch('livekit.plugins.openai'):
                with patch('livekit.plugins.silero'):
                    yield


@pytest.fixture
def mock_environment_variables():
    """Fixture pour variables d'environnement de test"""
    test_env = {
        'LIVEKIT_URL': 'wss://test.livekit.cloud',
        'LIVEKIT_API_KEY': 'test-key',
        'LIVEKIT_API_SECRET': 'test-secret',
        'STT_MODEL': 'whisper-1',
        'LLM_MODEL': 'gpt-4o-mini',
        'TTS_MODEL': 'tts-1',
        'TTS_VOICE_ID': 'alloy',
        'AGENT_INSTRUCTIONS': 'Test assistant'
    }
    
    with patch.dict(os.environ, test_env, clear=True):
        yield test_env


@pytest.fixture
def mock_job_context():
    """Fixture pour JobContext mocké"""
    mock_ctx = Mock()
    mock_ctx.room = Mock()
    mock_ctx.room.name = "test-room"
    mock_ctx.connect = Mock(return_value=None)
    return mock_ctx
