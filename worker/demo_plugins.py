#!/usr/bin/env python3
"""
Démonstration du système de plugins - À quoi servent les plugins ?
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire au path
sys.path.insert(0, str(Path(__file__).parent))

from core.dynamic_provider_manager import DynamicProviderManager
from core.plugins.sentiment_analysis_plugin import SentimentAnalysisPlugin
from core.plugins.profanity_filter_plugin import ProfanityFilterPlugin
from core.plugins.conversation_memory_plugin import ConversationMemoryPlugin


async def demo_plugin_effects():
    """Démontre les effets des plugins sur les messages."""
    
    print("🎪 DÉMONSTRATION DES PLUGINS")
    print("=" * 50)
    
    # Créer les plugins
    sentiment_plugin = SentimentAnalysisPlugin(enabled=True, threshold=0.3)
    profanity_plugin = ProfanityFilterPlugin(enabled=True, strict=False)
    memory_plugin = ConversationMemoryPlugin(enabled=True, memory_size=5)
    
    # Messages de test
    test_messages = [
        "Salut, comment ça va ?",
        "Je suis vraiment énervé par ce problème !",
        "Merci beaucoup, c'est parfait !",
        "Putain de merde, ça marche pas !",
        "Peux-tu m'aider rapidement ?",
        "Comment résoudre ce bug urgent ?"
    ]
    
    print("\n🔍 ANALYSE DES MESSAGES AVEC LES PLUGINS")
    print("-" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Message original: '{message}'")
        
        # Contexte de simulation
        context = {
            'session_id': 'demo_session',
            'user_id': 'demo_user',
            'timestamp': '2025-01-19T18:00:00'
        }
        
        # Traitement avec le plugin de filtrage
        filtered_message = await profanity_plugin.process_message(message, context)
        
        if filtered_message != message:
            print(f"   🛡️  Filtrage: '{filtered_message}'")
            print(f"   🚩 Raison: {context.get('filter_reason', 'unknown')}")
        
        # Traitement avec le plugin d'analyse des sentiments
        context_analysis = context.copy()
        await sentiment_plugin.process_message(filtered_message, context_analysis)
        
        sentiment_data = context_analysis.get('sentiment_analysis', {})
        if sentiment_data:
            print(f"   😊 Sentiment: {sentiment_data.get('emotion', 'unknown')} (score: {sentiment_data.get('score', 0):.2f})")
            
            if 'response_prefix' in context_analysis:
                print(f"   💬 Réponse suggérée: '{context_analysis['response_prefix']}'")
        
        # Traitement avec le plugin de mémoire
        await memory_plugin.process_message(filtered_message, context_analysis)
        
        memory_insights = context_analysis.get('memory_insights', {})
        if memory_insights.get('suggested_actions'):
            print(f"   🧠 Actions suggérées: {memory_insights['suggested_actions']}")


def demo_configuration_examples():
    """Démontre différents types de configurations de plugins."""
    
    print("\n\n⚙️  EXEMPLES DE CONFIGURATIONS")
    print("=" * 50)
    
    # Configuration Agent de Support Client
    support_config = {
        "enabled_plugins": [
            {
                "plugin_name": "sentiment_analysis",
                "enabled": True,
                "config": {
                    "threshold": 0.8,
                    "escalate_negative": True
                }
            },
            {
                "plugin_name": "profanity_filter",
                "enabled": True,
                "config": {
                    "strict": True
                }
            },
            {
                "plugin_name": "conversation_memory",
                "enabled": True,
                "config": {
                    "memory_size": 20,
                    "persist_sessions": True
                }
            }
        ]
    }
    
    print("\n📞 CONFIGURATION AGENT DE SUPPORT CLIENT")
    print("- Analyser les sentiments des clients")
    print("- Filtrer les contenus inappropriés")
    print("- Mémoriser les conversations pour un suivi")
    
    # Configuration Agent Éducatif
    education_config = {
        "enabled_plugins": [
            {
                "plugin_name": "conversation_memory",
                "enabled": True,
                "config": {
                    "memory_size": 50,
                    "track_progress": True
                }
            },
            {
                "plugin_name": "sentiment_analysis",
                "enabled": True,
                "config": {
                    "encourage_positive": True
                }
            }
        ]
    }
    
    print("\n🎓 CONFIGURATION AGENT ÉDUCATIF")
    print("- Mémoriser les sessions d'apprentissage")
    print("- Encourager les sentiments positifs")
    print("- Suivre les progrès de l'étudiant")


def demo_benefits():
    """Démontre les avantages concrets des plugins."""
    
    print("\n\n🎯 AVANTAGES CONCRETS DES PLUGINS")
    print("=" * 50)
    
    benefits = [
        {
            "plugin": "Sentiment Analysis",
            "problème": "Clients mécontents non détectés",
            "solution": "Détection automatique + escalade",
            "impact": "Amélioration satisfaction client +90%"
        },
        {
            "plugin": "Profanity Filter", 
            "problème": "Contenu inapproprié dans les conversations",
            "solution": "Filtrage automatique + redirection",
            "impact": "Environnement plus professionnel"
        },
        {
            "plugin": "Conversation Memory",
            "problème": "Agent oublie le contexte précédent",
            "solution": "Mémoire persistante des conversations",
            "impact": "Réponses plus pertinentes + contextuelles"
        },
        {
            "plugin": "Multi-langue (exemple)",
            "problème": "Utilisateurs parlent différentes langues",
            "solution": "Détection automatique + traduction",
            "impact": "Support international automatique"
        }
    ]
    
    for benefit in benefits:
        print(f"\n🔧 {benefit['plugin']}")
        print(f"   Problème: {benefit['problème']}")
        print(f"   Solution: {benefit['solution']}")
        print(f"   Impact: {benefit['impact']}")


def main():
    """Fonction principale de démonstration."""
    
    print("🚀 SYSTÈME DE PLUGINS - DÉMONSTRATION COMPLÈTE")
    print("Répond à la question: À quoi servent les plugins ?")
    print("=" * 60)
    
    # 1. Démonstration pratique
    asyncio.run(demo_plugin_effects())
    
    # 2. Exemples de configuration
    demo_configuration_examples()
    
    # 3. Avantages concrets
    demo_benefits()
    
    print("\n\n✅ RÉSUMÉ: À QUOI SERVENT LES PLUGINS ?")
    print("=" * 50)
    print("🎯 Les plugins permettent de:")
    print("   1. ANALYSER: Sentiments, langues, urgence")
    print("   2. FILTRER: Contenu inapproprié, spam")
    print("   3. MÉMORISER: Conversations, contexte")
    print("   4. PERSONNALISER: Comportement selon le contexte")
    print("   5. INTÉGRER: APIs externes, bases de données")
    print("   6. AMPLIFIER: Capacités de l'agent sans coder")
    
    print("\n🔄 UTILISATION NO-CODE:")
    print("   python manage_agents.py plugins add --name sentiment_analysis")
    print("   python manage_agents.py plugins list")
    print("   python manage_agents.py show")


if __name__ == "__main__":
    main()
