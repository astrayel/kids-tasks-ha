#!/usr/bin/env python3
"""
Script d'installation automatique pour Kids Tasks Manager
Copie les fichiers nécessaires dans les bons répertoires Home Assistant
"""
import os
import shutil
import sys
from pathlib import Path

def find_hass_config():
    """Trouve le répertoire de configuration Home Assistant"""
    possible_paths = [
        Path.home() / ".homeassistant",
        Path("/config"),  # Docker
        Path.home() / "homeassistant",
        Path("/usr/share/hassio/homeassistant"),
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "configuration.yaml").exists():
            return path
    
    return None

def install_integration(hass_config_dir):
    """Installe l'intégration dans Home Assistant"""
    
    source_dir = Path(__file__).parent / "custom_components" / "kids_tasks"
    target_dir = hass_config_dir / "custom_components" / "kids_tasks"
    
    print(f"📦 Installation de l'intégration...")
    print(f"   Source: {source_dir}")
    print(f"   Destination: {target_dir}")
    
    # Créer le répertoire cible
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier tous les fichiers Python et de configuration
    for file_path in source_dir.glob("*"):
        if file_path.suffix in [".py", ".json", ".yaml"]:
            shutil.copy2(file_path, target_dir)
            print(f"   ✅ {file_path.name}")
    
    # Copier les traductions
    if (source_dir / "translations").exists():
        shutil.copytree(
            source_dir / "translations", 
            target_dir / "translations", 
            dirs_exist_ok=True
        )
        print(f"   ✅ translations/")

def install_frontend(hass_config_dir):
    """Installe l'interface frontend"""
    
    source_file = Path(__file__).parent / "custom_components" / "kids_tasks" / "kids-tasks-card.js"
    
    # Essayer plusieurs emplacements possibles
    possible_targets = [
        hass_config_dir / "www" / "kids_tasks" / "kids-tasks-card.js",
        hass_config_dir / "www" / "community" / "kids-tasks-ha" / "kids-tasks-card.js",
    ]
    
    for target_file in possible_targets:
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_file)
        print(f"   ✅ Interface copiée vers: {target_file}")

def update_lovelace_resources(hass_config_dir):
    """Propose la configuration Lovelace"""
    
    print("\n🎨 Configuration de l'interface:")
    print("   Ajoutez cette ressource dans Home Assistant:")
    print("   Configuration → Lovelace Dashboards → Ressources")
    print()
    print("   URL: /local/kids_tasks/kids-tasks-card.js")
    print("   Type: Module JavaScript")
    print()
    print("   Ou ajoutez dans configuration.yaml:")
    print("   lovelace:")
    print("     resources:")
    print("       - url: /local/kids_tasks/kids-tasks-card.js")
    print("         type: module")

def main():
    print("🏠 Installation Kids Tasks Manager pour Home Assistant")
    print("=" * 60)
    
    # Trouver Home Assistant
    if len(sys.argv) > 1:
        hass_config_dir = Path(sys.argv[1])
    else:
        hass_config_dir = find_hass_config()
    
    if not hass_config_dir:
        print("❌ Répertoire Home Assistant non trouvé!")
        print("   Utilisez: python install.py /path/to/config")
        sys.exit(1)
    
    print(f"📍 Home Assistant détecté: {hass_config_dir}")
    
    try:
        # Installer l'intégration
        install_integration(hass_config_dir)
        
        # Installer l'interface
        install_frontend(hass_config_dir)
        
        # Instructions pour Lovelace
        update_lovelace_resources(hass_config_dir)
        
        print("\n🎉 Installation terminée!")
        print("   1. Redémarrez Home Assistant")
        print("   2. Ajoutez la ressource Lovelace")
        print("   3. Configurez l'intégration dans Configuration → Intégrations")
        print("   4. Ajoutez la carte kids-tasks-card à votre dashboard")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()