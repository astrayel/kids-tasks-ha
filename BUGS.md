# Bugs en cours

Suivi des problèmes identifiés non encore résolus.

---

## [BUG-001] Les cartes personnalisées n'apparaissent pas dans le sélecteur de tuiles HA

**Statut** : Ouvert  
**Sévérité** : Haute  
**Composant** : `www/kids_tasks/kids-tasks-card.js`  
**Signalé le** : 2026-05-23

### Symptôme

Les 4 cartes (`kids-tasks-child-card`, `kids-tasks-validation-card`, `kids-tasks-task-list-card`, `kids-tasks-reward-card`) n'apparaissent pas dans la liste des tuiles proposées lors de l'ajout d'une carte à un dashboard Lovelace.

### Cause probable

HA utilise `window.customCards` pour peupler le sélecteur de tuiles. Plusieurs raisons possibles :

1. La ressource `/local/kids_tasks/kids-tasks-card.js` n'est pas déclarée dans Lovelace (Paramètres → Tableaux de bord → Ressources)
2. Le fichier JS est chargé après que HA scanne `window.customCards` au démarrage
3. Le champ `preview: true` absent des entrées `window.customCards` — certaines versions HA l'exigent pour afficher la carte dans le picker

### Pistes de résolution

- [ ] Vérifier que la ressource est bien déclarée avec le type `module`
- [ ] Ajouter `preview: true` dans chaque entrée de `window.customCards`
- [ ] Tester l'enregistrement via `customElements.whenDefined()` pour s'assurer que le push dans `window.customCards` se fait après la définition de l'élément
- [ ] Vérifier dans la console du navigateur que `window.customCards` contient bien les 4 entrées après le chargement de la page

### Références

- [HA Custom Cards documentation](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)
- `www/kids_tasks/kids-tasks-card.js` — section HACS / Lovelace registration (fin du fichier)

---

## [BUG-002] Perte totale des données après mise à jour vers v2.0.0

**Statut** : Ouvert  
**Sévérité** : Critique  
**Composant** : `coordinator/_storage.py`, `const.py`  
**Signalé le** : 2026-05-23

### Symptôme

Après installation de la branche `dev` (v2.0.0), toutes les données sont perdues : enfants, tâches, récompenses, points, historique, configuration des cartes. L'intégration repart de zéro comme lors d'une première installation.

### Causes candidates à investiguer

1. **Migration v1 → v2 défectueuse** — `_migrate_data()` dans `coordinator/_storage.py` est appelée quand `STORAGE_VERSION` passe de 1 à 2. Si la fonction retourne un dict vide ou mal formé au lieu des données migrées, toutes les données sont silencieusement écrasées.

2. **Clé de stockage modifiée** — `STORAGE_KEY = f"{DOMAIN}.storage"` est identique entre v1 et v2, mais vérifier que le fichier `.storage/kids_tasks.storage` est bien présent sur le système après la mise à jour.

3. **`async_remove_entry` appelé par erreur** — cette fonction dans `__init__.py` appelle `storage.async_remove()` et supprime toutes les entités. Elle ne doit être appelée que lors d'une désinstallation, pas d'un rechargement. À vérifier dans les logs HA au moment du redémarrage.

4. **Rechargement de l'intégration** — si l'intégration est rechargée (plutôt que HA redémarré) pendant la mise à jour, des race conditions entre `async_unload_entry` et `async_setup_entry` pourraient corrompre l'état en mémoire avant la sauvegarde.

### Données à collecter pour diagnostiquer

- [ ] Contenu du fichier `.storage/kids_tasks.storage` **avant** et **après** la mise à jour (backup HA ou accès SSH)
- [ ] Logs HA complets au moment du redémarrage — chercher `kids_tasks` et `storage`
- [ ] Vérifier si `async_remove_entry` apparaît dans les logs
- [ ] Vérifier la valeur de `version` dans `.storage/kids_tasks.storage` (doit passer de 1 à 2 après migration)

### Risque

Perte irréversible des données utilisateur si le fichier `.storage/kids_tasks.storage` a été écrasé ou supprimé. Bloquerait toute mise à jour v1 → v2 en production.

### Références

- `custom_components/kids_tasks/coordinator/_storage.py` — `_migrate_data()`, `_load_data()`
- `custom_components/kids_tasks/const.py` — `STORAGE_VERSION = 2`, `STORAGE_KEY`
- `custom_components/kids_tasks/__init__.py` — `async_remove_entry()`
