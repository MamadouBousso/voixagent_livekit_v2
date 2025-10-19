#!/usr/bin/env python3
"""
Script CLI pour gérer les agents sans coder
Permet de changer facilement de providers STT, TTS, LLM et d'ajouter des plugins
"""

import sys
import json
import os
import argparse
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from core.dynamic_provider_manager import DynamicProviderManager, ProviderConfig, PluginConfig


class AgentConfigCLI:
    """CLI pour la gestion des configurations d'agent"""
    
    def __init__(self):
        self.manager = DynamicProviderManager()
    
    def show_current_config(self):
        """Affiche la configuration actuelle"""
        config = self.manager.get_config()
        
        print("🔧 Configuration actuelle:")
        print("=" * 50)
        
        print(f"📝 Instructions: {config.instructions[:100]}...")
        print()
        
        print("🤖 Providers:")
        print(f"  LLM: {config.llm.provider_name}/{config.llm.model}")
        print(f"  STT: {config.stt.provider_name}/{config.stt.model}")
        print(f"  TTS: {config.tts.provider_name}/{config.tts.model} (voix: {config.tts.voice_id})")
        print(f"  VAD: {config.vad.provider_name}/{config.vad.model}")
        print()
        
        print("🔌 Plugins actifs:")
        for plugin in config.enabled_plugins:
            status = "✅" if plugin.enabled else "❌"
            print(f"  {status} {plugin.plugin_name}")
        
        print()
        print("⚙️  Options:")
        print(f"  Barge-in: {'Activé' if config.enable_barge_in else 'Désactivé'}")
        print(f"  Métriques: {'Activées' if config.enable_metrics else 'Désactivées'}")
    
    def list_providers(self):
        """Liste les providers disponibles"""
        providers = self.manager.list_available_providers()
        
        print("📋 Providers disponibles:")
        print("=" * 40)
        
        for provider_type, provider_list in providers.items():
            print(f"\n{provider_type.upper()}:")
            for provider in provider_list:
                print(f"  • {provider}")
    
    def change_provider(self, provider_type: str, provider_name: str, model: str, **kwargs):
        """Change un provider"""
        try:
            # Créer la nouvelle configuration
            new_config = ProviderConfig(
                provider_name=provider_name,
                model=model,
                **kwargs
            )
            
            # Mettre à jour
            self.manager.update_provider(provider_type, new_config)
            print(f"✅ Provider {provider_type} changé vers {provider_name}/{model}")
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def list_plugins(self):
        """Liste les plugins disponibles"""
        plugins = self.manager.list_available_plugins()
        
        print("🔌 Plugins disponibles:")
        print("=" * 30)
        for plugin in plugins:
            print(f"  • {plugin}")
        
        config = self.manager.get_config()
        print("\n📋 Plugins actuellement actifs:")
        for plugin in config.enabled_plugins:
            status = "✅" if plugin.enabled else "❌"
            print(f"  {status} {plugin.plugin_name}")
    
    def add_plugin(self, plugin_name: str, enabled: bool = True, config_file: str = None):
        """Ajoute un plugin"""
        plugin_config = {"plugin_name": plugin_name, "enabled": enabled}
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                plugin_config["config"] = json.load(f)
        
        plugin_cfg = PluginConfig(**plugin_config)
        self.manager.add_plugin(plugin_cfg)
        print(f"✅ Plugin {plugin_name} ajouté")
    
    def remove_plugin(self, plugin_name: str):
        """Supprime un plugin"""
        self.manager.remove_plugin(plugin_name)
        print(f"✅ Plugin {plugin_name} supprimé")
    
    def create_template(self, output_file: str):
        """Crée un fichier de configuration template"""
        self.manager.create_config_template(output_file)
        print(f"✅ Template créé: {output_file}")
    
    def interactive_setup(self):
        """Configuration interactive"""
        print("🚀 Configuration interactive de l'agent")
        print("=" * 40)
        
        # Instructions
        instructions = input("📝 Instructions de l'agent (Enter pour garder actuel): ").strip()
        if instructions:
            self.manager._config.instructions = instructions
        
        # LLM
        print("\n🤖 Configuration LLM:")
        llm_provider = input("Provider (openai, anthropic): ").strip() or "openai"
        llm_model = input(f"Modèle pour {llm_provider}: ").strip() or "gpt-4o-mini"
        
        # STT
        print("\n🎤 Configuration STT:")
        stt_provider = input("Provider (openai, google): ").strip() or "openai"
        stt_model = input(f"Modèle pour {stt_provider}: ").strip() or "whisper-1"
        
        # TTS
        print("\n🔊 Configuration TTS:")
        tts_provider = input("Provider (openai, elevenlabs): ").strip() or "openai"
        tts_model = input(f"Modèle pour {tts_provider}: ").strip() or "tts-1"
        tts_voice = input("Voix (alloy, echo, fable, etc.): ").strip() or "alloy"
        
        # Appliquer les changements
        self.change_provider('llm', llm_provider, llm_model)
        self.change_provider('stt', stt_provider, stt_model)
        self.change_provider('tts', tts_provider, tts_model, voice_id=tts_voice)
        
        print("\n✅ Configuration mise à jour!")
        self.show_current_config()


def main():
    """Fonction principale du CLI"""
    parser = argparse.ArgumentParser(description="Gestionnaire d'agent vocal - Configuration NO-CODE")
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande show
    subparsers.add_parser('show', help='Afficher la configuration actuelle')
    
    # Commande list-providers
    subparsers.add_parser('list-providers', help='Lister les providers disponibles')
    
    # Commande change-llm
    llm_parser = subparsers.add_parser('change-llm', help='Changer le provider LLM')
    llm_parser.add_argument('provider', help='Nom du provider (ex: openai)')
    llm_parser.add_argument('model', help='Modèle (ex: gpt-4o-mini)')
    llm_parser.add_argument('--api-key', help='Clé API')
    llm_parser.add_argument('--temperature', type=float, help='Température (0.0-1.0)')
    
    # Commande change-stt
    stt_parser = subparsers.add_parser('change-stt', help='Changer le provider STT')
    stt_parser.add_argument('provider', help='Nom du provider (ex: openai)')
    stt_parser.add_argument('model', help='Modèle (ex: whisper-1)')
    stt_parser.add_argument('--api-key', help='Clé API')
    
    # Commande change-tts
    tts_parser = subparsers.add_parser('change-tts', help='Changer le provider TTS')
    tts_parser.add_argument('provider', help='Nom du provider (ex: openai)')
    tts_parser.add_argument('model', help='Modèle (ex: tts-1)')
    tts_parser.add_argument('--voice', help='Voix (ex: alloy)')
    tts_parser.add_argument('--api-key', help='Clé API')
    
    # Commande plugins
    plugins_parser = subparsers.add_parser('plugins', help='Gérer les plugins')
    plugins_parser.add_argument('action', choices=['list', 'add', 'remove'], help='Action sur les plugins')
    plugins_parser.add_argument('--name', help='Nom du plugin')
    plugins_parser.add_argument('--config', help='Fichier de config du plugin')
    
    # Commande template
    template_parser = subparsers.add_parser('template', help='Créer un template de configuration')
    template_parser.add_argument('output', help='Fichier de sortie')
    
    # Commande interactive
    subparsers.add_parser('interactive', help='Configuration interactive')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AgentConfigCLI()
    
    try:
        if args.command == 'show':
            cli.show_current_config()
        
        elif args.command == 'list-providers':
            cli.list_providers()
        
        elif args.command == 'change-llm':
            kwargs = {}
            if args.api_key:
                kwargs['api_key'] = args.api_key
            if args.temperature:
                kwargs['temperature'] = args.temperature
            cli.change_provider('llm', args.provider, args.model, **kwargs)
        
        elif args.command == 'change-stt':
            kwargs = {}
            if args.api_key:
                kwargs['api_key'] = args.api_key
            cli.change_provider('stt', args.provider, args.model, **kwargs)
        
        elif args.command == 'change-tts':
            kwargs = {}
            if args.api_key:
                kwargs['api_key'] = args.api_key
            if args.voice:
                kwargs['voice_id'] = args.voice
            cli.change_provider('tts', args.provider, args.model, **kwargs)
        
        elif args.command == 'plugins':
            if args.action == 'list':
                cli.list_plugins()
            elif args.action == 'add':
                if not args.name:
                    print("❌ Nom du plugin requis avec --name")
                    return
                cli.add_plugin(args.name, config_file=args.config)
            elif args.action == 'remove':
                if not args.name:
                    print("❌ Nom du plugin requis avec --name")
                    return
                cli.remove_plugin(args.name)
        
        elif args.command == 'template':
            cli.create_template(args.output)
        
        elif args.command == 'interactive':
            cli.interactive_setup()
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
