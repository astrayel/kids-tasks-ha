# Installation

## Prérequis

- Home Assistant 2024.1.0 ou plus récent
- HACS installé (pour l'installation via HACS)

## Installation via HACS (Recommandé)

### Étape 1 : Ajouter le repository

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur "Intégrations" 
3. Cliquez sur les 3 points en haut à droite
4. Sélectionnez "Dépôts personnalisés"
5. Ajoutez l'URL : `https://github.com/votre-username/kids-tasks-ha`
6. Sélectionnez "Intégration" comme catégorie
7. Cliquez sur "Ajouter"

### Étape 2 : Installer l'intégration

1. Recherchez "Kids Tasks Manager" dans HACS
2. Cliquez sur "Télécharger"
3. Redémarrez Home Assistant

### Étape 3 : Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **"+ Ajouter une intégration"**
3. Recherchez **"Kids Tasks Manager"**
4. Suivez l'assistant de configuration

## Installation Manuelle

### Étape 1 : Télécharger les fichiers

1. Téléchargez la dernière release depuis [GitHub](https://github.com/votre-username/kids-tasks-ha/releases)
2. Extrayez l'archive

### Étape 2 : Copier les fichiers

1. Copiez le dossier `custom_components/kids_tasks` vers `config/custom_components/kids_tasks`
2. Votre structure devrait ressembler à :
config/
├── custom_components/
│   └── kids_tasks/
│       ├── init.py
│       ├── const.py
│       └── ... (autres fichiers)
└── configuration.yaml

### Étape 3 : Redémarrer et configurer

1. Redémarrez Home Assistant
2. Suivez les étapes de configuration ci-dessus

## Vérification de l'installation

Après l'installation et la configuration, vous devriez voir :

- Une nouvelle intégration "Kids Tasks Manager" dans vos intégrations
- De nouvelles entités commençant par `kids_tasks.`
- Les services disponibles dans Outils de développement → Services

## Dépannage

### L'intégration n'apparaît pas

1. Vérifiez que tous les fichiers sont dans le bon dossier
2. Redémarrez Home Assistant complètement
3. Vérifiez les logs dans Configuration → Logs

### Erreurs de configuration

1. Supprimez l'intégration depuis Configuration → Intégrations
2. Redémarrez Home Assistant
3. Réessayez la configuration

### Logs de débogage

Pour activer les logs détaillés, ajoutez dans `configuration.yaml` :

```yaml
logger:
  default: info
  logs:
    custom_components.kids_tasks: debug
### `.gitignore`

Byte-compiled / optimized / DLL files
pycache/
*.py[cod]
*$py.class
IDE
.vscode/
.idea/
*.swp
*.swo
OS
.DS_Store
Thumbs.db
Testing
.pytest_cache/
.coverage
htmlcov/
Build artifacts
build/
dist/
*.egg-info/
Home Assistant
*.log
.HA_VERSION
.uuid
Temporary files
*.tmp
*~

---

## 🚀 Instructions pour créer le repository GitHub

### 1. Créer le repository
```bash
# Créer un nouveau repository privé sur GitHub nommé : kids-tasks-ha