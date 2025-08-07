# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
et ce projet adhère au [Versioning Sémantique](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-07

### Ajouté
- Première version de l'intégration Kids Tasks Manager
- Gestion complète des profils enfants avec système de points/niveaux
- Système de tâches récurrentes avec catégorisation
- Validation parentale optionnelle avec notifications
- Système de récompenses personnalisable
- Services complets pour la gestion via Home Assistant
- Support multilingue (français/anglais)
- Dashboards dédiés parents et enfants
- Entités automatiques : capteurs, boutons, sélecteurs
- Configuration flow intégrée
- Stockage persistant des données
- Événements système pour automatisations
- Support HACS complet
- Documentation complète

### Fonctionnalités
- `kids_tasks.add_child` - Ajouter un enfant
- `kids_tasks.add_task` - Créer une tâche récurrente  
- `kids_tasks.add_reward` - Définir une récompense
- `kids_tasks.complete_task` - Marquer une tâche terminée
- `kids_tasks.validate_task` - Valider une tâche (parents)
- `kids_tasks.claim_reward` - Réclamer une récompense
- `kids_tasks.reset_task` - Remettre une tâche à zéro

### Entités créées
- Capteurs de points, niveaux, tâches complétées par enfant
- Capteurs globaux (tâches en attente, total journalier)
- Boutons de completion et validation des tâches
- Sélecteurs de statut des tâches
- Contrôles numériques pour les points des tâches

[1.0.0]: https://github.com/votre-username/kids-tasks-ha/releases/tag/v1.0.0