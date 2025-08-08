# 🖥️ Guide de l'Interface Graphique Kids Tasks Manager

## 📖 Vue d'ensemble

L'interface graphique Kids Tasks Manager vous permet de gérer facilement les enfants, tâches et récompenses sans avoir à écrire de configuration YAML. Cette interface moderne et responsive fonctionne directement dans Home Assistant.

## 🚀 Installation

### 1. Installation automatique (Recommandée)

Utilisez le script d'installation fourni :

```bash
# Depuis le répertoire du projet
python install.py

# Ou spécifiez le chemin vers votre config HA
python install.py /path/to/homeassistant/config
```

Le script copiera automatiquement :
- L'intégration dans `custom_components/kids_tasks/`
- L'interface dans `www/kids_tasks/kids-tasks-card.js`

### 2. Installation manuelle

#### Étape 1 : Intégration
Copiez le dossier complet :
```
custom_components/kids_tasks/ → config/custom_components/kids_tasks/
```

#### Étape 2 : Interface frontend
Créez le répertoire et copiez le fichier :
```bash
mkdir -p config/www/kids_tasks/
cp custom_components/kids_tasks/kids-tasks-card.js config/www/kids_tasks/
```

### 3. Configuration dans Home Assistant

#### Via l'interface utilisateur :

1. **Configuration** → **Lovelace Dashboards** → **Ressources**
2. Cliquez sur **"+ Ajouter une ressource"**
3. URL : `/local/kids_tasks/kids-tasks-card.js`
4. Type de ressource : **Module JavaScript**
5. Cliquez sur **"Créer"**

#### Via configuration YAML :

Ajoutez dans votre `configuration.yaml` :
```yaml
lovelace:
  resources:
    - url: /local/kids_tasks/kids-tasks-card.js
      type: module
```

### 4. Redémarrage
Redémarrez Home Assistant pour charger l'intégration.

### 3. Ajouter la carte à votre dashboard

1. Allez dans votre dashboard Lovelace
2. Cliquez sur **"Modifier le dashboard"**
3. Cliquez sur **"+ Ajouter une carte"**
4. Recherchez **"Kids Tasks Card"**
5. Configurez selon vos préférences

## 🎛️ Configuration de la carte

### Options disponibles

```yaml
type: kids-tasks-card
title: "Gestionnaire de Tâches Enfants"  # Optionnel
show_navigation: true  # Afficher les onglets (défaut: true)
```

### Exemple de configuration complète

```yaml
type: kids-tasks-card
title: "Tâches de la famille Martin"
show_navigation: true
```

## 🧭 Navigation

L'interface est organisée en 4 onglets principaux :

### 📊 **Tableau de bord**
- Vue d'ensemble avec statistiques
- Cartes des enfants avec leur progression
- Tâches en attente de validation parentale
- Classement des enfants par points

### 👶 **Enfants**
- Liste de tous les enfants enregistrés
- Ajout/modification des profils enfants
- Vue des statistiques individuelles
- Gestion des avatars et informations

### 📝 **Tâches**
- Liste de toutes les tâches créées
- Création et modification des tâches
- Assignation aux enfants
- Gestion des catégories et fréquences

### 🎁 **Récompenses**
- Catalogue des récompenses disponibles
- Création et modification des récompenses
- Gestion des coûts en points
- Échange de récompenses

## ✨ Fonctionnalités principales

### 🎯 **Gestion des enfants**

**Ajouter un enfant :**
1. Onglet **"Enfants"** → Bouton **"Ajouter"**
2. Saisissez le nom
3. Choisissez un avatar emoji
4. Définissez les points initiaux (optionnel)
5. Cliquez sur **"Enregistrer"**

**Modifier un enfant :**
1. Cliquez sur **"Modifier"** sur la carte de l'enfant
2. Modifiez les informations
3. Ajustez les points si nécessaire
4. Sauvegardez les changements

### 📋 **Gestion des tâches**

**Créer une tâche :**
1. Onglet **"Tâches"** → Bouton **"Ajouter"**
2. Nom et description de la tâche
3. Choisissez la catégorie (chambre, devoirs, etc.)
4. Définissez les points attribués
5. Sélectionnez la fréquence (quotidienne, hebdomadaire, etc.)
6. Assignez à un enfant
7. Activez/désactivez la validation parentale

**Catégories disponibles :**
- 🛏️ **Chambre** : Ranger, faire le lit
- 🛁 **Salle de bain** : Se laver, nettoyer
- 🍽️ **Cuisine** : Mettre la table, débarrasser
- 📚 **Devoirs** : Faire les devoirs, réviser
- 🌳 **Extérieur** : Jardinage, sortir les poubelles
- 🐕 **Animaux** : Nourrir, promener
- 📦 **Autre** : Tâches diverses

**Fréquences disponibles :**
- **Quotidienne** : Tous les jours
- **Hebdomadaire** : Une fois par semaine
- **Mensuelle** : Une fois par mois
- **Une fois** : Tâche ponctuelle

### 🎁 **Gestion des récompenses**

**Créer une récompense :**
1. Onglet **"Récompenses"** → Bouton **"Ajouter"**
2. Nom et description de la récompense
3. Choisissez la catégorie
4. Définissez le coût en points
5. Activez la quantité limitée si nécessaire

**Catégories de récompenses :**
- 📱 **Écran** : Temps supplémentaire tablette/TV
- 🚗 **Sortie** : Parc, cinéma, restaurant
- 👑 **Privilège** : Choisir le repas, se coucher plus tard
- 🧸 **Jouet** : Nouveau jouet, livre
- 🍭 **Friandise** : Bonbons, glace
- 🎉 **Amusement** : Activité spéciale

**Échanger une récompense :**
1. Cliquez sur **"Échanger"** sur la récompense
2. Sélectionnez l'enfant (doit avoir assez de points)
3. Confirmez l'échange
4. Les points sont automatiquement déduits

## 🎮 **Validation parentale**

### Processus de validation

1. L'enfant termine une tâche (via app mobile ou interface)
2. La tâche passe en statut **"En attente"**
3. Elle apparaît dans la section **"Tâches à valider"** du tableau de bord
4. Le parent clique sur **"Valider"** ou **"Rejeter"**
5. Si validée, les points sont attribués à l'enfant

### Actions disponibles

- ✅ **Valider** : Accorde les points et marque comme terminée
- ❌ **Rejeter** : Remet la tâche en statut "À faire"

## 📱 **Interface responsive**

L'interface s'adapte automatiquement aux différentes tailles d'écran :

**Desktop/Tablette :**
- Navigation par onglets horizontaux
- Grilles multi-colonnes
- Formulaires en ligne

**Mobile :**
- Navigation compacte
- Affichage en colonne unique
- Formulaires empilés verticalement

## 🎨 **Personnalisation visuelle**

L'interface respecte le thème de votre Home Assistant :

- **Couleurs** : Suit votre thème actuel
- **Police** : Utilise la police système de HA
- **Animations** : Transitions fluides et modernes
- **Icons** : Emojis pour une interface ludique

## 🔧 **Intégration avec les automatisations**

L'interface fonctionne parfaitement avec vos automatisations existantes :

```yaml
# Exemple : Notification quand une tâche est terminée
automation:
  - alias: "Notification tâche terminée"
    trigger:
      - platform: event
        event_type: kids_tasks_task_completed
    action:
      - service: notify.mobile_app_parent
        data:
          title: "Tâche terminée !"
          message: "{{ trigger.event.data.child_name }} a terminé {{ trigger.event.data.task_name }}"
```

## 🐛 **Dépannage**

### La carte ne s'affiche pas
1. Vérifiez que le fichier JS est bien dans le bon répertoire
2. Rechargez les ressources Lovelace
3. Vérifiez la console du navigateur pour les erreurs

### Données non affichées
1. Vérifiez que l'intégration Kids Tasks est configurée
2. Ajoutez au moins un enfant via les services
3. Les entités apparaissent dynamiquement après création

### Formulaires non fonctionnels
Note : Dans la version actuelle, les formulaires affichent des alertes de placeholder. 
Pour les fonctionnalités complètes, utilisez les services Home Assistant.

## 🚀 **Fonctionnalités à venir**

- ✅ Formulaires modaux interactifs complets
- ✅ Glisser-déposer pour réorganiser
- ✅ Graphiques de progression avancés
- ✅ Mode sombre/clair
- ✅ Notifications push
- ✅ Export PDF des rapports

## 📞 **Support**

Pour toute question ou problème :
- [Issues GitHub](https://github.com/astrayel/kids-tasks-ha/issues)
- [Discussions](https://github.com/astrayel/kids-tasks-ha/discussions)
- [Communauté Home Assistant](https://community.home-assistant.io/)

---

*Interface créée avec ❤️ pour simplifier la gestion des tâches familiales*