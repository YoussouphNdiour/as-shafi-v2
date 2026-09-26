# 06 — Decision Tokens

Tokens de décision pris pendant le brainstorming v2 (2026-09-26).

## Décisions fondatrices

| # | Question | Décision | Raison |
|---|---|---|---|
| D1 | Stack v2 ? | Odoo 19 propre (Option A) | Écosystème éprouvé, compta/stock intégrés |
| D2 | Socle ACS ? | Fork léger d'ACS HMS | Contrôle total, extraire les parties utiles, supprimer le reste |
| D3 | Statut clinique ? | Pré-lancement / pilote | Pas de migration de données, on part de zéro |
| D4 | Workflow séance ? | Flux unique simplifié | 1 générateur → procedures, consultations séparées |
| D5 | Modules paiement ? | Reconstruire sans frais cachés | Sécurité, éthique, webhook signé |
| D6 | Priorités ? | Tout en même temps | Pré-lancement, reconstruction complète |
| D7 | Documentation ? | Complète (16 fichiers .md) | Maintenabilité long terme |
| D8 | Modèles ACS à garder ? | patient, physician, procedure, appointment, prescription, consumable.line | + suggestions additionnelles |
| D9 | nephro.insurer ? | Supprimé | Tarification gérée uniquement via pricing.rule liée au patient |

## Décisions de sécurité

| # | Décision | Raison (issue v1) |
|---|---|---|
| S1 | Zéro `sudo()` dans controllers | Cause n°1 des failles sécurité v1 (portail) |
| S2 | Zéro `cr.commit()` | Casse l'isolation transactionnelle (WhatsApp wizard) |
| S3 | ACL deny by default | v1 donnait CRUD à `base.group_user` (tous les utilisateurs Odoo) |
| S4 | Webhooks HMAC signés | v1 acceptait n'importe quelle requête sur les retours paiement |
| S5 | Pas de `auth="public"` sur données médicales | v1 exposait les ordonnances via endpoint public |
| S6 | Pas de frais cachés | v1 ajoutait 200 XOF par transaction vers un numéro personnel |
| S7 | Pas de self-request HTTP | v1 faisait requests.get() vers soi-même → deadlock |
| S8 | Record rules `noupdate="1"` | v1 avait des rules écrasables à chaque upgrade |

## Décisions de workflow

| # | Décision | Raison |
|---|---|---|
| W1 | 4 états max par workflow | v1 avait 7 états RDV inutiles |
| W2 | Pas de lien automatique séance ↔ RDV | v1 créait des doublons |
| W3 | Pas de couche Treatment | Inutile en dialyse chronique |
| W4 | Pas d'Evaluation en contexte néphro | Doublonne avec bilans |
| W5 | Dashboard appelle action_*() pas orm.write() | v1 bypassait le workflow |
| W6 | Erreurs de facturation visibles | v1 faisait `except Exception: pass` |

## Décisions de nommage

| # | Décision |
|---|---|
| N1 | Modules : `nephro_<domaine>` |
| N2 | Modèles : `nephro.<domaine>.<entité>` |
| N3 | Vues : `nephro_<domaine>_<modele>_view_<type>` |
| N4 | Groupes : `nephro_core.group_nephro_<role>` |
| N5 | Strings de champs en anglais, traductions en .po |
