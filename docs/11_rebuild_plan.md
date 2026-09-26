# 11 — Rebuild Plan

Ce fichier sera complété par le skill `writing-plans` après validation du spec.

## Structure prévisionnelle

### Phase 1 — Socle (nephro_core)
- Fork des modèles ACS (patient, physician, procedure, appointment, prescription)
- Groupes de sécurité et ACL
- Record rules
- Vues de base (list, form)
- Menus
- Tests unitaires (workflow + sécurité)

### Phase 2 — Clinique (nephro_dialysis + nephro_bilans + nephro_complications)
- Extension séance (pré/post dialyse, paramètres machine)
- Signes vitaux, KT/V, poids sec
- Planning, postes, générateur masse
- Bilans biologiques complets avec seuils
- Complications per-séance
- Tables de configuration
- Tests unitaires

### Phase 3 — Opérationnel (nephro_billing + nephro_dashboard)
- Règles tarifaires, facturation auto, facturation groupée
- Dashboard médecin OWL
- Interface infirmier OWL
- Widget secrétaire
- Tests unitaires + tests E2E Playwright

### Phase 4 — Patient (nephro_portal + nephro_whatsapp)
- Portail patient (6 pages + tableau de bord)
- Service WhatsApp + crons
- Tests portail (record rules, pas de sudo)

### Phase 5 — Paiements + i18n (payment_wave + payment_orange_money + nephro_fr)
- Modules de paiement reconstruits (HMAC, sans frais)
- Traductions françaises complètes
- Tests HMAC + codes HTTP

---

*Plan détaillé à générer via `writing-plans`.*
