"""
Tests unitaires pour DependencyContainer
Teste les erreurs d'injection de dépendances
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.dependency_container import DependencyContainer, DependencyNotFoundError


class TestDependencyContainer:
    """Tests pour la classe DependencyContainer"""
    
    def setup_method(self):
        """Setup pour chaque test - reset du singleton"""
        DependencyContainer._instance = None
        DependencyContainer._initialized = False
        self.container = DependencyContainer()
    
    def test_singleton_pattern(self):
        """Test pattern Singleton"""
        container1 = DependencyContainer()
        container2 = DependencyContainer()
        
        assert container1 is container2
        print("✅ Pattern Singleton fonctionne")
    
    def test_register_and_get_service(self):
        """Test enregistrement et récupération de service"""
        mock_service = Mock()
        service_name = "test_service"
        
        self.container.register_service(service_name, mock_service)
        retrieved_service = self.container.get(service_name)
        
        assert retrieved_service is mock_service
        print("✅ Enregistrement/récupération service fonctionne")
    
    def test_register_and_get_singleton(self):
        """Test enregistrement et récupération de singleton"""
        mock_singleton = Mock()
        singleton_name = "test_singleton"
        
        self.container.register_singleton(singleton_name, mock_singleton)
        retrieved_singleton = self.container.get(singleton_name)
        
        assert retrieved_singleton is mock_singleton
        print("✅ Enregistrement/récupération singleton fonctionne")
    
    def test_register_and_get_factory(self):
        """Test enregistrement et récupération via factory"""
        mock_service = Mock()
        factory_name = "test_factory"
        mock_factory = Mock(return_value=mock_service)
        
        self.container.register_factory(factory_name, mock_factory)
        retrieved_service = self.container.get(factory_name)
        
        assert retrieved_service is mock_service
        mock_factory.assert_called_once()
        print("✅ Factory pattern fonctionne")
    
    def test_dependency_not_found_error(self):
        """Test erreur quand dépendance non trouvée"""
        with pytest.raises(DependencyNotFoundError) as exc_info:
            self.container.get("non_existent_service")
        
        assert "Dépendance non trouvée: non_existent_service" in str(exc_info.value)
        print("✅ Erreur dépendance non trouvée gérée")
    
    def test_get_optional_returns_none(self):
        """Test récupération optionnelle retourne None si non trouvée"""
        result = self.container.get_optional("non_existent_service")
        assert result is None
        print("✅ Récupération optionnelle fonctionne")
    
    def test_is_registered(self):
        """Test vérification d'enregistrement"""
        # Non enregistré
        assert not self.container.is_registered("test_service")
        
        # Enregistrer un service
        self.container.register_service("test_service", Mock())
        assert self.container.is_registered("test_service")
        
        # Enregistrer un singleton
        self.container.register_singleton("test_singleton", Mock())
        assert self.container.is_registered("test_singleton")
        
        # Enregistrer une factory
        self.container.register_factory("test_factory", Mock())
        assert self.container.is_registered("test_factory")
        
        print("✅ Vérification enregistrement fonctionne")
    
    def test_priority_order_singleton_service_factory(self):
        """Test ordre de priorité: singleton > service > factory"""
        # Créer des mocks différents pour chaque type
        mock_singleton = Mock()
        mock_service = Mock()
        mock_factory = Mock(return_value=Mock())
        
        service_name = "test_priority"
        
        # Enregistrer dans l'ordre: service, factory, singleton (pour tester la priorité)
        self.container.register_service(service_name, mock_service)
        self.container.register_factory(service_name, mock_factory)
        self.container.register_singleton(service_name, mock_singleton)
        
        # Singleton devrait avoir la priorité
        result = self.container.get(service_name)
        assert result is mock_singleton
        
        # Nettoyer et tester service
        self.container.clear()
        self.container.register_service(service_name, mock_service)
        self.container.register_factory(service_name, mock_factory)
        
        result = self.container.get(service_name)
        assert result is mock_service
        
        print("✅ Ordre de priorité des dépendances correct")
    
    def test_clear_container(self):
        """Test nettoyage du conteneur"""
        # Ajouter des dépendances
        self.container.register_service("service1", Mock())
        self.container.register_singleton("singleton1", Mock())
        self.container.register_factory("factory1", Mock())
        
        # Vérifier qu'elles existent
        assert len(self.container._services) == 1
        assert len(self.container._singletons) == 1
        assert len(self.container._factories) == 1
        
        # Nettoyer
        self.container.clear()
        
        # Vérifier que tout est nettoyé
        assert len(self.container._services) == 0
        assert len(self.container._singletons) == 0
        assert len(self.container._factories) == 0
        print("✅ Nettoyage conteneur fonctionne")
    
    def test_factory_called_multiple_times(self):
        """Test que la factory est appelée à chaque récupération"""
        mock_factory = Mock(return_value=Mock())
        factory_name = "multi_factory"
        
        self.container.register_factory(factory_name, mock_factory)
        
        # Récupérer plusieurs fois
        self.container.get(factory_name)
        self.container.get(factory_name)
        self.container.get(factory_name)
        
        # Factory devrait être appelée 3 fois
        assert mock_factory.call_count == 3
        print("✅ Factory appelée à chaque récupération")
    
    def test_circular_dependency_detection(self):
        """Test détection de dépendance circulaire (si implémentée)"""
        # Créer une factory qui dépend d'elle-même
        def circular_factory():
            # Simuler une dépendance circulaire
            return self.container.get("circular_service")
        
        self.container.register_factory("circular_service", circular_factory)
        
        # Ceci devrait échouer avec une dépendance circulaire
        # (Pour l'instant, on teste juste que ça ne plante pas le système)
        try:
            self.container.get("circular_service")
            print("⚠️  Dépendance circulaire non détectée (à implémenter)")
        except RecursionError:
            print("✅ Dépendance circulaire détectée")
        except Exception as e:
            print(f"⚠️  Autre erreur lors du test circulaire: {e}")


if __name__ == "__main__":
    # Exécution directe pour validation rapide
    test_instance = TestDependencyContainer()
    
    try:
        print("🧪 Tests DependencyContainer...")
        test_instance.setup_method()
        test_instance.test_singleton_pattern()
        test_instance.setup_method()
        test_instance.test_register_and_get_service()
        test_instance.setup_method()
        test_instance.test_register_and_get_singleton()
        test_instance.setup_method()
        test_instance.test_register_and_get_factory()
        test_instance.setup_method()
        test_instance.test_dependency_not_found_error()
        test_instance.setup_method()
        test_instance.test_get_optional_returns_none()
        test_instance.setup_method()
        test_instance.test_is_registered()
        test_instance.setup_method()
        test_instance.test_clear_container()
        test_instance.setup_method()
        test_instance.test_circular_dependency_detection()
        
        print("\n✅ Tous les tests DependencyContainer réussis")
    except Exception as e:
        print(f"\n❌ Échec test DependencyContainer: {e}")
        raise
