### `info.md`
```markdown
# Kids Tasks Manager

Une intégration Home Assistant complète pour gérer les tâches récurrentes de vos enfants avec un système de gamification.

## Fonctionnalités principales

### 🧸 Gestion des Enfants
- Profils individuels avec avatars
- Système de points et de niveaux
- Statistiques personnalisées
- Progression visuelle

### ✅ Système de Tâches
- Tâches récurrentes (quotidiennes, hebdomadaires, mensuelles)
- Catégorisation intelligente (chambre, cuisine, devoirs, etc.)
- Attribution flexible des points
- Suivi automatique des complétions

### 🎁 Récompenses
- Catalogue personnalisable de récompenses
- Système de coût en points
- Récompenses à quantité limitée
- Historique des réclamations

### 👨‍👩‍👧‍👦 Contrôle Parental
- Mode validation activable/désactivable
- Notifications en temps réel
- Interface de validation simple
- Tableau de bord dédié

### 📊 Dashboards
- Dashboard parent avec vue d'ensemble
- Dashboard individuel par enfant
- Statistiques en temps réel
- Interface mobile optimisée

## Installation

Cette intégration peut être installée via HACS ou manuellement.

**Via HACS :**
1. Ajoutez ce repository comme source personnalisée dans HACS
2. Recherchez "Kids Tasks Manager" 
3. Installez et redémarrez Home Assistant

**Installation manuelle :**
1. Copiez le dossier `custom_components/kids_tasks` dans votre configuration
2. Redémarrez Home Assistant
3. Ajoutez l'intégration via l'interface

## Configuration

Après l'installation, allez dans Configuration → Intégrations et ajoutez "Kids Tasks Manager".

L'assistant de configuration vous guidera pour :
- Configurer les paramètres généraux
- Activer/désactiver la validation parentale  
- Configurer les notifications

## Utilisation

Une fois configuré, utilisez les services pour :
- Ajouter des enfants : `kids_tasks.add_child`
- Créer des tâches : `kids_tasks.add_task` 
- Définir des récompenses : `kids_tasks.add_reward`
- Gérer les completions et validations

L'intégration créera automatiquement toutes les entités nécessaires (capteurs, boutons, sélecteurs) pour un contrôle complet.