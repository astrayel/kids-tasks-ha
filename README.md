# 🧸 Kids Tasks Manager pour Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![HACS][hacs-shield]][hacs]

![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffee-shield]][buymecoffee]

_Intégration pour gérer les tâches récurrentes des enfants avec système de récompenses et validation parentale._

---

## 🌟 Fonctionnalités

- ✅ **Gestion des tâches récurrentes** avec catégorisation
- 👶 **Profils enfants individuels** avec système de points et niveaux  
- 🎁 **Système de récompenses** personnalisable
- ✋ **Validation parentale** optionnelle
- 📊 **Dashboards dédiés** parents et enfants
- 🔔 **Notifications** temps réel
- 📱 **Interface mobile** optimisée
- 🌍 **Multilingue** (FR/EN)

---

## 📸 Captures d'écran

### Interface Graphique
| Tableau de bord | Gestion Enfants | Gestion Tâches | Validation Parentale |
|---|---|---|---|
| ![Dashboard](docs/images/interface_dashboard.png) | ![Enfants](docs/images/interface_children.png) | ![Tâches](docs/images/interface_tasks.png) | ![Validation](docs/images/interface_validation.png) |

### Configuration
| Dashboard Parent | Dashboard Enfant | Config Flow |
|---|---|---|
| ![Dashboard Parent](docs/images/dashboard_parent.png) | ![Dashboard Enfant](docs/images/dashboard_child.png) | ![Configuration](docs/images/config_flow.png) |

---

## 🚀 Installation

### Via HACS (Recommandé)

1. Assurez-vous que [HACS](https://hacs.xyz/) est installé
2. Allez dans **HACS** → **Intégrations** 
3. Cliquez sur **⋮** → **"Dépôts personnalisés"**
4. Ajoutez `https://github.com/astrayel/kids-tasks-ha` comme dépôt **"Intégration"**
5. Trouvez **"Kids Tasks Manager"** et cliquez sur **"Télécharger"**
6. Redémarrez Home Assistant

### Installation automatique

Utilisez le script fourni :
```bash
python install.py
```

### Installation manuelle

1. Téléchargez les fichiers depuis GitHub
2. Copiez `custom_components/kids_tasks` vers votre dossier `config/custom_components/`
3. Copiez `kids-tasks-card.js` vers `config/www/kids_tasks/`
4. Redémarrez Home Assistant

### Configuration de l'interface

Ajoutez la ressource Lovelace :
- URL : `/local/kids_tasks/kids-tasks-card.js`
- Type : Module JavaScript

Puis ajoutez une carte de type `kids-tasks-card` à votre dashboard.

📖 **[Guide complet de l'interface](INTERFACE_GUIDE.md)**

---

## ⚙️ Configuration

1. Allez dans **Configuration** → **Intégrations**
2. Cliquez sur **"+ Ajouter une intégration"** 
3. Recherchez **"Kids Tasks Manager"**
4. Suivez l'assistant de configuration

---

## 🛠️ Services disponibles

### Ajouter un enfant
```yaml
service: kids_tasks.add_child
data:
  name: "Emma"
  avatar: "👧"
```

### Ajouter une tâche
```yaml
service: kids_tasks.add_task
data:
  name: "Ranger sa chambre"
  description: "Faire le lit et ranger les jouets"
  category: "bedroom"
  points: 15
  frequency: "daily"
  assigned_child_id: "emma_id"
```

### Ajouter une récompense
```yaml
service: kids_tasks.add_reward
data:
  name: "30 min d'écran supplémentaire"
  cost: 20
  category: "screen_time"
```

---

## 📖 Documentation

- [Installation détaillée](docs/installation.md)
- [Configuration avancée](docs/configuration.md) 
- [Exemples d'utilisation](docs/examples.md)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Consultez notre [guide de contribution](CONTRIBUTING.md).

---

## 🆘 Support

- [Discussions GitHub](https://github.com/astrayel/kids-tasks-ha/discussions)
- [Issues GitHub](https://github.com/astrayel/kids-tasks-ha/issues)
- [Community Forum](https://community.home-assistant.io/)

---

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## ☕ Support le projet

Si cette intégration vous aide, n'hésitez pas à me soutenir !

[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/astrayel)

---

<!-- Badges -->
[releases-shield]: https://img.shields.io/github/release/astrayel/kids-tasks-ha.svg?style=for-the-badge
[releases]: https://github.com/astrayel/kids-tasks-ha/releases

[commits-shield]: https://img.shields.io/github/commit-activity/y/astrayel/kids-tasks-ha.svg?style=for-the-badge  
[commits]: https://github.com/astrayel/kids-tasks-ha/commits/main

[license-shield]: https://img.shields.io/github/license/astrayel/kids-tasks-ha.svg?style=for-the-badge

[hacs-shield]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/hacs/integration

[maintenance-shield]: https://img.shields.io/badge/maintainer-astrayel-blue.svg?style=for-the-badge

[buymecoffee]: https://www.buymeacoffee.com/astrayel
[buymecoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
