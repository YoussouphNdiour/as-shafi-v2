# 10 — Current Issues (v1)

Problèmes identifiés lors du code review de la v1 (modules `acs_hms_*`). Chaque problème est corrigé dans la v2.

## Problèmes critiques

### C1 — Frais cachés dans les modules de paiement
- **Fichiers** : `payment_wave/const.py`, `payment_orange_money/const.py`
- **Problème** : 200 XOF ajoutés silencieusement à chaque transaction, versés vers `+221777671661`
- **Correction v2** : Supprimé. Zéro frais développeur.

### C2 — `self.env.cr.commit()` dans WhatsApp
- **Fichiers** : `acs_hms_whatsapp/wizard/whatsapp_compose_message.py:86`, `whatsapp_compose_invoice.py:82`
- **Problème** : Casse l'isolation transactionnelle, corruption de données possible
- **Correction v2** : Supprimé. Service stateless sans commit.

### C3 — Endpoint public exposant des données médicales
- **Fichier** : `acs_hms/controllers/acs_hms.py:11-16`
- **Problème** : Route `auth="public"` + `sudo()` pour accéder aux ordonnances via un code simple
- **Correction v2** : Toutes routes médicales en `auth="user"`, pas de sudo.

### C4 — URL production hardcodée (Wave)
- **Fichier** : `payment_wave/models/payment_transaction.py:157`
- **Problème** : `base_url = 'https://as-shafi.com'` → webhooks pointent vers prod en dev
- **Correction v2** : `get_base_url()` dynamique.

### C5 — Self-request HTTP (WhatsApp)
- **Fichier** : `acs_hms_whatsapp/wizard/whatsapp_compose_message.py:119-128`
- **Problème** : `requests.get()` vers soi-même → risque deadlock
- **Correction v2** : Supprimé.

## Problèmes élevés

### H1 — ACL trop permissives
- `acs.nephrology.schedule` : CRUD pour `base.group_user` (tous les utilisateurs Odoo)
- **Correction v2** : ACL deny by default, groupes dédiés `group_nephro_*`

### H2 — Facturation silencieuse
- `nephro_billing/models/procedure.py:456` : `except Exception: pass`
- **Correction v2** : Erreurs visibles, pas de try/except aveugle

### H3 — Dashboard bypass workflow
- `NurseDashboard.js:176` : `orm.write('state', 'cancel')` direct
- **Correction v2** : Toujours `orm.call('action_cancel')`

### H4 — CORS wildcard sur fichiers médicaux
- `acs_hms_whatsapp/controllers/main.py:444` : `Access-Control-Allow-Origin: *`
- **Correction v2** : Pas de header CORS (API server-side)

### H5 — Webhook paiement sans signature
- `payment_orange_money/controllers/main.py:487-604`
- **Correction v2** : HMAC SHA-256 obligatoire

### H6 — Webhook retourne toujours HTTP 200
- `payment_wave/controllers/main.py:692-743`
- **Correction v2** : 200/400/500 selon le cas

## Problèmes moyens

- `chlore` en `Char` au lieu de `Float` dans bilans
- Cache 1 an sur documents médicaux PDF
- Attachements `public: True` permanent (WhatsApp)
- `noupdate="0"` sur record rules (écrasables à chaque upgrade)
- Auteur manifest `'Odoo S.A.'` au lieu de `'As-Shafi Medical'`
- Pas de pagination sur certaines routes portail
- 4 flux différents pour créer des séances
- 7 états RDV inutiles
- Couche Treatment inutile en dialyse chronique
- N+1 queries dans le dashboard médecin
- Mois hardcodés en français dans le code Python

## Problèmes faibles

- Imports inutilisés
- Code commenté non supprimé
- f-strings dans les appels logger
- ACL dupliquées dans les CSV
- Modules sans `installable: True` explicite
- Pas de fichiers i18n pour la plupart des modules custom
