# Nephro HMS v2 — Design Complet

**Date :** 2026-09-26
**Projet :** As-Shafi Medical — Plateforme Clinique Dialyse/Néphrologie v2
**Stack :** Odoo 19, Docker, VPS Contabo PRO4 (12 vCPU / 24 GB RAM)
**Approche :** Fork léger ACS HMS + modules domaine propres
**Statut :** Pré-lancement / pilote (pas de migration de données)

---

## Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Architecture des modules](#2-architecture-des-modules)
3. [Data Model](#3-data-model)
4. [Sécurité](#4-sécurité)
5. [Workflows et états](#5-workflows-et-états)
6. [UI/UX](#6-uiux)
7. [Intégrations](#7-intégrations)
8. [Tests](#8-tests)
9. [Conventions et déploiement](#9-conventions-et-déploiement)

---

## 1. Contexte et objectifs

### Pourquoi une v2

La v1 (modules `acs_hms_*`) a accumulé 23 design specs en 3 mois, résultant en :
- 4 flux différents pour créer des séances de dialyse
- Dépendance forte sur ACS HMS propriétaire (OPL-1) avec concepts inutiles (Treatment, Evaluation, 7 états RDV)
- Failles de sécurité : `sudo()` dans tous les controllers portail, `cr.commit()` dans WhatsApp, endpoint public exposant des données médicales, ACL `base.group_user` trop permissives
- Frais cachés de 200 XOF par transaction dans les modules de paiement
- Zéro test unitaire sur les modules de base

### Décisions fondatrices

| Décision | Choix | Raison |
|---|---|---|
| Stack | Odoo 19 propre | Écosystème éprouvé, compta/stock intégrés |
| Socle | Fork léger ACS HMS | Contrôle total, pas de code mort |
| Workflow séance | Flux unique simplifié | 1 générateur → procedures, consultations séparées |
| Paiements | Reconstruire sans frais cachés | Sécurité, éthique, webhook signé |
| Priorités | Tout en même temps | Pré-lancement, pas de migration |
| Documentation | Complète (16 fichiers .md) | Maintenabilité long terme |

### Utilisateurs

| Rôle | Device | Interface |
|---|---|---|
| Médecin néphrologue | PC bureau | Dashboard + dossier patient |
| Infirmière | Tablette (pendant séance) | Interface séance tactile |
| Secrétaire | PC | Planning + patients |
| Agent facturation | PC | Factures + paiements |
| Patient | Téléphone / navigateur | Portail web responsive |
| Administrateur | PC | Configuration complète |

### Périmètre clinique

- 50 à 150 patients dialysés
- 150 à 500 séances par semaine

---

## 2. Architecture des modules

### Arbre de dépendances

```
odoo (base, website, account, product, contacts, mail)
 └── nephro_core                    [Fork ACS — socle]
      │   Patient, Physician, Procedure, Appointment,
      │   Prescription, Consumable, Security Groups
      │
      ├── nephro_dialysis            [Séances enrichies]
      │   │   Signes vitaux, KT/V, poids sec, accès vasculaire,
      │   │   dialyseur, dialysat, planning, générateur masse
      │   │
      │   ├── nephro_bilans          [Bilans biologiques]
      │   │       Bilan, paramètres, seuils, alertes cron
      │   │
      │   ├── nephro_complications   [Complications per-séance]
      │   │       Types, survenue, résolution, alertes
      │   │
      │   ├── nephro_billing         [Facturation]
      │   │       Règles tarifaires, facture auto,
      │   │       consommables → lignes facture, soldes patients
      │   │       Dépend aussi de : account
      │   │
      │   ├── nephro_dashboard       [OWL — dashboards]
      │   │       Dashboard médecin, interface infirmier tablette,
      │   │       widget secrétaire, alertes temps réel
      │   │       Dépend aussi de : nephro_bilans, nephro_complications
      │   │
      │   └── nephro_portal          [Portail patient]
      │           Séances, bilans, RDV, ordonnances, factures
      │           Dépend aussi de : website, nephro_bilans, nephro_billing
      │
      ├── nephro_whatsapp            [Notifications]
      │       Rappels RDV, alertes bilans, fin séance
      │       Dépend aussi de : nephro_dialysis
      │
      └── nephro_fr                  [i18n français]
              Traductions .po complètes pour tous les modules

payment_wave                         [Paiement Wave — indépendant]
      Dépend de : payment

payment_orange_money                 [Paiement Orange Money — indépendant]
      Dépend de : payment
```

### Règles architecturales

| Règle | Raison |
|---|---|
| Zéro `sudo()` dans les controllers | Cause n°1 des failles sécurité v1 |
| Zéro `cr.commit()` | Casse l'isolation transactionnelle |
| ACL restrictives par défaut | v1 donnait CRUD à `base.group_user` |
| Pas de frais cachés | v1 ajoutait 200 XOF silencieusement |
| Champs en anglais, traductions en .po | Standard Odoo, permet le multi-langue |
| Tests unitaires par module | v1 avait 0 tests |
| Webhooks signés (HMAC SHA-256) | v1 acceptait n'importe quelle requête |
| 4 états max par workflow | v1 avait jusqu'à 7 états inutiles |

### Convention de nommage

| Élément | Convention | Exemple |
|---|---|---|
| Module | `nephro_<domaine>` | `nephro_billing` |
| Modèle Python | `nephro.<domaine>.<entité>` | `nephro.dialysis.session` |
| Vue XML ID | `nephro_<domaine>_<modele>_view_<type>` | `nephro_dialysis_session_view_form` |
| Action XML ID | `nephro_<domaine>_<modele>_action` | `nephro_billing_invoice_action` |
| Groupe | `nephro_core.group_nephro_<role>` | `nephro_core.group_nephro_nurse` |
| Menu | `nephro_<domaine>_menu_<nom>` | `nephro_dialysis_menu_sessions` |

---

## 3. Data Model

### 3.1 — nephro_core (fork ACS)

#### nephro.patient

```
nephro.patient (_inherits res.partner)
├── Identité
│   ├── name (Char)                    ← hérité de res.partner
│   ├── hms_id (Char, sequence auto)   ← "HMS/2026/0001"
│   ├── birth_date (Date)
│   ├── gender (Selection: male/female)
│   ├── blood_group (Selection: A+/A-/B+/B-/AB+/AB-/O+/O-)
│   ├── phone / mobile (Char)          ← hérité de res.partner
│   └── emergency_contact (Char)
│
├── Néphrologie
│   ├── is_nephro (Boolean)
│   ├── dialysis_type (Selection: hemodialysis/peritoneal)
│   ├── vascular_access_id (M2o → nephro.vascular.access.type)
│   ├── schedule_id (M2o → nephro.schedule)
│   ├── dry_weight (Float)
│   ├── dialysis_start_date (Date)
│   └── pricing_rule_id (M2o → nephro.pricing.rule)
│
├── Médical
│   ├── physician_id (M2o → nephro.physician)
│   ├── allergy_ids (M2m → nephro.allergy)
│   ├── medical_history (Html)
│   └── active (Boolean, default=True)
│
└── Computed
    ├── age (Integer, computed)
    ├── procedure_count (Integer, computed)
    ├── bilan_count (Integer, computed)
    └── balance_due (Float, computed)
```

#### nephro.physician

```
nephro.physician (_inherits res.partner)
├── specialty (Char)
├── license_number (Char)
├── user_id (M2o → res.users)
├── department (Char)
└── active (Boolean)
```

#### nephro.procedure

```
nephro.procedure
├── Identité
│   ├── name (Char, sequence auto)     ← "DP/2026/0001"
│   ├── patient_id (M2o → nephro.patient, required)
│   ├── physician_id (M2o → nephro.physician)
│   ├── product_id (M2o → product.product)
│   ├── date (Datetime, required)
│   └── duration (Float)
│
├── Workflow
│   ├── state (Selection: scheduled/running/done/cancel)
│   ├── start_time (Datetime)
│   ├── end_time (Datetime)
│   ├── cancel_reason (Text)
│   └── actual_duration (Float, computed)
│
├── Consommables
│   └── consumable_line_ids (O2m → nephro.consumable.line)
│
└── Facturation
    ├── invoice_id (M2o → account.move)
    └── is_invoiced (Boolean, computed)
```

#### nephro.appointment

```
nephro.appointment
├── name (Char, sequence auto)
├── patient_id (M2o → nephro.patient, required)
├── physician_id (M2o → nephro.physician)
├── date (Datetime, required)
├── duration (Float)
├── reason (Text)
├── notes (Text)
├── state (Selection: draft/confirmed/done/cancel)
└── cancel_reason (Text)
```

#### nephro.prescription + nephro.prescription.line

```
nephro.prescription
├── name (Char, sequence auto)
├── patient_id (M2o → nephro.patient, required)
├── physician_id (M2o → nephro.physician, required)
├── date (Date)
├── state (Selection: draft/confirmed/done/cancel)
├── line_ids (O2m → nephro.prescription.line)
└── notes (Text)

nephro.prescription.line
├── prescription_id (M2o → nephro.prescription)
├── product_id (M2o → product.product)
├── dosage (Char)
├── frequency (Char)
├── route (Selection: oral/iv/sc/im)
├── duration_days (Integer)
└── notes (Text)
```

#### nephro.consumable.line

```
nephro.consumable.line
├── procedure_id (M2o → nephro.procedure)
├── product_id (M2o → product.product, required)
├── quantity (Float, default=1)
├── uom_id (M2o → uom.uom)
└── lot_id (M2o → stock.lot)
```

### 3.2 — nephro_dialysis

#### Extension de nephro.procedure (héritage _inherit)

```
nephro.procedure (extension dialyse)
├── Avant séance
│   ├── pre_weight (Float)
│   ├── pre_bp (Char)
│   ├── pre_temp (Float)
│   ├── arrival_status (Selection: normal/tired/pain/fever/other)
│   ├── interdialytic_weight_gain (Float, computed)
│   └── target_uf (Float, computed)
│
├── Paramètres machine
│   ├── schedule_id (M2o → nephro.schedule)
│   ├── station_id (M2o → nephro.station)
│   ├── vascular_access_id (M2o → nephro.vascular.access.type)
│   ├── dialyzer_id (M2o → nephro.dialyzer.type)
│   ├── dialysate_id (M2o → nephro.dialysate.type)
│   ├── blood_flow (Float)
│   ├── dialysate_flow (Float)
│   ├── anticoagulation (Selection: heparin/lmwh/none)
│   ├── anticoag_dose (Float)
│   └── parameter_change_reason (Text)
│
├── Fin de séance
│   ├── post_weight (Float)
│   ├── post_bp (Char)
│   ├── actual_uf (Float, computed)
│   ├── global_tolerance (Selection: good/fair/poor)
│   ├── ktv (Float, computed)
│   ├── ktv_status (Selection: adequate/inadequate, computed)
│   ├── urr (Float, computed)
│   └── end_notes (Text)
│
├── Signes vitaux
│   └── vital_sign_ids (O2m → nephro.vital.sign)
│
└── Machine
    ├── pv_arterial (Float)
    ├── ptm (Float)
    ├── conductivity (Float)
    ├── uf_rate (Float)
    └── vst_start (Float)
```

#### nephro.vital.sign

```
nephro.vital.sign
├── procedure_id (M2o → nephro.procedure, required, ondelete=cascade)
├── timestamp (Datetime, default=now)
├── systolic_bp (Integer)
├── diastolic_bp (Integer)
├── heart_rate (Integer)
├── respiratory_rate (Integer)
├── spo2 (Float)
├── temperature (Float)
├── glycemia (Float)
├── is_alert (Boolean, computed, store=True)
└── notes (Text)
```

#### nephro.schedule

```
nephro.schedule
├── name (Char)
├── code (Char)
├── monday/tuesday/.../sunday (Boolean)
├── start_time (Float)
├── end_time (Float)
├── station_id (M2o → nephro.station)
├── physician_id (M2o → nephro.physician)
├── nurse_ids (M2m → res.users)
├── max_patients (Integer)
└── active (Boolean)
```

#### nephro.station

```
nephro.station
├── name (Char)
├── room (Char)
├── station_type (Selection: standard/isolation)
├── equipment_model (Char)
└── active (Boolean)
```

#### nephro.dry.weight.history

```
nephro.dry.weight.history
├── patient_id (M2o → nephro.patient)
├── date (Date, default=today)
├── weight (Float, required)
├── changed_by_id (M2o → res.users)
└── reason (Text)
```

#### nephro.session.generator (TransientModel)

```
nephro.session.generator (TransientModel)
├── patient_ids (M2m → nephro.patient)
├── schedule_id (M2o → nephro.schedule)
├── date_start (Date, required)
├── date_end (Date, required)
├── exclude_holidays (Boolean, default=True)
├── preview_count (Integer, computed)
└── action_generate() → crée N nephro.procedure
```

#### Tables de configuration

```
nephro.dialyzer.type
nephro.dialysate.type
nephro.vascular.access.type
nephro.holiday
nephro.allergy
```

### 3.3 — nephro_bilans

#### nephro.bilan

```
nephro.bilan
├── Identité
│   ├── name (Char, sequence auto)
│   ├── patient_id (M2o → nephro.patient, required)
│   ├── physician_id (M2o → nephro.physician)
│   ├── date (Date, required)
│   ├── bilan_type (Selection: monthly/quarterly/semi_annual/annual/punctual)
│   └── attachment_ids (M2m → ir.attachment)
│
├── Hématologie
│   ├── hemoglobin (Float)
│   ├── hematocrit (Float)
│   ├── wbc (Float)
│   ├── platelets (Float)
│   └── ferritin (Float)
│
├── Biochimie rénale
│   ├── creatinine (Float)
│   ├── urea_pre (Float)
│   ├── urea_post (Float)
│   └── uric_acid (Float)
│
├── Électrolytes
│   ├── sodium (Float)
│   ├── potassium (Float)
│   ├── calcium (Float)
│   ├── phosphorus (Float)
│   ├── bicarbonate (Float)
│   ├── chloride (Float)
│   └── ca_p_ratio (Float, computed)
│
├── Minéraux-os
│   ├── pth (Float)
│   ├── vitamin_d (Float)
│   └── alkaline_phosphatase (Float)
│
├── Nutrition / Inflammation
│   ├── albumin (Float)
│   ├── total_protein (Float)
│   ├── crp (Float)
│   └── prealbumin (Float)
│
├── Sérologies
│   ├── hbs_ag (Selection: pos/neg/pending)
│   ├── anti_hbs (Selection: pos/neg/pending)
│   ├── anti_hbc (Selection: pos/neg/pending)
│   ├── anti_hcv (Selection: pos/neg/pending)
│   └── anti_hiv (Selection: pos/neg/pending)
│
└── Computed
    ├── alert_count (Integer, computed)
    └── status (Selection: normal/warning/critical, computed)
```

#### nephro.bilan.threshold

```
nephro.bilan.threshold
├── parameter (Selection)
├── min_value (Float)
├── max_value (Float)
├── unit (Char)
└── active (Boolean)
```

### 3.4 — nephro_complications

#### nephro.complication

```
nephro.complication
├── procedure_id (M2o → nephro.procedure, required)
├── complication_type (Selection: hypotension/cramps/nausea/chest_pain/fever/pruritus/early_stop/other)
├── occurrence_time (Datetime, default=now)
├── bp_at_occurrence (Char)
├── action_taken (Text)
├── resolution (Selection: resolved/partial/unresolved)
├── early_stop_minutes (Integer)
└── notes (Text)
```

### 3.5 — nephro_billing

#### nephro.pricing.rule

```
nephro.pricing.rule
├── name (Char, required)
├── price (Float, required)
├── tax_rate (Float)
├── insurance_coverage (Float)
├── patient_share (Float, computed)
└── active (Boolean)
```

### 3.6 — Diagramme des relations

```
nephro.patient ─────────────────────────────────────┐
  │ 1                                                │
  ├──→ M nephro.procedure (séances)                  │
  │         │ 1                                      │
  │         ├──→ M nephro.vital.sign                 │
  │         ├──→ M nephro.complication               │
  │         ├──→ M nephro.consumable.line            │
  │         └──→ 1 account.move (facture)            │
  │                                                  │
  ├──→ M nephro.bilan                                │
  ├──→ M nephro.appointment                          │
  ├──→ M nephro.prescription                         │
  ├──→ M nephro.dry.weight.history                   │
  ├──→ 1 nephro.schedule                             │
  ├──→ 1 nephro.physician                            │
  └──→ 1 nephro.pricing.rule                         │
                                                     │
nephro.schedule ──→ 1 nephro.station                 │
                ──→ 1 nephro.physician               │
                ──→ M res.users (infirmières)         │
```

---

## 4. Sécurité

### 4.1 — Hiérarchie des groupes

```
nephro_core.group_nephro_user          ← Base : lecture seule
    ├── nephro_core.group_nephro_secretary
    ├── nephro_core.group_nephro_nurse
    ├── nephro_core.group_nephro_billing
    ├── nephro_core.group_nephro_doctor
    │       └── nephro_core.group_nephro_manager
    └── (portal user via base.group_portal)
```

Catégorie de module dédiée `module_category_nephrology` — aucun groupe ne descend de `base.group_user`.

### 4.2 — Matrice ACL

#### nephro_core

| Modèle | User | Secretary | Nurse | Billing | Doctor | Manager |
|---|---|---|---|---|---|---|
| nephro.patient | R | RCWD | R | R | RCW | RCWD |
| nephro.physician | R | R | R | R | R | RCWD |
| nephro.procedure | R | RC | RCW | R | RCWD | RCWD |
| nephro.appointment | R | RCWD | R | — | RCWD | RCWD |
| nephro.prescription | R | R | R | R | RCWD | RCWD |
| nephro.prescription.line | R | R | R | R | RCWD | RCWD |
| nephro.consumable.line | R | R | RCW | R | RCWD | RCWD |

#### nephro_dialysis

| Modèle | User | Secretary | Nurse | Billing | Doctor | Manager |
|---|---|---|---|---|---|---|
| nephro.vital.sign | — | — | RCWD | — | RCWD | RCWD |
| nephro.schedule | R | R | R | — | RCW | RCWD |
| nephro.station | R | R | R | — | R | RCWD |
| nephro.dry.weight.history | — | — | — | — | RCWD | RCWD |
| nephro.session.generator | — | RC | — | — | RC | RCWD |
| nephro.dialyzer.type | — | — | R | — | R | RCWD |
| nephro.dialysate.type | — | — | R | — | R | RCWD |
| nephro.vascular.access.type | — | — | R | — | R | RCWD |
| nephro.holiday | — | R | — | — | — | RCWD |

#### nephro_bilans / nephro_complications / nephro_billing

| Modèle | User | Secretary | Nurse | Billing | Doctor | Manager |
|---|---|---|---|---|---|---|
| nephro.bilan | — | — | R | — | RCWD | RCWD |
| nephro.bilan.threshold | — | — | — | — | RCW | RCWD |
| nephro.complication | — | — | RCW | — | RCWD | RCWD |
| nephro.pricing.rule | — | R | — | R | R | RCWD |

### 4.3 — Record Rules

#### Infirmière : séances de ses plannings uniquement

```python
domain: [('schedule_id.nurse_ids', 'in', [user.id])]
```

#### Portail patient : ses propres données uniquement

```python
domain: [('patient_id.partner_id', '=', user.partner_id.id)]
# Appliqué sur : nephro.procedure, nephro.bilan, nephro.appointment,
#                nephro.prescription, account.move
```

Toutes les record rules en `noupdate="1"`.

### 4.4 — Règles des endpoints

| Règle | Détail |
|---|---|
| Pas de `auth="public"` sur données médicales | Toutes routes médicales en `auth="user"` |
| Pas de `sudo()` dans les controllers | Les record rules filtrent |
| Webhook paiement signé | HMAC SHA-256 |
| Validation de longueur | cancel_reason, notes : max 2000 chars |

---

## 5. Workflows et états

### 5.1 — Séance de dialyse (flux principal et unique)

```
Générateur masse → N nephro.procedure (état SCHEDULED)

    SCHEDULED ──→ RUNNING ──→ DONE ──→ [auto-facture optionnelle]
        │                       
        └──→ CANCEL          RUNNING ──→ CANCEL (médecin uniquement)
```

| Transition | Qui | Validation |
|---|---|---|
| → scheduled | Wizard générateur | Planning + jours fériés |
| scheduled → running | Infirmière | pre_weight + pre_bp obligatoires |
| running → done | Infirmière | post_weight obligatoire, KT/V auto |
| scheduled → cancel | Secrétaire / Médecin | cancel_reason obligatoire |
| running → cancel | Médecin uniquement | cancel_reason + complication auto |

Verrou : le dashboard infirmier appelle `action_start()` / `action_done()` / `action_cancel()` — jamais `orm.write({state})` direct.

### 5.2 — Consultation

```
DRAFT ──→ CONFIRMED ──→ DONE
  │
  └──→ CANCEL
```

Aucun lien automatique avec les séances. Flux totalement séparé.

### 5.3 — Ordonnance

```
DRAFT ──→ CONFIRMED ──→ DONE
  │
  └──→ CANCEL
```

### 5.4 — Facturation

Flux natif Odoo `account.move` : `DRAFT → POSTED → PAID` (ou `REVERSED` via avoir). Aucun état custom.

Création automatique optionnelle depuis `action_done()` si `nephro_billing.auto_invoice = True`.

Facturation groupée via wizard `nephro.batch.invoice.wizard` avec prévisualisation.

### 5.5 — Bilan biologique

Pas de workflow à états. Enregistrement de données → computed auto (badges, alertes, status) → propagation dashboard + portail + WhatsApp.

Cron quotidien : alerte si patient sans bilan depuis > 30 jours.

### 5.6 — Complication

Création pendant séance RUNNING → nephro.complication → alerte dashboard médecin (bus temps réel). Si resolution = unresolved à la clôture → alerte rouge persistante.

---

## 6. UI/UX

### 6.1 — Menus par rôle

```
Néphrologie                                    Sec  Inf  Fac  Med  Adm
├── Patients                          (seq 10)  ✓    —    —    ✓    ✓
├── Rendez-vous                       (seq 20)  ✓    —    —    ✓    ✓
├── Hémodialyses                      (seq 30)  ✓    R    R    ✓    ✓
├── Ordonnances                       (seq 40)  R    —    —    ✓    ✓
├── Bilans biologiques                (seq 50)  —    R    —    ✓    ✓
├── Générer séances en masse          (seq 60)  ✓    —    —    ✓    ✓
├── Dashboard médecin                 (seq 70)  —    —    —    ✓    ✓
├── Interface infirmier               (seq 80)  —    ✓    —    —    ✓
├── Facturation dialyse               (seq 90)  —    —    ✓    —    ✓
│   ├── Séances non facturées
│   ├── Toutes les factures
│   ├── Soldes patients
│   ├── Facturation groupée
│   └── Rapports
└── Configuration                     (seq 100) —    —    —    —    ✓
```

Redirections après login : Infirmière → Dashboard infirmier, Facturation → Séances non facturées, Médecin/Secrétaire → Liste patients.

### 6.2 — Dashboard médecin (OWL)

Composants :
- DoctorKpiBar : 4 compteurs KPI (séances jour, terminées, en cours, alertes)
- StationGrid : tableau postes temps réel (poste, patient, statut, durée)
- AlertPanel : sidebar alertes (critique rouge, attention orange)
- PatientSlidePanel : panel latéral dossier patient (clic sur ligne)
- MonthlyCharts : graphiques Chart.js (KT/V, complications, occupation)

Endpoint JSON `/nephro/dashboard/doctor/data` (auth=user, pas de sudo). Rafraîchissement 30s + alertes temps réel via bus.Bus Odoo.

### 6.3 — Interface infirmier tablette (OWL)

Optimisée tactile — grands boutons, lisible à 50cm.

Écrans :
1. PatientCardGrid : cartes par poste (statut, timer, actions)
2. SessionView : formulaire séance (pré-dialyse, machine, signes vitaux)
3. ComplicationPopup : sélection type rapide, TA, action, résolution
4. EndSessionForm : poids post, KT/V auto, tolérance, validation

Toutes les transitions via `this.orm.call('nephro.procedure', 'action_*')`.

### 6.4 — Portail patient (QWeb)

Routes : `/my/nephro`, `/my/seances`, `/my/bilans`, `/my/rdv`, `/my/ordonnances`, `/my/factures`

Principes : pas de sudo (record rules), langage simplifié, pagination 20/page, mobile-first 375px, téléchargement PDF QWeb.

### 6.5 — Widget secrétaire

Composant OWL en haut de la liste patients : compteurs jour (total, terminés, en cours, programmés, absents), postes occupés.

---

## 7. Intégrations

### 7.1 — WhatsApp (WasenderAPI)

Service stateless `WhatsAppSender.send_message(env, phone, message, attachment)`. Pas de wizard, pas de cr.commit, pas de self-request HTTP, pas de CORS.

Attachements : URL signée temporaire (1h), pas de `public: True` permanent.

Événements : Rappel J-1 (cron 18h), Rappel J (cron 6h30), Fin séance (action_done), Bilan critique (cron), Annulation patient (portail), Absence (secrétaire).

### 7.2 — Paiement Wave

Zéro frais développeur. URL retour via `get_base_url()` (pas hardcodé). HMAC SHA-256 sur les webhooks retour/annulation. Codes HTTP : 200/400/500 selon le cas. Warning UI clair en mode test (= argent réel).

### 7.3 — Paiement Orange Money

Mêmes corrections que Wave. Auteur manifest `'As-Shafi Medical'`. Référence lookup exact `=` (pas LIKE). Index SQL dans migration script (pas dans `init()`).

### 7.4 — Exports

PDF (QWeb) : fiche séance, bilan, ordonnance, facture, attestation soins annuelle.
Excel (xlsxwriter) : séances par période, rapport financier mensuel, liste patients.

---

## 8. Tests

### 8.1 — Deux niveaux

1. **Tests unitaires Python** (Odoo TransactionCase) — rapides, par module
2. **Tests E2E Playwright** — parcours utilisateur complets par rôle

### 8.2 — Structure

Chaque module a un dossier `tests/` avec `common.py` (classe de base + données) + fichiers `test_*.py`.

Classe de base `NephroTestCommon` : crée utilisateurs par rôle (secretary, nurse, doctor, billing, manager), patient de test, médecin, station, planning.

### 8.3 — Couverture minimale

| Module | Seuil |
|---|---|
| nephro_core | 100% des transitions d'état + ACL 5 rôles + record rules |
| nephro_dialysis | 100% des champs computed (KT/V, UF, alertes) |
| nephro_bilans | 100% des alertes + cron overdue |
| nephro_complications | 100% des types |
| nephro_billing | 100% du flux facturation (auto + batch) |
| nephro_portal | 0 fuite de données (record rules, pas de sudo) |
| payment_wave / orange_money | 100% des codes retour + HMAC |

### 8.4 — Playwright

5 specs par rôle : `01_secretary.spec.js`, `02_doctor.spec.js`, `03_nurse.spec.js`, `04_billing.spec.js`, `05_portal.spec.js`. Helper partagé `loginAs(page, role)`.

---

## 9. Conventions et déploiement

### 9.1 — Code Python

- Imports : stdlib → odoo → locaux
- Champs : regroupés par thème avec commentaires
- Compute : toujours `@api.depends()`
- Logger : `_logger.info("msg %s", arg)` — jamais f-string
- Strings : anglais, traductions en .po
- Interdit : `sudo()` controllers, `cr.commit()`, `except Exception: pass`, `requests.get(self)`

### 9.2 — Manifests

- Version : `19.0.2.x.y`
- Author : `'As-Shafi Medical'`
- License : `'LGPL-3'`
- `installable: True` toujours explicite
- `application: True` uniquement pour nephro_core
- Ordre data : security → data → views → report → menu

### 9.3 — i18n

Module `nephro_fr` centralise tous les `.po` français. Champs en anglais dans le code. Extraction via `odoo-bin --i18n-export`.

### 9.4 — Déploiement

Docker / Odoo 19 / PostgreSQL / Nginx reverse proxy + SSL.

Installation : `odoo-bin -d asshafi -i nephro_core,nephro_dialysis,...`
Mise à jour : `odoo-bin -d asshafi -u nephro_core,...`
Tests : `odoo-bin -d test_asshafi --test-enable -i nephro_core,...`

### 9.5 — Structure docs/

16 fichiers .md + guide/ + superpowers/ couvrant : overview, features, data model, API, UI, decisions, business model, intégrations, conventions, issues v1, rebuild plan, appendix sources, gap fill, contrat qualité, orchestration, journal décisions, debug tracker.
