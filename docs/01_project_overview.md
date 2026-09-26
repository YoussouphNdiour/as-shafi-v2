# 01 — Project Overview

## Vision

As-Shafi Medical est une plateforme clinique de gestion de dialyse/néphrologie construite sur Odoo 19. La v2 est une reconstruction complète des plugins, corrigeant les problèmes architecturaux, de sécurité et de workflow de la v1.

## Contexte

- **Établissement** : Centre de dialyse As-Shafi Medical
- **Périmètre** : 50-150 patients dialysés, 150-500 séances/semaine
- **Statut** : Pré-lancement / pilote (pas de migration de données)

## Stack technique

| Composant | Technologie |
|---|---|
| Backend | Odoo 19 (Python 3.12) |
| Frontend backend | OWL (Odoo Web Library) |
| Portail | QWeb templates (responsive) |
| Base de données | PostgreSQL |
| Conteneurisation | Docker |
| Serveur | VPS Contabo PRO4 (12 vCPU / 24 GB RAM) |
| Proxy | Nginx + SSL Let's Encrypt |
| WhatsApp | WasenderAPI |
| Paiements | Wave API, Orange Money API |

## Approche

**Fork léger d'ACS HMS** : on extrait les modèles utiles (patient, physician, procedure, appointment, prescription) des modules ACS propriétaires et on les reconstruit dans un socle propre `nephro_core`. Les modules domaine (dialysis, bilans, complications, billing, dashboard, portal) sont construits par-dessus.

## Modules v2

```
nephro_core → nephro_dialysis → nephro_bilans
                              → nephro_complications
                              → nephro_billing
                              → nephro_dashboard
                              → nephro_portal
           → nephro_whatsapp
           → nephro_fr
payment_wave (indépendant)
payment_orange_money (indépendant)
```

## Utilisateurs

| Rôle | Device | Interface principale |
|---|---|---|
| Médecin néphrologue | PC bureau | Dashboard + dossier patient |
| Infirmière | Tablette | Interface séance tactile (OWL) |
| Secrétaire | PC | Planning + patients |
| Agent facturation | PC | Factures + paiements |
| Patient | Téléphone / navigateur | Portail web `/my/nephro` |
| Administrateur | PC | Configuration complète |

## Référence

- Spec complet : `docs/superpowers/specs/2026-09-26-nephro-v2-complete-design.md`
- Code review v1 : `docs/10_current_issues.md`
