# ⚙️ Configuration Kids Tasks Manager

## Configuration initiale

### Via l'interface utilisateur

1. **Configuration** → **Intégrations** → **Ajouter une intégration**
2. Recherchez **"Kids Tasks Manager"**
3. Configurez les options de base :
   - **Nom** : Nom de votre installation (ex: "Famille Martin")
   - **Validation parentale** : Activée par défaut
   - **Notifications** : Activées par défaut

## Options de configuration

### Options disponibles

| Option | Description | Défaut | Type |
|--------|-------------|--------|------|
| `validation_required` | Validation parentale obligatoire | `true` | Boolean |
| `notifications_enabled` | Notifications activées | `true` | Boolean |
| `auto_reset_tasks` | Remise à zéro automatique quotidienne | `true` | Boolean |
| `points_multiplier` | Multiplicateur de points global | `1.0` | Float |

### Modification des options

1. **Configuration** → **Intégrations**
2. Trouvez **Kids Tasks Manager**
3. Cliquez sur **"Configurer"**
4. Modifiez les paramètres souhaités
5. Cliquez sur **"Soumettre"**

## Guide de démarrage rapide

### 1. Ajouter des enfants

```yaml
# Service pour ajouter un enfant
service: kids_tasks.add_child
data:
  name: "Emma"
  avatar: "👧"
  initial_points: 0
```

```yaml
# Ajouter plusieurs enfants
service: kids_tasks.add_child
data:
  name: "Lucas"
  avatar: "👦"
```

### 2. Créer des tâches de base

#### Tâches quotidiennes
```yaml
service: kids_tasks.add_task  
data:
  name: "Ranger sa chambre"
  description: "Faire le lit, ranger les jouets, vêtements au panier"
  category: "bedroom"
  points: 15
  frequency: "daily"
  assigned_child_id: "emma_001"
  validation_required: true
```

#### Tâches hebdomadaires
```yaml
service: kids_tasks.add_task
data:
  name: "Sortir les poubelles"
  category: "outdoor" 
  points: 10
  frequency: "weekly"
  assigned_child_id: "lucas_001"
```

#### Devoirs
```yaml
service: kids_tasks.add_task
data:
  name: "Faire les devoirs"
  description: "Terminer tous les devoirs du jour"
  category: "homework"
  points: 20
  frequency: "daily"
  validation_required: true
```

### 3. Définir des récompenses

#### Récompenses d'écran
```yaml
service: kids_tasks.add_reward
data:
  name: "30 min d'écran supplémentaire" 
  description: "Temps d'écran bonus pour tablette/TV"
  cost: 50
  category: "screen_time"
```

#### Sorties
```yaml
service: kids_tasks.add_reward
data:
  name: "Sortie au parc"
  cost: 100
  category: "outing"
  limited_quantity: 2  # Max 2 fois par semaine
```

#### Privilèges
```yaml
service: kids_tasks.add_reward
data:
  name: "Choisir le repas du soir"
  cost: 75
  category: "privilege"
```

## Automatisations recommandées

### Réinitialisation quotidienne

```yaml
# Remet toutes les tâches quotidiennes à "À faire" chaque matin
automation:
  - alias: "Reset tâches quotidiennes"
    description: "Remet les tâches quotidiennes à zéro chaque matin"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: kids_tasks.reset_all_daily_tasks

  - alias: "Reset tâches hebdomadaires" 
    description: "Remet les tâches hebdomadaires à zéro le lundi"
    trigger:
      - platform: time
        at: "06:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: kids_tasks.reset_all_weekly_tasks
```

### Notifications pour parents

```yaml
automation:
  - alias: "Notification tâche terminée"
    description: "Alerte quand un enfant termine une tâche"
    trigger:
      - platform: event
        event_type: kids_tasks_task_completed
    action:
      - service: notify.mobile_app_parent
        data:
          title: "Tâche terminée !"
          message: "{{ trigger.event.data.child_name }} a terminé {{ trigger.event.data.task_name }}"
          data:
            actions:
              - action: "VALIDATE_TASK"
                title: "Valider"
                uri: "/lovelace/kids-tasks"

  - alias: "Notification validation requise"
    description: "Alerte quand une tâche attend validation"
    trigger:
      - platform: event
        event_type: kids_tasks_task_completed
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.validation_required }}"
    action:
      - service: notify.mobile_app_parent
        data:
          title: "Validation requise"
          message: "{{ trigger.event.data.child_name }} attend validation pour {{ trigger.event.data.task_name }}"
```

### Félicitations automatiques

```yaml
automation:
  - alias: "Félicitations montée de niveau"
    description: "Annonce vocale quand un enfant monte de niveau"
    trigger:
      - platform: event
        event_type: kids_tasks_level_up
    action:
      - service: tts.google_translate_say
        data:
          entity_id: media_player.salon
          message: "Bravo {{ trigger.event.data.child_name }} ! Tu passes au niveau {{ trigger.event.data.new_level }} !"

  - alias: "Série de réussites"
    description: "Félicite pour 7 jours consécutifs"
    trigger:
      - platform: event
        event_type: kids_tasks_streak_achieved
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.streak_days >= 7 }}"
    action:
      - service: kids_tasks.add_points
        data:
          child_id: "{{ trigger.event.data.child_id }}"
          points: 50
          reason: "Série de 7 jours consécutifs !"
```

### Rappels quotidiens

```yaml
automation:
  - alias: "Rappel tâches du soir"
    description: "Rappel vocal des tâches non terminées"
    trigger:
      - platform: time
        at: "18:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.kids_tasks_pending_tasks
        above: 0
    action:
      - service: tts.google_translate_say
        data:
          entity_id: media_player.salon
          message: "Il reste {{ states('sensor.kids_tasks_pending_tasks') }} tâches à terminer aujourd'hui !"
```

## Configuration avancée

### Personalisation des points

Vous pouvez ajuster les points selon l'âge ou la difficulté :

```yaml
# Points bonus pour les plus jeunes
automation:
  - alias: "Bonus points jeunes enfants"
    trigger:
      - platform: event
        event_type: kids_tasks_task_validated
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.child_age < 8 }}"
    action:
      - service: kids_tasks.add_points
        data:
          child_id: "{{ trigger.event.data.child_id }}"
          points: 5
          reason: "Bonus jeune enfant"
```

### Pénalités pour tâches oubliées

```yaml
automation:
  - alias: "Pénalité tâches oubliées"
    trigger:
      - platform: time
        at: "20:00:00"  # Vérification le soir
    condition:
      - condition: numeric_state
        entity_id: sensor.kids_tasks_overdue_tasks
        above: 0
    action:
      - service: kids_tasks.remove_points
        data:
          child_id: "{{ child_with_overdue_tasks }}"
          points: 5
          reason: "Tâche oubliée"
```

### Récompenses automatiques

```yaml
automation:
  - alias: "Récompense hebdomadaire automatique"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: time
        weekday:
          - fri  # Vendredi soir
      - condition: template
        value_template: "{{ states('sensor.kids_tasks_emma_tasks_week') | int >= 35 }}"  # 5 tâches * 7 jours
    action:
      - service: kids_tasks.add_points
        data:
          child_id: "emma_001"
          points: 100
          reason: "Semaine parfaite - toutes les tâches réalisées !"
```

## Intégration avec d'autres systèmes

### Google Calendar

```yaml
# Ajouter les tâches importantes au calendrier
automation:
  - alias: "Ajouter tâche importante au calendrier"
    trigger:
      - platform: event
        event_type: kids_tasks_task_created
    condition:
      - condition: template
        value_template: "{{ trigger.event.data.points >= 25 }}"  # Tâches importantes
    action:
      - service: calendar.create_event
        data:
          calendar_entity_id: calendar.famille
          summary: "Tâche: {{ trigger.event.data.task_name }}"
          description: "{{ trigger.event.data.child_name }} - {{ trigger.event.data.points }} points"
          start_date_time: "{{ now().replace(hour=9, minute=0, second=0) }}"
          end_date_time: "{{ now().replace(hour=9, minute=30, second=0) }}"
```

### Éclairage de statut

```yaml
# LED de couleur selon le statut des tâches
automation:
  - alias: "LED statut tâches Emma"
    trigger:
      - platform: state
        entity_id: sensor.kids_tasks_emma_tasks_today
    action:
      - service: light.turn_on
        data:
          entity_id: light.led_chambre_emma
          color_name: >
            {% set completed = states('sensor.kids_tasks_emma_tasks_today') | int %}
            {% set total = states('sensor.kids_tasks_emma_total_tasks') | int %}
            {% if completed == total %}
              green
            {% elif completed > total / 2 %}
              orange
            {% else %}
              red
            {% endif %}
```

### Contrôle parental écrans

```yaml
# Bloquer les écrans si tâches non faites
automation:
  - alias: "Blocage écran tâches non faites"
    trigger:
      - platform: time
        at: "16:00:00"  # Après l'école
    condition:
      - condition: numeric_state
        entity_id: sensor.kids_tasks_emma_tasks_today
        below: 3  # Moins de 3 tâches complétées
    action:
      - service: switch.turn_off
        entity_id: switch.tablette_emma
      - service: notify.mobile_app_emma_tablet
        data:
          message: "Termine tes tâches pour débloquer ta tablette !"
```

## Dépannage configuration

### Problèmes courants

**Services non reconnus** :
- Vérifiez que l'intégration est bien configurée (pas juste installée)
- Redémarrez Home Assistant après modification

**Entités manquantes** :
- Les entités sont créées dynamiquement après ajout d'enfants/tâches
- Utilisez d'abord les services pour créer du contenu

**Automatisations ne se déclenchent pas** :
- Vérifiez les noms des événements : `kids_tasks_task_completed`, etc.
- Consultez les logs pour voir si les événements sont émis

**Points non attribués** :
- Vérifiez que `validation_required` correspond à votre workflow
- Les points ne sont attribués qu'après validation si activée

### Logs de débogage

Pour activer les logs détaillés :

```yaml
# configuration.yaml
logger:
  default: info
  logs:
    custom_components.kids_tasks: debug
```

Ceci affichera toutes les actions de l'intégration dans les logs.
