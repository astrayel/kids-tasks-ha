# Modèle de droits

Kids Tasks classe chaque appel de service dans l'un de quatre régimes, déduit
du compte Home Assistant à l'origine de l'appel. La garde est **côté serveur** :
masquer un bouton dans une carte ne protège rien, contourner l'interface avec
les outils de développement est à la portée d'un enfant curieux.

## Les quatre régimes

| Régime | Reconnu par | Peut faire | Ne peut pas |
|---|---|---|---|
| **Parent** | `user.is_admin` | tout | — |
| **Enfant** | `user_id` ↔ `person_entity_id` du profil | compléter, réclamer, équiper, lire son historique — **pour lui seul** | valider, rejeter, points, niveaux, CRUD |
| **Tablette** | `user_id` listé dans l'option `kiosk_users` | compléter, réclamer, équiper — **pour n'importe quel enfant** | valider, rejeter, points, niveaux, CRUD |
| **Invité** | tout le reste | `list_tasks`, `list_children` | toute écriture |

Un appel sans utilisateur (`context.user_id is None`) — automatisation, script,
blueprint — est traité comme **interne** et autorisé : il a été écrit par
quelqu'un qui disposait déjà d'un accès administrateur.

## Pourquoi un régime « tablette »

Une tablette murale est connectée sous un compte unique. Elle ne peut pas
savoir lequel des trois enfants se tient devant elle, donc restreindre ses
actions à un seul profil la rendrait inutilisable. Le compte kiosque agit donc
pour n'importe quel enfant.

Le trou est assumé : un enfant peut marquer faite la tâche d'un frère ou d'une
sœur depuis la tablette. Deux choses le rendent acceptable :

1. **La validation parentale reste obligatoire** — rien n'est crédité sans un
   passage par un compte parent.
2. **Rien de sensible n'est atteignable** depuis ce compte : ni points, ni
   niveaux, ni création ou suppression.

Le choix du profil sur la tablette est libre, sans code : la friction d'un code
partagé entre enfants qui se regardent taper n'apporte rien de plus que la
validation parentale.

## Configuration

1. Créez un compte Home Assistant **non-administrateur** par enfant, et une
   entité `person` pointant vers ce compte.
2. Renseignez cette entité dans le profil de l'enfant
   (`person_entity_id`) — c'est ce qui fait le lien.
3. Créez un compte non-administrateur pour la tablette.
4. Déclarez-le dans **Paramètres → Appareils et services → Kids Tasks →
   Configurer → Appareils partagés (tablette)**.

Un enfant sans compte lié n'est pas bloqué : ses tâches restent accessibles
depuis la tablette et depuis les comptes parents.

## Ajouter un service

Tout service non listé dans `POLICY_CHILD_SCOPED` ou `POLICY_PUBLIC`
(`permissions.py`) est **réservé aux parents** par défaut. Un nouveau service
est donc verrouillé tant qu'on ne l'ouvre pas explicitement — l'oubli va dans
le sens sûr.

Les services sont enregistrés via `build_registrar()` et non directement par
`hass.services.async_register`, ce qui garantit qu'aucun ne peut être exposé
sans garde par inadvertance.

## Vérifier

Connecté avec le compte d'un enfant, dans **Outils de développement →
Actions** :

- `kids_tasks.complete_task` avec son propre `child_id` → fonctionne
- `kids_tasks.complete_task` avec le `child_id` d'un frère → refusé
- `kids_tasks.validate_task` → refusé
- `kids_tasks.set_points` → refusé

Depuis le compte tablette :

- `kids_tasks.complete_task` avec n'importe quel `child_id` → fonctionne
- `kids_tasks.set_points` → refusé
