# 📦 Installation Kids Tasks Manager

## Prérequis

- Home Assistant 2024.1.0 ou plus récent
- HACS installé (pour installation recommandée)

## Installation via HACS (Recommandé)

### Étape 1 : Ajouter le repository

1. Ouvrez HACS dans Home Assistant
2. Allez dans **"Intégrations"**
3. Cliquez sur **⋮** (menu) en haut à droite
4. Sélectionnez **"Dépôts personnalisés"**
5. Ajoutez l'URL : `https://github.com/astrayel/kids-tasks-ha`
6. Sélectionnez **"Intégration"** comme catégorie
7. Cliquez sur **"Ajouter"**

### Étape 2 : Installer l'intégration

1. Recherchez **"Kids Tasks Manager"** dans HACS
2. Cliquez sur **"Télécharger"**
3. Redémarrez Home Assistant

### Étape 3 : Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **"+ Ajouter une intégration"**
3. Recherchez **"Kids Tasks Manager"**
4. Suivez l'assistant de configuration

## Installation Manuelle

### Étape 1 : Télécharger

1. Téléchargez la dernière version depuis [GitHub Releases](https://github.com/astrayel/kids-tasks-ha/releases)
2. Extrayez l'archive

### Étape 2 : Installation

1. Copiez le dossier `custom_components/kids_tasks` vers `config/custom_components/kids_tasks`
2. Votre structure devrait être :
```
config/
├── custom_components/
│   └── kids_tasks/
│       ├── __init__.py
│       ├── manifest.json
│       └── ... (autres fichiers)
└── configuration.yaml
```

### Étape 3 : Redémarrage et configuration

1. Redémarrez Home Assistant
2. Ajoutez l'intégration via l'interface

## Vérification de l'installation

Après installation, vérifiez :

### ✅ Intégration présente
- Visible dans **Configuration** → **Intégrations**
- Statut "Configuré" avec icône verte

### ✅ Services disponibles
1. Allez dans **Outils de développement** → **Services**
2. Recherchez les services commençant par `kids_tasks.`
3. Vous devriez voir :
   - `kids_tasks.add_child`
   - `kids_tasks.add_task`
   - `kids_tasks.add_reward`
   - Et autres...

### ✅ Entités créées
1. Allez dans **Outils de développement** → **États**
2. Filtrez par `kids_tasks`
3. Les entités apparaîtront après avoir ajouté des enfants/tâches

## Dépannage

### L'intégration n'apparaît pas

**Problème** : Kids Tasks Manager n'est pas visible dans la liste des intégrations

**Solutions** :
1. Vérifiez la structure des fichiers :
   ```bash
   ls -la config/custom_components/kids_tasks/
   # Doit contenir : __init__.py, manifest.json, etc.
   ```
2. Consultez les logs : **Configuration** → **Logs**
3. Redémarrez complètement Home Assistant
4. Vérifiez que vous avez bien Home Assistant 2024.1.0+

### Erreurs au démarrage

**Problème** : Erreurs dans les logs au démarrage de HA

**Solutions** :
1. Consultez le fichier `home-assistant.log`
2. Vérifiez que tous les fichiers Python sont présents
3. Assurez-vous qu'aucun fichier n'est corrompu

### Services non disponibles

**Problème** : Les services `kids_tasks.*` n'apparaissent pas

**Solutions** :
1. Vérifiez que l'intégration est configurée (pas seulement installée)
2. Redémarrez Home Assistant après configuration
3. Vérifiez le fichier `services.yaml` dans le dossier de l'intégration

### Entités manquantes

**Problème** : Aucune entité `kids_tasks.*` visible

**Cause** : Normal après installation - les entités sont créées dynamiquement

**Solution** : 
1. Ajoutez d'abord un enfant via le service `kids_tasks.add_child`
2. Ajoutez des tâches via `kids_tasks.add_task`
3. Les entités apparaîtront automatiquement

## Mise à jour

### Via HACS
1. Allez dans **HACS** → **Intégrations**
2. Trouvez **Kids Tasks Manager**
3. Cliquez sur **"Mettre à jour"** si disponible
4. Redémarrez Home Assistant

### Manuelle
1. Sauvegardez vos données (optionnel)
2. Remplacez les fichiers dans `custom_components/kids_tasks/`
3. Redémarrez Home Assistant

## Désinstallation

### Complète
1. Supprimez l'intégration depuis **Configuration** → **Intégrations**
2. Supprimez le dossier `custom_components/kids_tasks/`
3. Redémarrez Home Assistant

### Conservation des données
Les données sont stockées dans le fichier de stockage HA. Pour les conserver :
1. Sauvegardez via le service `kids_tasks.backup_data`
2. Procédez à la désinstallation
3. Restaurez après réinstallation avec `kids_tasks.restore_data`

## Support d'installation

Si vous rencontrez des problèmes :

1. **GitHub Issues** : [Signaler un problème](https://github.com/astrayel/kids-tasks-ha/issues)
2. **Discussions** : [Forum de discussion](https://github.com/astrayel/kids-tasks-ha/discussions)
3. **Communauté HA** : [Community Forum](https://community.home-assistant.io/)

Incluez toujours dans votre rapport :
- Version de Home Assistant
- Méthode d'installation (HACS/manuelle)
- Logs d'erreur complets
- Étapes pour reproduire le problème
