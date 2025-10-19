"""
Tests unitaires pour ConfigurationBuilder
Teste toutes les erreurs de configuration documentées
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.configuration_builder import ConfigurationBuilder, AgentConfiguration, ConfigurationError


class TestConfigurationBuilder:
    """Tests pour la classe ConfigurationBuilder"""
    
    def test_default_configuration(self):
        """Test création avec configuration par défaut"""
        builder = ConfigurationBuilder()
        config = builder.build()
        
        assert config.instructions == "You are a friendly, concise assistant. Keep answers short."
        assert config.stt_model == "whisper-1"
        assert config.llm_model == "gpt-4o-mini"
        assert config.tts_model == "tts-1"
        assert config.tts_voice == "alloy"
        print("✅ Configuration par défaut correcte")
    
    @patch.dict(os.environ, {
        'AGENT_INSTRUCTIONS': 'Test instructions',
        'STT_MODEL': 'whisper-1',
        'LLM_MODEL': 'gpt-4o',
        'TTS_MODEL': 'tts-1-hd',
        'TTS_VOICE_ID': 'nova'
    })
    def test_load_from_environment(self):
        """Test chargement depuis variables d'environnement"""
        builder = ConfigurationBuilder()
        config = builder.load_from_env().build()
        
        assert config.instructions == 'Test instructions'
        assert config.stt_model == 'whisper-1'
        assert config.llm_model == 'gpt-4o'
        assert config.tts_model == 'tts-1-hd'
        assert config.tts_voice == 'nova'
        print("✅ Chargement depuis variables d'environnement correct")
    
    def test_invalid_tts_model_raises_error(self):
        """Test erreur pour modèle TTS invalide"""
        builder = ConfigurationBuilder()
        builder.with_tts_model("eleven_turbo_v2")  # Modèle invalide
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        assert "Modèle TTS invalide" in str(exc_info.value)
        print("✅ Erreur TTS modèle invalide détectée")
    
    def test_empty_instructions_raises_error(self):
        """Test erreur pour instructions vides"""
        builder = ConfigurationBuilder()
        builder.with_instructions("")
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        assert "Les instructions de l'agent ne peuvent pas être vides" in str(exc_info.value)
        print("✅ Erreur instructions vides détectée")
    
    def test_empty_stt_model_raises_error(self):
        """Test erreur pour modèle STT vide"""
        builder = ConfigurationBuilder()
        builder.with_stt_model("")
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        assert "Le modèle STT doit être défini" in str(exc_info.value)
        print("✅ Erreur modèle STT vide détectée")
    
    def test_empty_llm_model_raises_error(self):
        """Test erreur pour modèle LLM vide"""
        builder = ConfigurationBuilder()
        builder.with_llm_model("")
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        assert "Le modèle LLM doit être défini" in str(exc_info.value)
        print("✅ Erreur modèle LLM vide détectée")
    
    def test_empty_tts_model_raises_error(self):
        """Test erreur pour modèle TTS vide"""
        builder = ConfigurationBuilder()
        builder.with_tts_model("")
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        assert "Le modèle TTS doit être défini" in str(exc_info.value)
        print("✅ Erreur modèle TTS vide détectée")
    
    def test_chained_builder_methods(self):
        """Test méthodes chainables du builder"""
        config = (ConfigurationBuilder()
                 .with_instructions("Custom instructions")
                 .with_stt_model("whisper-1")
                 .with_llm_model("gpt-4")
                 .with_tts_model("tts-1", "alloy")
                 .build())
        
        assert config.instructions == "Custom instructions"
        assert config.stt_model == "whisper-1"
        assert config.llm_model == "gpt-4"
        assert config.tts_model == "tts-1"
        assert config.tts_voice == "alloy"
        print("✅ Méthodes chainables fonctionnent")
    
    def test_quoted_environment_variables_issue(self):
        """Test problème des guillemets dans les variables d'environnement"""
        # Simule le problème découvert avec les variables entre guillemets
        with patch.dict(os.environ, clear=True):
            # Variables avec guillemets (problème)
            os.environ['LLM_MODEL'] = '"gpt-4o-mini"'
            os.environ['TTS_MODEL'] = '"tts-1"'  # Ceci va causer une erreur de validation
            
            builder = ConfigurationBuilder()
            builder.load_from_env()
            
            # Les guillemets causent une erreur car '"tts-1"' != 'tts-1'
            with pytest.raises(ConfigurationError) as exc_info:
                config = builder.build()
            
            assert "Modèle TTS invalide" in str(exc_info.value)
            assert '"tts-1"' in str(exc_info.value)
            print("✅ Détection problème variables entre guillemets - erreur attendue")
    
    def test_load_from_agent_config(self):
        """Test chargement depuis agent_config modulaire"""
        mock_agent_config = MagicMock()
        mock_agent_config.system_instructions = "Modular instructions"
        mock_agent_config.stt.model = "modular-stt"
        mock_agent_config.llm.model = "modular-llm"
        mock_agent_config.tts.model = "modular-tts"
        mock_agent_config.tts.voice = "modular-voice"
        
        builder = ConfigurationBuilder()
        config = builder.load_from_agent_config(mock_agent_config).build()
        
        assert config.instructions == "Modular instructions"
        assert config.stt_model == "modular-stt"
        assert config.llm_model == "modular-llm"
        assert config.tts_model == "modular-tts"
        assert config.tts_voice == "modular-voice"
        print("✅ Chargement depuis agent_config modulaire correct")
    
    def test_to_dict_conversion(self):
        """Test conversion en dictionnaire"""
        builder = ConfigurationBuilder()
        config_dict = builder.with_instructions("Test").build().__dict__
        
        expected_keys = {'instructions', 'stt_model', 'llm_model', 'tts_model', 'tts_voice'}
        assert set(config_dict.keys()) == expected_keys
        assert config_dict['instructions'] == "Test"
        print("✅ Conversion en dictionnaire correcte")


if __name__ == "__main__":
    # Exécution directe des tests pour validation rapide
    test_instance = TestConfigurationBuilder()
    
    try:
        print("🧪 Tests ConfigurationBuilder...")
        test_instance.test_default_configuration()
        test_instance.test_load_from_environment()
        test_instance.test_invalid_tts_model_raises_error()
        test_instance.test_empty_instructions_raises_error()
        test_instance.test_chained_builder_methods()
        test_instance.test_quoted_environment_variables_issue()
        print("\n✅ Tous les tests ConfigurationBuilder réussi")
    except Exception as e:
        print(f"\n❌ Échec test ConfigurationBuilder: {e}")
        raise
