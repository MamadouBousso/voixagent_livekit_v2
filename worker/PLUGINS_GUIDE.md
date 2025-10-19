# Guide des Plugins - Système d'Extension de l'Agent

## 🤔 À quoi servent les plugins ?

Les **plugins** sont des **extensions modulaires** qui permettent d'**ajouter des fonctionnalités** à votre agent vocal **sans modifier le code principal**. C'est le système d'extension le plus puissant du projet !

## 🎯 Rôles des Plugins

### **1. Traitement des Messages**
Les plugins peuvent **intercepter et modifier** les messages avant et après traitement :

```python
async def process_message(self, message: str, context: Dict[str, Any]) -> str:
    # Traiter le message avant l'envoi au LLM
    return modified_message
```

### **2. Analyse en Temps Réel**
- **Analyse des sentiments** : Détecter l'émotion de l'utilisateur
- **Détection de langage** : Identifier la langue parlée
- **Analyse de contenu** : Scanner pour du contenu inapproprié

### **3. Personnalisation du Comportement**
- **Mémoire conversationnelle** : Se souvenir des conversations précédentes
- **Adaptation contextuelle** : Changer le ton selon la situation
- **Réponses personnalisées** : Réponses spécifiques à certains mots-clés

### **4. Intégrations Externes**
- **API tierces** : Intégrer avec d'autres services
- **Bases de données** : Stocker/récupérer des informations
- **Webhooks** : Notifier d'autres systèmes

## 🔌 Types de Plugins Exemples

### **Filtre de Contenu Inapproprié**
```python
class ProfanityFilterPlugin(AgentPlugin):
    def __init__(self, **kwargs):
        self.bad_words = kwargs.get('bad_words', ['mot1', 'mot2'])
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        for word in self.bad_words:
            if word in message.lower():
                return "Je préfère ne pas répondre à cela."
        return message
```

### **Analyse des Sentiments**
```python
class SentimentAnalysisPlugin(AgentPlugin):
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        sentiment = analyze_sentiment(message)
        
        if sentiment < -0.5:  # Utilisateur en colère
            return f"Je comprends votre frustration. {message}"
        elif sentiment > 0.5:  # Utilisateur content
            return f"Je suis content que vous soyez heureux ! {message}"
        
        return message
```

### **Mémoire Conversationnelle**
```python
class ConversationMemoryPlugin(AgentPlugin):
    def __init__(self, **kwargs):
        self.memory_size = kwargs.get('memory_size', 10)
        self.conversations = {}
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        session_id = context.get('session_id')
        
        # Stocker le message
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            'user': message,
            'timestamp': datetime.now()
        })
        
        return message  # Transmettre sans modification
```

### **Plugin de Traduction**
```python
class TranslationPlugin(AgentPlugin):
    def __init__(self, **kwargs):
        self.target_language = kwargs.get('target_language', 'en')
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        # Traduire le message entrant
        translated_input = translate(message, self.target_language)
        
        # Traiter avec l'agent
        # ... (logique de traitement)
        
        # Traduire la réponse
        return translate(response, 'fr')
```

## 🚀 Utilisation Pratique

### **Ajout d'un Plugin**

#### Via CLI (NO-CODE)
```bash
# Ajouter le plugin d'analyse des sentiments
python manage_agents.py plugins add --name sentiment_analysis

# Ajouter un filtre de contenu
python manage_agents.py plugins add --name profanity_filter
```

#### Via Configuration JSON
```json
{
  "enabled_plugins": [
    {
      "plugin_name": "sentiment_analysis",
      "enabled": true,
      "config": {
        "threshold": 0.7,
        "language": "fr"
      }
    },
    {
      "plugin_name": "conversation_memory", 
      "enabled": true,
      "config": {
        "memory_size": 50,
        "persist_to_db": true
      }
    }
  ]
}
```

### **Plugins Disponibles**

```bash
# Lister tous les plugins
python manage_agents.py plugins list
```

## 🎪 Exemples Concrets d'Usage

### **Cas d'Usage 1 : Agent de Support Client**
```json
{
  "enabled_plugins": [
    {
      "plugin_name": "sentiment_analysis",
      "enabled": true,
      "config": {"escalate_threshold": -0.8}
    },
    {
      "plugin_name": "customer_database",
      "enabled": true,
      "config": {"api_url": "https://crm.company.com"}
    },
    {
      "plugin_name": "ticket_creator",
      "enabled": true
    }
  ]
}
```

**Résultat** : L'agent détecte automatiquement les clients mécontents et crée des tickets de support.

### **Cas d'Usage 2 : Agent Multilingue**
```json
{
  "enabled_plugins": [
    {
      "plugin_name": "language_detection",
      "enabled": true
    },
    {
      "plugin_name": "translation",
      "enabled": true,
      "config": {
        "auto_translate": true,
        "target_languages": ["en", "es", "fr"]
      }
    }
  ]
}
```

**Résultat** : L'agent détecte la langue et répond automatiquement dans la langue appropriée.

### **Cas d'Usage 3 : Agent de Formation**
```json
{
  "enabled_plugins": [
    {
      "plugin_name": "conversation_memory",
      "enabled": true,
      "config": {"persist_sessions": true}
    },
    {
      "plugin_name": "quiz_generator",
      "enabled": true,
      "config": {"difficulty_level": "beginner"}
    },
    {
      "plugin_name": "progress_tracker",
      "enabled": true,
      "config": {"analytics_endpoint": "https://platform.analytics.com"}
    }
  ]
}
```

**Résultat** : L'agent se souvient des sessions précédentes, génère des quiz et suit les progrès.

## 🔧 Comment Créer un Plugin

### **Structure de Base**
```python
from core.interfaces import AgentPlugin

class MonPlugin(AgentPlugin):
    def __init__(self, **kwargs):
        self.name = "Mon Plugin"
        self.config = kwargs
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        # Votre logique ici
        return message
    
    def get_name(self) -> str:
        return self.name
    
    def is_enabled(self) -> bool:
        return True
```

### **Enregistrement du Plugin**
```python
from core.factories import PluginFactory
from mon_plugin import MonPlugin

PluginFactory.register_plugin("mon_plugin", MonPlugin)
```

## 📊 Avantages des Plugins

### **🔧 Extensibilité**
- Ajout de fonctionnalités **sans casser** le code principal
- **Modularité** : Chaque plugin a une responsabilité unique

### **⚡ Flexibilité**
- **Activation/Désactivation** à la volée
- **Configuration** différente par plugin
- **Composition** de multiples plugins

### **🔒 Sécurité**
- **Isolation** : Un plugin défaillant n'affecte pas les autres
- **Permissions** : Contrôler l'accès aux ressources

### **🎛️ Contrôle**
- **NO-CODE** : Ajout via configuration seulement
- **Hot-swapping** : Changement sans redémarrage
- **Monitoring** : Métriques par plugin

## 🚨 Points d'Attention

### **Performance**
- Les plugins ajoutent de la **latence**
- **Ordre d'exécution** peut importer
- **Cache** pour éviter les recalculs

### **Compatibilité**
- **Versioning** des plugins
- **Dépendances** entre plugins
- **Tests** avant déploiement

## 🎯 Résumé

Les plugins servent à **étendre les capacités** de votre agent vocal de manière **modulaire et flexible** :

1. **Traitement** des messages et réponses
2. **Analyse** en temps réel (sentiments, langue, etc.)
3. **Intégrations** avec des services externes
4. **Personnalisation** du comportement
5. **Extension** du pipeline **sans coder**

C'est le système le plus puissant pour **personnaliser votre agent** selon vos besoins spécifiques ! 🚀
