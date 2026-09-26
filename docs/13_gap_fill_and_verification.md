# 13 — Gap Fill and Verification

Checklist de vérification : rien n'est oublié entre la v1 et la v2.

## Fonctionnalités v1 → v2

| Fonctionnalité v1 | Portée v2 | Module v2 | Statut |
|---|---|---|---|
| Dossier patient (identité, HMS ID) | ✅ Porté | nephro_core | — |
| Fiche médecin | ✅ Porté | nephro_core | — |
| Séance de dialyse (procédure) | ✅ Porté + enrichi | nephro_core + nephro_dialysis | — |
| Consultation (RDV) simplifié 4 états | ✅ Porté | nephro_core | — |
| Ordonnances médicamenteuses | ✅ Porté | nephro_core | — |
| Consommables par séance | ✅ Porté | nephro_core | — |
| Signes vitaux multi-mesures | ✅ Porté | nephro_dialysis | — |
| Alerte hypotension (TA < 90) | ✅ Porté | nephro_dialysis | — |
| KT/V Daugirdas II auto | ✅ Porté | nephro_dialysis | — |
| URR auto | ✅ Porté | nephro_dialysis | — |
| Poids sec historique | ✅ Porté | nephro_dialysis | — |
| Planning dialyse | ✅ Porté | nephro_dialysis | — |
| Postes de dialyse | ✅ Porté | nephro_dialysis | — |
| Générateur séances masse | ✅ Porté (flux unique) | nephro_dialysis | — |
| Jours fériés | ✅ Porté | nephro_dialysis | — |
| Bilans biologiques complets | ✅ Porté (chlore Float) | nephro_bilans | — |
| Seuils configurables | ✅ Porté | nephro_bilans | — |
| Badges couleur bilans | ✅ Porté | nephro_bilans | — |
| Cron bilans en retard | ✅ Porté | nephro_bilans | — |
| Complications per-séance | ✅ Porté | nephro_complications | — |
| Règles tarifaires | ✅ Porté (sans insurer) | nephro_billing | — |
| Facturation auto | ✅ Porté (sans except pass) | nephro_billing | — |
| Facturation groupée | ✅ Porté (wizard) | nephro_billing | — |
| Solde patient | ✅ Porté | nephro_billing | — |
| Dashboard médecin OWL | ✅ Porté | nephro_dashboard | — |
| Interface infirmier OWL | ✅ Porté | nephro_dashboard | — |
| Widget secrétaire | ✅ Porté | nephro_dashboard | — |
| Portail patient (6 pages) | ✅ Porté (sans sudo) | nephro_portal | — |
| WhatsApp rappels | ✅ Porté (sans cr.commit) | nephro_whatsapp | — |
| Paiement Wave | ✅ Porté (sans frais, HMAC) | payment_wave | — |
| Paiement Orange Money | ✅ Porté (sans frais, HMAC) | payment_orange_money | — |
| Traductions FR | ✅ Porté (.po) | nephro_fr | — |

## Fonctionnalités v1 supprimées (volontairement)

| Fonctionnalité | Raison |
|---|---|
| hms.treatment (couche traitement) | Inutile en dialyse chronique |
| RDV 7 états | Remplacé par 4 états |
| Lien auto séance ↔ RDV | Flux séparés |
| acs.patient.evaluation | Doublonne avec bilans |
| acs.pain.level | TransientModel vide |
| nephro.insurer + insurer.claim | Simplifié via pricing.rule |
| Endpoint public ordonnances | Faille de sécurité |
| Frais développeur paiement | Éthique |
| Wizard WhatsApp avec cr.commit | Sécurité |
| Self-request HTTP WhatsApp | Deadlock risk |

## Vérification sécurité

| Point | Vérifié | Fichier de référence |
|---|---|---|
| Zéro sudo() dans controllers | ☐ | Tous controllers/*.py |
| Zéro cr.commit() | ☐ | grep global |
| Zéro auth="public" sur données médicales | ☐ | Tous controllers/*.py |
| ACL deny by default | ☐ | security/ir.model.access.csv |
| Record rules noupdate="1" | ☐ | security/security_rules.xml |
| HMAC sur webhooks paiement | ☐ | payment_*/controllers/main.py |
| Pas de frais cachés | ☐ | payment_*/const.py |
| Pas de CORS wildcard | ☐ | Tous controllers/*.py |

## Vérification tests

| Module | Tests Python | Tests E2E | Vérifié |
|---|---|---|---|
| nephro_core | Workflow + ACL + record rules | Login + navigation | ☐ |
| nephro_dialysis | KT/V + validations + generator | Séance complète | ☐ |
| nephro_bilans | Seuils + cron | Portail graphique | ☐ |
| nephro_complications | Création + résolution | Popup infirmière | ☐ |
| nephro_billing | Auto-invoice + batch | Facture + paiement | ☐ |
| nephro_portal | Record rules (0 sudo) | 5 pages | ☐ |
| payment_wave | HMAC + HTTP codes | — | ☐ |
| payment_orange_money | HMAC + HTTP codes | — | ☐ |
