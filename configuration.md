⚙️ Configuration Kids Tasks Manager
Configuration initiale
Via l'interface utilisateur

Configuration → Intégrations → Ajouter une intégration
Recherchez "Kids Tasks Manager"
Configurez les options :

Nom : Nom de votre installation
Validation parentale : Activée par défaut
Notifications : Activées par défaut



Configuration avancée
Options disponibles
OptionDescriptionDéfautvalidation_requiredValidation parentale obligatoiretruenotifications_enabledNotifications activéestrueauto_reset_tasksRemise à zéro automatiquetruepoints_multiplierMultiplicateur de points1.0
Modification des options

Configuration → Intégrations
Trouvez Kids Tasks Manager
Cliquez sur "Configurer"
Modifiez les paramètres souhaités

Premiers pas
1. Ajouter des enfants
yamlservice: kids_tasks.add_child
data:
  name: "Emma"
  avatar: "👧"
  initial_points: 0
2. Créer des tâches
yamlservice: kids_tasks.add_task  
data:
  name: "Ranger sa chambre"
  category: "bedroom"
  points: 15
  frequency: "daily"
  assigned_child_id: "emma_001"
3. Définir des récompenses
yamlservice: kids_tasks.add_reward
data:
  name: "30 min d'écran supplémentaire" 
  cost: 50
  category: "screen_time"
Automatisations recommandées
Réinitialisation quotidienne
yamlautomation:
  - alias: "Reset tâches quotidiennes"
    trigger:
      - platform: time
        at: "06:00:00"
    action:
      - service: kids_tasks.reset_all_daily_tasks
Notifications
yamlautomation:
  - alias: "Notification tâche terminée"
    trigger:
      - platform: event
        event_type: kids_tasks_task_completed
    action:
      - service: notify.mobile_app_parent
        data:
          title: "Tâche terminée !"
          message: "{{ trigger.event.data.child_name }} a terminé {{ trigger.event.data.task_name }}"
Personnalisation
Catégories personnalisées
Les catégories par défaut peuvent être étendues en modifiant const.py
Points et niveaux
Le système de niveaux peut être personnalisé dans models.py
Interface utilisateur
Des cartes Lovelace personnalisées peuvent être créées pour afficher les données
