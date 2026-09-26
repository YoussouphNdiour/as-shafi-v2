# 14 — Quality Contract

Règles non négociables pour la v2. Tout code qui viole ces règles est rejeté.

## Sécurité — Règles absolues

1. **JAMAIS** `sudo()` dans un controller ou une route HTTP
2. **JAMAIS** `self.env.cr.commit()` dans du code modèle ou wizard
3. **JAMAIS** `auth="public"` sur une route qui retourne des données médicales
4. **JAMAIS** `except Exception: pass` — au minimum `_logger.exception()`
5. **JAMAIS** de frais cachés non déclarés dans les modules de paiement
6. **JAMAIS** `requests.get()` vers son propre serveur
7. **JAMAIS** `Access-Control-Allow-Origin: *` sur des endpoints de fichiers médicaux
8. **JAMAIS** `Cache-Control: max-age > 3600` sur des documents médicaux PDF
9. **JAMAIS** `noupdate="0"` sur des record rules de sécurité
10. **JAMAIS** d'ACL CRUD pour `base.group_user` sur des modèles médicaux

## Workflow — Règles absolues

11. Les composants OWL appellent `this.orm.call('model', 'action_method')` — **JAMAIS** `this.orm.write({'state': '...'})` directement
12. Chaque transition d'état passe par une méthode Python `action_*()` qui valide les prérequis
13. Maximum 4 états par workflow : `scheduled/running/done/cancel` ou `draft/confirmed/done/cancel`

## Code — Règles absolues

14. Strings de champs en **anglais** : `string="Blood Pressure"` — traductions dans `.po`
15. Logger : `_logger.info("message %s", arg)` — **pas** de f-string dans les appels logger
16. Manifest : `'author': 'As-Shafi Medical'`, `'license': 'LGPL-3'`, `'installable': True` explicite
17. Webhook paiement : HMAC SHA-256 obligatoire, codes HTTP corrects (200/400/500)
18. Chaque module a un dossier `tests/` avec au minimum 1 test class par modèle principal

## Portail — Règles absolues

19. Le portail utilise les record rules pour filtrer — pas de sudo
20. Pagination sur toutes les listes (20 items/page)
21. Validation de longueur sur les champs texte utilisateur (max 2000 chars)
22. Toutes les routes portail en `auth="user"` (pas `auth="public"`)

## Processus

- Tout PR doit passer les tests `--test-enable` sans erreur
- Code review obligatoire avant merge
- Vérification grep `sudo()`, `cr.commit()`, `except Exception: pass` avant chaque release
