"""
Dependency Injection Container - Gestion des dépendances
Utilise le pattern Service Locator / Dependency Injection
"""

import logging
from typing import Dict, Any, TypeVar, Type, Callable
from abc import ABC, abstractmethod

T = TypeVar('T')


class DependencyContainer:
    """
    Conteneur de dépendances utilisant le pattern Singleton
    Gère l'injection de dépendances et les instances partagées
    """
    
    _instance: 'DependencyContainer' = None
    
    def __new__(cls) -> 'DependencyContainer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._services: Dict[str, Any] = {}
            self._factories: Dict[str, Callable] = {}
            self._singletons: Dict[str, Any] = {}
            self._initialized = True
            logging.info("DependencyContainer initialisé")
    
    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Enregistre une instance singleton dans le conteneur
        """
        self._singletons[name] = instance
        logging.debug(f"Singleton enregistré: {name}")
    
    def register_factory(self, name: str, factory: Callable) -> None:
        """
        Enregistre une factory pour créer des instances à la demande
        """
        self._factories[name] = factory
        logging.debug(f"Factory enregistrée: {name}")
    
    def register_service(self, name: str, service: Any) -> None:
        """
        Enregistre un service dans le conteneur
        """
        self._services[name] = service
        logging.debug(f"Service enregistré: {name}")
    
    def get(self, name: str) -> Any:
        """
        Récupère une dépendance du conteneur
        """
        # Vérifier d'abord les singletons
        if name in self._singletons:
            return self._singletons[name]
        
        # Ensuite les services
        if name in self._services:
            return self._services[name]
        
        # Enfin les factories
        if name in self._factories:
            instance = self._factories[name]()
            logging.debug(f"Instance créée via factory: {name}")
            return instance
        
        raise DependencyNotFoundError(f"Dépendance non trouvée: {name}")
    
    def get_optional(self, name: str) -> Any:
        """
        Récupère une dépendance de manière optionnelle (retourne None si non trouvée)
        """
        try:
            return self.get(name)
        except DependencyNotFoundError:
            return None
    
    def is_registered(self, name: str) -> bool:
        """
        Vérifie si une dépendance est enregistrée
        """
        return (name in self._singletons or 
                name in self._services or 
                name in self._factories)
    
    def clear(self) -> None:
        """
        Nettoie toutes les dépendances (utile pour les tests)
        """
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logging.info("Conteneur de dépendances nettoyé")


class DependencyNotFoundError(Exception):
    """Exception levée quand une dépendance n'est pas trouvée"""
    pass


# Instance globale du conteneur
container = DependencyContainer()
