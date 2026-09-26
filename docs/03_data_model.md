# 03 — Data Model

Référence complète de tous les modèles, champs et relations.

## nephro_core

### nephro.patient (_inherits res.partner)

| Champ | Type | Description |
|---|---|---|
| name | Char | Nom complet (hérité res.partner) |
| hms_id | Char | Numéro HMS auto (séquence) |
| birth_date | Date | Date de naissance |
| gender | Selection (male/female) | Genre |
| blood_group | Selection | Groupe sanguin (A+/A-/B+/B-/AB+/AB-/O+/O-) |
| phone / mobile | Char | Téléphone (hérité res.partner) |
| emergency_contact | Char | Contact d'urgence |
| is_nephro | Boolean | Active le suivi dialyse |
| dialysis_type | Selection (hemodialysis/peritoneal) | Type de dialyse |
| vascular_access_id | M2o → nephro.vascular.access.type | Accès vasculaire |
| schedule_id | M2o → nephro.schedule | Planning dialyse |
| dry_weight | Float | Poids sec actuel (kg) |
| dialysis_start_date | Date | Date début dialyse |
| pricing_rule_id | M2o → nephro.pricing.rule | Tarification |
| physician_id | M2o → nephro.physician | Médecin référent |
| allergy_ids | M2m → nephro.allergy | Allergies |
| medical_history | Html | Antécédents médicaux |
| active | Boolean | Actif (default=True) |
| age | Integer | Âge (computed) |
| procedure_count | Integer | Nb séances (computed) |
| bilan_count | Integer | Nb bilans (computed) |
| balance_due | Float | Solde impayé (computed) |

### nephro.physician (_inherits res.partner)

| Champ | Type | Description |
|---|---|---|
| specialty | Char | Spécialité |
| license_number | Char | Numéro de licence |
| user_id | M2o → res.users | Utilisateur Odoo lié |
| department | Char | Service |
| active | Boolean | Actif |

### nephro.procedure

| Champ | Type | Description |
|---|---|---|
| name | Char | Référence auto (DP/2026/0001) |
| patient_id | M2o → nephro.patient | Patient (required) |
| physician_id | M2o → nephro.physician | Médecin |
| product_id | M2o → product.product | Type procédure facturable |
| date | Datetime | Date/heure (required) |
| duration | Float | Durée prévue (heures) |
| state | Selection | scheduled/running/done/cancel |
| start_time | Datetime | Heure début effective |
| end_time | Datetime | Heure fin effective |
| cancel_reason | Text | Motif annulation |
| actual_duration | Float | Durée effective (computed) |
| consumable_line_ids | O2m → nephro.consumable.line | Consommables |
| invoice_id | M2o → account.move | Facture liée |
| is_invoiced | Boolean | Facturée (computed) |

### nephro.appointment

| Champ | Type | Description |
|---|---|---|
| name | Char | Référence auto (RDV/2026/0001) |
| patient_id | M2o → nephro.patient | Patient (required) |
| physician_id | M2o → nephro.physician | Médecin |
| date | Datetime | Date/heure (required) |
| duration | Float | Durée |
| reason | Text | Motif |
| notes | Text | Notes |
| state | Selection | draft/confirmed/done/cancel |
| cancel_reason | Text | Motif annulation |

### nephro.prescription + nephro.prescription.line

| Champ (prescription) | Type | Description |
|---|---|---|
| name | Char | Référence auto (ORD/2026/0001) |
| patient_id | M2o → nephro.patient | Patient (required) |
| physician_id | M2o → nephro.physician | Médecin (required) |
| date | Date | Date |
| state | Selection | draft/confirmed/done/cancel |
| line_ids | O2m → nephro.prescription.line | Lignes |
| notes | Text | Notes |

| Champ (line) | Type | Description |
|---|---|---|
| prescription_id | M2o → nephro.prescription | Ordonnance |
| product_id | M2o → product.product | Médicament |
| dosage | Char | Ex: "40 000 UI / semaine" |
| frequency | Char | Ex: "3x/semaine en IV" |
| route | Selection (oral/iv/sc/im) | Voie d'administration |
| duration_days | Integer | Durée en jours |
| notes | Text | Notes |

### nephro.consumable.line

| Champ | Type | Description |
|---|---|---|
| procedure_id | M2o → nephro.procedure | Séance |
| product_id | M2o → product.product | Produit (required) |
| quantity | Float | Quantité (default=1) |
| uom_id | M2o → uom.uom | Unité de mesure |
| lot_id | M2o → stock.lot | Traçabilité |

---

## nephro_dialysis

### Extension nephro.procedure (_inherit)

| Champ | Type | Description |
|---|---|---|
| pre_weight | Float | Poids arrivée (kg) |
| pre_bp | Char | TA pré-dialyse ("130/80") |
| pre_temp | Float | Température pré |
| arrival_status | Selection | normal/tired/pain/fever/other |
| interdialytic_weight_gain | Float | Gain interdialytique (computed) |
| target_uf | Float | UF cible (computed) |
| schedule_id | M2o → nephro.schedule | Planning |
| station_id | M2o → nephro.station | Poste |
| vascular_access_id | M2o → nephro.vascular.access.type | Accès vasculaire |
| dialyzer_id | M2o → nephro.dialyzer.type | Dialyseur |
| dialysate_id | M2o → nephro.dialysate.type | Dialysat |
| blood_flow | Float | Débit sanguin (mL/min) |
| dialysate_flow | Float | Débit dialysat (mL/min) |
| anticoagulation | Selection (heparin/lmwh/none) | Anticoagulation |
| anticoag_dose | Float | Dose anticoagulant |
| parameter_change_reason | Text | Motif changement protocole |
| post_weight | Float | Poids sortie (kg) |
| post_bp | Char | TA post-dialyse |
| actual_uf | Float | UF réelle (computed) |
| global_tolerance | Selection (good/fair/poor) | Tolérance |
| ktv | Float | KT/V Daugirdas II (computed) |
| ktv_status | Selection (adequate/inadequate) | Statut KT/V (computed) |
| urr | Float | URR (computed) |
| end_notes | Text | Notes fin |
| vital_sign_ids | O2m → nephro.vital.sign | Signes vitaux |
| pv_arterial | Float | Pression veineuse |
| ptm | Float | Pression transmembranaire |
| conductivity | Float | Conductivité |
| uf_rate | Float | Débit UF (mL/h) |
| vst_start | Float | VST début |

### nephro.vital.sign

| Champ | Type | Description |
|---|---|---|
| procedure_id | M2o → nephro.procedure | Séance (required, cascade) |
| timestamp | Datetime | Horodatage (default=now) |
| systolic_bp | Integer | TA systolique |
| diastolic_bp | Integer | TA diastolique |
| heart_rate | Integer | Fréquence cardiaque |
| respiratory_rate | Integer | Fréquence respiratoire |
| spo2 | Float | SpO2 (%) |
| temperature | Float | Température (°C) |
| glycemia | Float | Glycémie |
| is_alert | Boolean | Alerte (computed, store, systolic < 90) |
| notes | Text | Notes |

### nephro.schedule

| Champ | Type | Description |
|---|---|---|
| name | Char | Nom |
| code | Char | Code court |
| monday-sunday | Boolean | Jours de la semaine (7 champs) |
| start_time | Float | Heure début (8.0 = 08:00) |
| end_time | Float | Heure fin |
| station_id | M2o → nephro.station | Poste par défaut |
| physician_id | M2o → nephro.physician | Médecin référent |
| nurse_ids | M2m → res.users | Infirmières assignées |
| max_patients | Integer | Capacité max |
| active | Boolean | Actif |

### nephro.station

| Champ | Type | Description |
|---|---|---|
| name | Char | Nom ("Poste 3 - Salle B") |
| room | Char | Salle/secteur |
| station_type | Selection (standard/isolation) | Type |
| equipment_model | Char | Modèle générateur |
| active | Boolean | Actif |

### nephro.dry.weight.history

| Champ | Type | Description |
|---|---|---|
| patient_id | M2o → nephro.patient | Patient |
| date | Date | Date (default=today) |
| weight | Float | Poids sec (required) |
| changed_by_id | M2o → res.users | Modifié par |
| reason | Text | Motif |

### Tables de configuration

- `nephro.dialyzer.type` : name, active
- `nephro.dialysate.type` : name, active
- `nephro.vascular.access.type` : name, active
- `nephro.holiday` : name, date, active
- `nephro.allergy` : name, active

---

## nephro_bilans

### nephro.bilan

| Groupe | Champs |
|---|---|
| Identité | name (seq), patient_id, physician_id, date, bilan_type, attachment_ids |
| Hématologie | hemoglobin, hematocrit, wbc, platelets, ferritin |
| Biochimie rénale | creatinine, urea_pre, urea_post, uric_acid |
| Électrolytes | sodium, potassium, calcium, phosphorus, bicarbonate, chloride, ca_p_ratio (computed) |
| Minéraux-os | pth, vitamin_d, alkaline_phosphatase |
| Nutrition/Inflammation | albumin, total_protein, crp, prealbumin |
| Sérologies | hbs_ag, anti_hbs, anti_hbc, anti_hcv, anti_hiv (tous Selection: pos/neg/pending) |
| Computed | alert_count, status (normal/warning/critical) |

### nephro.bilan.threshold

| Champ | Type | Description |
|---|---|---|
| parameter | Selection | Paramètre biologique |
| min_value | Float | Seuil min |
| max_value | Float | Seuil max |
| unit | Char | Unité |
| active | Boolean | Actif |

---

## nephro_complications

### nephro.complication

| Champ | Type | Description |
|---|---|---|
| procedure_id | M2o → nephro.procedure | Séance (required) |
| complication_type | Selection | hypotension/cramps/nausea/chest_pain/fever/pruritus/early_stop/other |
| occurrence_time | Datetime | Heure survenue (default=now) |
| bp_at_occurrence | Char | TA au moment |
| action_taken | Text | Action prise |
| resolution | Selection | resolved/partial/unresolved |
| early_stop_minutes | Integer | Durée arrêt (si arrêt prématuré) |
| notes | Text | Notes |

---

## nephro_billing

### nephro.pricing.rule

| Champ | Type | Description |
|---|---|---|
| name | Char | Nom (required) |
| price | Float | Prix HT (required) |
| tax_rate | Float | Taux TVA (%) |
| insurance_coverage | Float | Couverture (%) |
| patient_share | Float | Part patient (computed) |
| active | Boolean | Actif |
