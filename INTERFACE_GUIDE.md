# Guide des cartes Lovelace — Kids Tasks Manager

4 cartes indépendantes déclarées dans `www/kids_tasks/kids-tasks-card.js`.

---

## Installation

### 1. Copier le fichier JS

```bash
python install.py          # détection automatique
# ou
python install.py /path/to/homeassistant/config
```

Le script copie `www/kids_tasks/kids-tasks-card.js` vers `config/www/kids_tasks/`.

### 2. Déclarer la ressource Lovelace

**Via l'UI** : Paramètres → Tableaux de bord → Ressources → Ajouter
- URL : `/local/kids_tasks/kids-tasks-card.js`
- Type : Module JavaScript

**Via YAML** :
```yaml
lovelace:
  resources:
    - url: /local/kids_tasks/kids-tasks-card.js
      type: module
```

### 3. Redémarrer Home Assistant

---

## Carte 1 — Enfant (`kids-tasks-child-summary-card`)

Vue compacte d'un enfant : avatar, niveau, barre XP, tâches du jour, bouton de validation rapide.

### Configuration YAML

```yaml
type: kids-tasks-child-summary-card
entity: sensor.kidtasks_leo_points   # capteur de points de l'enfant (requis)
```

### Propriétés

| Propriété | Requis | Description |
|-----------|--------|-------------|
| `entity`  | ✅ | `sensor.kidtasks_{nom}_points` de l'enfant |

### Fonctionnement

- Affiche l'avatar, le nom, le niveau et les pièces de l'enfant
- Barre de progression XP vers le niveau suivant
- Chips des tâches du jour avec statut coloré (✅ validé / ⏳ en attente / ⬜ à faire)
- Bouton « N à valider » si des tâches attendent — valide toutes en 1 tap
- Le dégradé de couleur suit `card_gradient_start` / `card_gradient_end` définis sur l'enfant

### Conseil : grille multi-enfants

```yaml
type: grid
columns: 2
cards:
  - type: kids-tasks-child-summary-card
    entity: sensor.kidtasks_leo_points
  - type: kids-tasks-child-summary-card
    entity: sensor.kidtasks_emma_points
```

---

## Carte 2 — Validation parentale (`kids-tasks-validation-card`)

Liste uniquement les tâches `pending_validation`. Actions Valider / Rejeter directement sur chaque ligne.

### Configuration YAML

```yaml
type: kids-tasks-validation-card
# entity optionnel — détecté automatiquement
```

### Propriétés

| Propriété | Requis | Description |
|-----------|--------|-------------|
| `entity`  | ❌ | Défaut : `sensor.kidtasks_pending_validations` |

### Fonctionnement

- Affiche icône de catégorie + nom de la tâche + enfant assigné + points
- Boutons **✓ Valider** (vert) et **✗ Rejeter** (rouge) inline sur chaque ligne
- Badge de compteur dans le header
- Affiche « ✅ Tout est validé » si la queue est vide

---

## Carte 3 — Liste de tâches (`kids-tasks-task-list-card`)

Vue complète avec filtres par fréquence et statut. Pour dashboard parent.

### Configuration YAML

```yaml
type: kids-tasks-task-list-card
# entity optionnel — détecté automatiquement
```

### Propriétés

| Propriété | Requis | Description |
|-----------|--------|-------------|
| `entity`  | ❌ | Défaut : `sensor.kidtasks_all_tasks_list` |

### Fonctionnement

- Chips de filtre : **Tous** / **Quotidien** / **Hebdo** / **⏳ En attente** / **✅ Faits**
- Chaque ligne : point de statut coloré + icône catégorie + nom + enfant assigné + badge points
- Boutons Valider / Rejeter uniquement sur les tâches `pending_validation`

---

## Carte 4 — Récompenses (`kids-tasks-reward-card`)

Catalogue visuel en grille. Vue enfant (avec échange) ou vue admin (lecture seule).

### Configuration YAML

**Vue admin (sans échange)** :
```yaml
type: kids-tasks-reward-card
```

**Vue enfant (avec échange)** :
```yaml
type: kids-tasks-reward-card
child_entity: sensor.kidtasks_emma_points
```

### Propriétés

| Propriété       | Requis | Description |
|-----------------|--------|-------------|
| `entity`        | ❌ | Défaut : `sensor.kidtasks_all_rewards_list` |
| `child_entity`  | ❌ | `sensor.kidtasks_{nom}_points` — active le bouton Échanger |

### Fonctionnement

- Grille responsive de tuiles (icône + nom + description + coût en points)
- Bouton **Échanger** actif si l'enfant a assez de points, grisé sinon
- Filtre par catégorie (🎉 fun, 📱 écran, 🚗 sortie, 👑 privilège, 🧸 jouet, 🍭 friandise)
- Quantité restante affichée si `limited_quantity` défini

---

## Exemple de dashboard complet

```yaml
title: Kids Tasks
views:
  - title: Famille
    cards:
      - type: kids-tasks-validation-card

      - type: grid
        columns: 2
        cards:
          - type: kids-tasks-child-summary-card
            entity: sensor.kidtasks_leo_points
          - type: kids-tasks-child-summary-card
            entity: sensor.kidtasks_emma_points

  - title: Tâches
    cards:
      - type: kids-tasks-task-list-card

  - title: Récompenses — Léo
    cards:
      - type: kids-tasks-reward-card
        child_entity: sensor.kidtasks_leo_points

  - title: Récompenses — Emma
    cards:
      - type: kids-tasks-reward-card
        child_entity: sensor.kidtasks_emma_points
```

---

## Dépannage

| Symptôme | Cause probable | Solution |
|----------|---------------|----------|
| Carte non reconnue | Ressource JS non chargée | Vérifier l'URL dans Ressources Lovelace |
| « Entité introuvable » | Intégration non configurée | Ajouter l'intégration Kids Tasks dans HA |
| Bouton Échanger toujours grisé | `child_entity` manquant ou mauvais nom | Vérifier l'entity_id du capteur de points |
| Tâches non affichées | Aucune tâche créée | Créer des tâches via `kids_tasks.add_task` |
