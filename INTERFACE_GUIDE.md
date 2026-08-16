# Guide des cartes Lovelace — Kids Tasks Manager

Les cartes ne sont **pas** dans ce dépôt. Elles vivent dans
[kids-tasks-ha-card](https://github.com/astrayel/kids-tasks-ha-card) et
s'installent séparément.

---

## Installation

### Via HACS (recommandé)

1. HACS → menu (⋮) → **Dépôts personnalisés**
2. URL : `https://github.com/astrayel/kids-tasks-ha-card`, catégorie **Lovelace**
3. Installer « Kids Tasks Card »
4. Redémarrer Home Assistant

### Manuellement

1. Récupérer `dist/kids-tasks-card.js` depuis le dépôt des cartes
2. Le copier dans `config/www/kids-tasks-card/`
3. **Paramètres → Tableaux de bord → Ressources → Ajouter**
   - URL : `/local/kids-tasks-card/kids-tasks-card.js`
   - Type : Module JavaScript

---

## Les quatre cartes

### `custom:kids-tasks-child-card` — vue enfant

Avatar, points, pièces, niveau, tâches du jour, récompenses et cosmétiques.
C'est la seule carte à mettre sur le dashboard d'un enfant ou d'une tablette.

```yaml
type: custom:kids-tasks-child-card
child_id: 3f2a1b4c-8e7d-4f9a-b2c1-0d5e6f7a8b9c
title: Mes tâches          # optionnel
show_rewards: true         # optionnel, défaut true
show_cosmetics: true       # optionnel, défaut true
show_completed: true       # optionnel, défaut true
```

Le `child_id` se lit dans les attributs de `sensor.kidtasks_<prénom>_points`
(Outils de développement → États).

Les tâches affichées reflètent le statut **de cet enfant**, pas l'état global
de la tâche : sur une tâche partagée, chacun voit son propre avancement.

### `custom:kids-tasks-supervisor` — validation parentale

File des tâches en attente, gestes de balayage pour valider ou rejeter, vue
d'ensemble des enfants, ajustement de points, historique global avec annulation.

```yaml
type: custom:kids-tasks-supervisor
title: Supervision         # optionnel
show_navigation: true      # optionnel, défaut true
```

Valider ou rejeter agit sur **un seul enfant** — celui de la ligne — et laisse
ses frères et sœurs en attente.

Affiche « réservé aux parents » sur un compte non-administrateur.

### `custom:kids-tasks-manager` — administration

CRUD complet des enfants, tâches et récompenses, et gestion des cosmétiques.

```yaml
type: custom:kids-tasks-manager
title: Administration      # optionnel
```

Affiche « réservé aux parents » sur un compte non-administrateur.

### `custom:kids-tasks-card` — tableau de bord général

Vue d'ensemble de la famille, plutôt destinée à un écran partagé du salon.

```yaml
type: custom:kids-tasks-card
title: Kids Tasks
show_completed: true
show_rewards: true
```

---

## Dashboards types

Voir [docs/dashboards.md](docs/dashboards.md) pour les trois configurations
complètes — vue enfant, vue tablette partagée, vue parent — ainsi que
l'exclusion recorder recommandée.

---

## Droits

Masquer une carte n'est pas une protection. La garde réelle est côté serveur,
dans l'intégration : voir [docs/permissions.md](docs/permissions.md).

---

## Dépannage

**La carte n'apparaît pas dans le sélecteur** — la ressource Lovelace n'est pas
déclarée, ou le navigateur a mis l'ancienne version en cache. Vider le cache et
recharger.

**« Enfant non trouvé (ID: …) »** — le `child_id` de la configuration ne
correspond à aucun enfant. Le relire dans les attributs du capteur de points.

**Un bouton ne fait rien** — ouvrir la console du navigateur. Un appel de
service refusé indique le régime de droits de l'appelant ; consulter
`docs/permissions.md`.
