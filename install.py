#!/usr/bin/env python3
"""Script d'installation automatique pour Kids Tasks Manager."""
import shutil
import sys
from pathlib import Path


def find_hass_config():
    """Trouve le répertoire de configuration Home Assistant."""
    possible_paths = [
        Path.home() / ".homeassistant",
        Path("/config"),
        Path.home() / "homeassistant",
        Path("/usr/share/hassio/homeassistant"),
    ]
    for path in possible_paths:
        if path.exists() and (path / "configuration.yaml").exists():
            return path
    return None


def install_integration(hass_config_dir):
    """Copie custom_components/kids_tasks/ vers le répertoire HA."""
    source_dir = Path(__file__).parent / "custom_components" / "kids_tasks"
    target_dir = hass_config_dir / "custom_components" / "kids_tasks"

    print(f"Installation de l'integration...")
    print(f"   Source: {source_dir}")
    print(f"   Destination: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)

    for file_path in source_dir.glob("*"):
        if file_path.is_file() and file_path.suffix in [".py", ".json", ".yaml"]:
            shutil.copy2(file_path, target_dir)
            print(f"   Copie {file_path.name}")

    for sub in source_dir.iterdir():
        if sub.is_dir() and not sub.name.startswith("__"):
            shutil.copytree(sub, target_dir / sub.name, dirs_exist_ok=True)
            print(f"   Copie {sub.name}/")


def main():
    print("Installation Kids Tasks Manager pour Home Assistant")
    print("=" * 60)

    if len(sys.argv) > 1:
        hass_config_dir = Path(sys.argv[1])
    else:
        hass_config_dir = find_hass_config()

    if not hass_config_dir:
        print("Repertoire Home Assistant non trouve.")
        print("Utilisez : python install.py /path/to/config")
        sys.exit(1)

    print(f"Home Assistant detecte : {hass_config_dir}")

    try:
        install_integration(hass_config_dir)
        print("\nInstallation terminee !")
        print("   1. Redemarrez Home Assistant")
        print("   2. Configurez l'integration dans Parametres -> Integrations")
        print("   3. Installez les cartes Lovelace, dans un depot separe :")
        print("      https://github.com/astrayel/kids-tasks-ha-card")
        print("      (voir INTERFACE_GUIDE.md)")
    except Exception as e:
        print(f"Erreur lors de l'installation : {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
