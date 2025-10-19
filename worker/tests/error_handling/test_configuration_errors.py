"""
Tests spécifiques pour les erreurs de configuration documentées
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.configuration_builder import ConfigurationBuilder, ConfigurationError


class TestConfigurationErrors:
    """Tests pour les erreurs de configuration spécifiques"""
    
    def test_quoted_environment_variables_error(self):
        """Test problème des variables entre guillemets dans .env"""
        # Ce problème a été rencontré: LLM_MODEL="gpt-4o-mini" au lieu de LLM_MODEL=gpt-4o-mini
        
        with patch.dict(os.environ, clear=True):
            # Variables avec guillemets (le problème détecté)
            os.environ['LLM_MODEL'] = '"gpt-4o-mini"'
            os.environ['TTS_MODEL'] = '"tts-1"'
            os.environ['STT_MODEL'] = '"whisper-1"'
            
            builder = ConfigurationBuilder()
            builder.load_from_env()
            
            # Le problème: les guillemets causent une erreur de validation
            with pytest.raises(ConfigurationError) as exc_info:
                config = builder.build()
            
            assert "Modèle TTS invalide" in str(exc_info.value)
            assert '"tts-1"' in str(exc_info.value)
            
            # Ceci devrait causer des problèmes d'usage
            print("✅ PROBLÈME DÉTECTÉ: Variables avec guillemets")
            print(f"   Erreur: {str(exc_info.value)}")
            print("   Solution: Supprimer les guillemets du fichier .env")
    
    def test_invalid_tts_model_eleven_labs_error(self):
        """Test erreur modèle TTS ElevenLabs incompatible"""
        # Problème rencontré: TTS_MODEL=eleven_turbo_v2 avec openai.TTS()
        
        builder = ConfigurationBuilder()
        builder.with_tts_model("eleven_turbo_v2")  # Modèle ElevenLabs
        
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        
        error_msg = str(exc_info.value)
        assert "Modèle TTS invalide" in error_msg
        assert "eleven_turbo_v2" in error_msg
        assert "tts-1" in error_msg or "tts-1-hd" in error_msg  # Modèles valides mentionnés
        
        print("✅ ERREUR TTS ElevenLabs DÉTECTÉE")
        print(f"   Erreur: {error_msg}")
        print("   Solution: Utiliser tts-1 ou tts-1-hd pour OpenAI")
    
    def test_missing_env_variables_graceful_handling(self):
        """Test gestion gracieuse des variables d'environnement manquantes"""
        with patch.dict(os.environ, clear=True):
            # Aucune variable d'environnement définie
            builder = ConfigurationBuilder()
            config = builder.load_from_env().build()
            
            # Devrait utiliser les valeurs par défaut
            assert config.instructions == "You are a friendly, concise assistant. Keep answers short."
            assert config.stt_model == "whisper-1"
            assert config.llm_model == "gpt-4o-mini"
            assert config.tts_model == "tts-1"
            assert config.tts_voice == "alloy"
            
            print("✅ Variables manquantes gérées avec valeurs par défaut")
    
    def test_empty_configuration_values_error(self):
        """Test erreurs pour valeurs vides"""
        builder = ConfigurationBuilder()
        
        # Test instructions vides
        builder.with_instructions("   ")  # Espaces seulement
        with pytest.raises(ConfigurationError) as exc_info:
            builder.validate()
        assert "instructions" in str(exc_info.value).lower()
        
        builder = ConfigurationBuilder()
        builder.with_instructions("")  # Vide
        with pytest.raises(ConfigurationError):
            builder.validate()
        
        print("✅ Erreurs valeurs vides détectées")
    
    def test_agent_config_integration_errors(self):
        """Test erreurs d'intégration avec agent_config modulaire"""
        # Test avec agent_config None
        builder = ConfigurationBuilder()
        config = builder.load_from_agent_config(None).build()
        
        # Devrait utiliser les valeurs par défaut
        assert config.instructions == "You are a friendly, concise assistant. Keep answers short."
        
        # Test avec agent_config sans attributs attendus
        mock_agent_config = Mock()
        mock_agent_config.system_instructions = None  # Attribut présent mais None
        
        builder = ConfigurationBuilder()
        config = builder.load_from_agent_config(mock_agent_config).build()
        
        # Devrait utiliser les valeurs par défaut
        assert config.instructions == "You are a friendly, concise assistant. Keep answers short."
        
        print("✅ Intégration agent_config gérée gracieusement")
    
    def test_configuration_validation_comprehensive(self):
        """Test validation complète de configuration"""
        builder = ConfigurationBuilder()
        
        # Configuration valide
        valid_config = builder.with_instructions("Valid instructions")\
                            .with_stt_model("whisper-1")\
                            .with_llm_model("gpt-4o")\
                            .with_tts_model("tts-1-hd", "nova")\
                            .build()
        
        assert valid_config.instructions == "Valid instructions"
        assert valid_config.tts_model == "tts-1-hd"
        assert valid_config.tts_voice == "nova"
        
        print("✅ Configuration valide acceptée")
        
        # Test avec TTS modèle invalide
        builder_invalid = ConfigurationBuilder()
        builder_invalid.with_tts_model("invalid-model")
        
        with pytest.raises(ConfigurationError):
            builder_invalid.validate()
        
        print("✅ Configuration invalide rejetée")


if __name__ == "__main__":
    test_instance = TestConfigurationErrors()
    
    try:
        print("🧪 Tests erreurs de configuration...")
        test_instance.test_quoted_environment_variables_error()
        test_instance.test_invalid_tts_model_eleven_labs_error()
        test_instance.test_missing_env_variables_graceful_handling()
        test_instance.test_empty_configuration_values_error()
        test_instance.test_agent_config_integration_errors()
        test_instance.test_configuration_validation_comprehensive()
        
        print("\n✅ Tous les tests erreurs configuration réussis")
    except Exception as e:
        print(f"\n❌ Échec tests configuration: {e}")
        raise
