📦 Installation Kids Tasks Manager
Prérequis

Home Assistant 2024.1.0 ou plus récent
HACS installé (pour installation recommandée)

Installation via HACS (Recommandé)
Étape 1 : Ajouter le repository

Ouvrez HACS dans Home Assistant
Allez dans "Intégrations"
Cliquez sur ⋮ (menu) en haut à droite
Sélectionnez "Dépôts personnalisés"
Ajoutez l'URL : https://github.com/astrayel/kids-tasks-ha
Sélectionnez "Intégration" comme catégorie
Cliquez sur "Ajouter"

Étape 2 : Installer l'intégration

Recherchez "Kids Tasks Manager" dans HACS
Cliquez sur "Télécharger"
Redémarrez Home Assistant

Étape 3 : Configuration

Allez dans Configuration → Intégrations
Cliquez sur "+ Ajouter une intégration"
Recherchez "Kids Tasks Manager"
Suivez l'assistant de configuration

Installation Manuelle
Étape 1 : Télécharger

Téléchargez la dernière version depuis GitHub Releases
Extrayez l'archive

Étape 2 : Installation

Copiez le dossier custom_components/kids_tasks vers config/custom_components/kids_tasks
Votre structure devrait être :

config/
├── custom_components/
│   └── kids_tasks/
│       ├── __init__.py
│       ├── manifest.json
│       └── ... (autres fichiers)
└── configuration.yaml
Étape 3 : Redémarrage et configuration

Redémarrez Home Assistant
Ajoutez l'intégration via l'interface

Vérification
Après installation, vérifiez :

Intégration visible dans Configuration → Intégrations
Services disponibles dans Outils de développement → Services
Entités créées commençant par kids_tasks.

Dépannage
L'intégration n'apparaît pas

Vérifiez la structure des fichiers
Consultez les logs : Configuration → Logs
Redémarrez complètement Home Assistant

Erreurs de services

Vérifiez que tous les fichiers sont présents
Consultez home-assistant.log
Désinstallez et réinstallez si nécessaire
