# 🧸 Kids Tasks Manager pour Home Assistant 

[![GitHub Release](https://img.shields.io/github/v/release/astrayel/kids-tasks-ha?style=for-the-badge)](https://github.com/astrayel/kids-tasks-ha/releases)
[![GitHub Issues](https://img.shields.io/github/issues/astrayel/kids-tasks-ha?style=for-the-badge)](https://github.com/astrayel/kids-tasks-ha/issues)
[![GitHub Stars](https://img.shields.io/github/stars/astrayel/kids-tasks-ha?style=for-the-badge)](https://github.com/astrayel/kids-tasks-ha/stargazers)
[![License](https://img.shields.io/github/license/astrayel/kids-tasks-ha?style=for-the-badge)](https://github.com/astrayel/kids-tasks-ha/blob/main/LICENSE)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange?style=for-the-badge)](https://github.com/hacs/integration)

_Intégration pour gérer les tâches récurrentes des enfants avec système de récompenses et validation parentale._

## 🌟 Fonctionnalités

- ✅ **Gestion des tâches récurrentes** avec catégorisation
- 👶 **Profils enfants individuels** avec système de points et niveaux
- 🎁 **Système de récompenses** personnalisable
- ✋ **Validation parentale** optionnelle
- 📊 **Dashboards dédiés** parents et enfants
- 🔔 **Notifications** temps réel
- 📱 **Interface mobile** optimisée
- 🌍 **Multilingue** (FR/EN)

## 📸 Captures d'écran

| Dashboard Parent | Dashboard Enfant | Configuration |
|---|---|---|
| ![Dashboard Parent](docs/images/dashboard_parent.png) | ![Dashboard Enfant](docs/images/dashboard_child.png) | ![Configuration](docs/images/config_flow.png) |

## 🚀 Installation

### Via HACS (Recommandé)

1. Assurez-vous que [HACS](https://hacs.xyz/) est installé
2. Allez dans HACS → Intégrations
3. Cliquez sur les 3 points en haut à droite → "Dépôts personnalisés"
4. Ajoutez `https://github.com/astrayel/kids-tasks-ha` comme dépôt de type "Intégration"
5. Trouvez "Kids Tasks Manager" et cliquez sur "Télécharger"
6. Redémarrez Home Assistant

### Installation manuelle

1. Téléchargez les fichiers depuis GitHub
2. Copiez le dossier `custom_components/kids_tasks` vers votre dossier `config/custom_components/`
3. Redémarrez Home Assistant

## ⚙️ Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **"+ Ajouter une intégration"**
3. Recherchez **"Kids Tasks Manager"**
4. Suivez l'assistant de configuration

## 📖 Documentation

- [Installation détaillée](docs/installation.md)
- [Configuration avancée](docs/configuration.md)
- [Exemples d'utilisation](docs/examples.md)

## 🛠️ Services disponibles

### `kids_tasks.add_child`
```yaml
service: kids_tasks.add_child
data:
  name: "Emma"
  avatar: "👧"
  kids_tasks.add_task
yamlservice: kids_tasks.add_task
data:
  name: "Ranger sa chambre"
  description: "Faire le lit et ranger les jouets"
  category: "bedroom"
  points: 15
  frequency: "daily"
  assigned_child_id: "emma_id"
kids_tasks.add_reward
yamlservice: kids_tasks.add_reward
data:
  name: "30 min d'écran supplémentaire"
  cost: 20
  category: "screen_time"
Voir tous les services →
🤝 Contribution
Les contributions sont les bienvenues ! Consultez notre guide de contribution.
🆘 Support

Discussions GitHub
Issues GitHub
Community Forum

📝 Changelog
Voir CHANGELOG.md pour l'historique des versions.
📄 Licence
Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.
☕ Support le projet
Si cette intégration vous aide, n'hésitez pas à me soutenir !
Afficher l'image