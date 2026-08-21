# Dashboards

Trois vues, une par usage. Les cartes viennent du dépôt
[kids-tasks-ha-card](https://github.com/astrayel/kids-tasks-ha-card).

## 1. Vue enfant — sur son propre compte

Une carte, plein écran, rien d'autre. À dupliquer par enfant en changeant
`child_id`.

```yaml
views:
  - title: Mes tâches
    path: mes-taches
    type: panel
    visible:
      - user: <user_id de l'enfant>
    cards:
      - type: custom:kids-tasks-child-card
        child_id: <child_id>
```

Le `child_id` se lit dans les attributs du capteur de points de l'enfant
(Outils de développement → États → `sensor.kidtasks_<prenom>_points`).

## 2. Vue tablette — appareil partagé

Le sélecteur de profil est libre, sans code : la validation parentale filtre
derrière, et un code partagé entre enfants qui se regardent taper n'apporte
rien.

Le plus simple est une vue par enfant, en sous-onglets, sur le dashboard de la
tablette :

```yaml
views:
  - title: Léo
    path: leo
    type: panel
    icon: mdi:account
    cards:
      - type: custom:kids-tasks-child-card
        child_id: <child_id de Léo>

  - title: Emma
    path: emma
    type: panel
    icon: mdi:account
    cards:
      - type: custom:kids-tasks-child-card
        child_id: <child_id d'Emma>

  - title: Nina
    path: nina
    type: panel
    icon: mdi:account
    cards:
      - type: custom:kids-tasks-child-card
        child_id: <child_id de Nina>
```

Le compte utilisé par la tablette doit être déclaré dans **Paramètres →
Appareils et services → Kids Tasks → Configurer → Appareils partagés**, sans
quoi il n'aura aucun droit d'écriture. Voir [permissions.md](permissions.md).

Les cartes Supervisor et Manager n'ont rien à faire sur ce dashboard : elles
s'affichent de toute façon en « réservé aux parents » sur un compte
non-administrateur.

## 3. Vue parent

```yaml
views:
  - title: Kids Tasks
    path: kids-tasks
    visible:
      - user: <user_id du parent 1>
      - user: <user_id du parent 2>
    cards:
      - type: custom:kids-tasks-supervisor
        title: Validation

      - type: grid
        columns: 3
        square: false
        cards:
          - type: custom:kids-tasks-child-card
            child_id: <child_id de Léo>
          - type: custom:kids-tasks-child-card
            child_id: <child_id d'Emma>
          - type: custom:kids-tasks-child-card
            child_id: <child_id de Nina>

  - title: Administration
    path: kids-tasks-admin
    visible:
      - user: <user_id du parent 1>
    cards:
      - type: custom:kids-tasks-manager
```

`visible:` masque l'onglet, ce n'est pas une protection : la vraie garde est
côté serveur.

## Alléger la base de données

Chaque capteur est réécrit à chaque cycle de rafraîchissement (60 s). Les
capteurs de liste et d'historique portent des attributs volumineux dont
l'historique n'a aucun intérêt — seules les valeurs de points et de niveau
méritent d'être conservées, et les statistiques horaires s'en chargent déjà.

Dans `configuration.yaml` :

```yaml
recorder:
  exclude:
    entities:
      - sensor.kidtasks_all_children_list
    entity_globs:
      - sensor.kidtasks_*_points_history
      - sensor.kidtasks_task_*
      - sensor.kidtasks_reward_*
      - switch.kidtasks_*
```

Ce qui reste enregistré : les points, les niveaux, les tâches faites du jour et
les compteurs globaux — de quoi tracer des courbes de progression.
