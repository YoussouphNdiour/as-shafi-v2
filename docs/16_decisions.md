# 16 — Decision Journal

Journal chronologique des décisions prises pendant le développement v2.

## 2026-09-26 — Brainstorming initial

### D1 — Stack : Odoo 19 propre
- **Contexte** : 3 options évaluées (Odoo propre, Next.js standalone, hybride)
- **Décision** : Option A — Odoo 19 avec modules nettoyés
- **Raison** : Écosystème éprouvé, compta/stock intégrés, pas de double maintenance

### D2 — Socle : Fork léger ACS HMS
- **Contexte** : 3 options (garder ACS, reconstruire from scratch, fork léger)
- **Décision** : Fork léger — copier les modèles utiles, supprimer le reste
- **Raison** : Contrôle total sans repartir de zéro

### D3 — Statut : Pré-lancement / pilote
- **Impact** : Pas de migration de données, on part de zéro
- **Conséquence** : Pas besoin de scripts de migration, liberté totale sur le schéma

### D4 — Workflow : Flux unique simplifié
- **Contexte** : v1 avait 4 flux différents pour créer des séances
- **Décision** : 1 seul flux (wizard générateur → nephro.procedure)
- **Raison** : Simplification, moins de bugs, formation utilisateur plus simple

### D5 — Paiements : Reconstruire sans frais cachés
- **Contexte** : v1 ajoutait 200 XOF par transaction
- **Décision** : Zéro frais développeur, webhook signé HMAC
- **Raison** : Éthique, sécurité, conformité

### D6 — Priorités : Tout en même temps
- **Contexte** : 3 options de priorisation
- **Décision** : Reconstruction complète simultanée
- **Raison** : Pré-lancement, pas de contrainte de migration incrémentale

### D7 — Documentation : Complète (16 fichiers)
- **Raison** : Maintenabilité long terme, onboarding nouveaux développeurs

### D8 — Modèles ACS conservés
- patient, physician, procedure, appointment (4 états), prescription, consumable.line
- Groupes de sécurité reconstruits de zéro

### D9 — nephro.insurer supprimé
- **Raison** : La tarification est gérée uniquement via `nephro.pricing.rule` liée au patient
- **Impact** : Suppression de nephro.insurer, nephro.insurer.claim, champs insurer_id

---

*Ajouter les décisions futures ci-dessous au fur et à mesure de l'implémentation.*
