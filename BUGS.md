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
