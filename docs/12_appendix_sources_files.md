# 12 — Appendix: Source Files Mapping

Mapping des fichiers ACS HMS v1 vers les modules nephro v2.

## nephro_core ← acs_hms_base + acs_hms

| Fichier ACS source | Modèle | Fichier v2 | Notes |
|---|---|---|---|
| `acs_hms_base/models/hms_base.py` | `hms.patient` | `nephro_core/models/patient.py` | Fork : renommé `nephro.patient`, supprimé champs inutiles |
| `acs_hms_base/models/physician.py` | `hms.physician` | `nephro_core/models/physician.py` | Fork : renommé `nephro.physician` |
| `acs_hms/models/procedure.py` | `acs.patient.procedure` | `nephro_core/models/procedure.py` | Fork : renommé `nephro.procedure`, 4 états |
| `acs_hms/models/appointment.py` | `hms.appointment` | `nephro_core/models/appointment.py` | Fork : renommé, 4 états au lieu de 7 |
| `acs_hms/models/prescription.py` | `prescription.order` | `nephro_core/models/prescription.py` | Fork : renommé `nephro.prescription` |
| `acs_hms/models/consumable.py` | `acs.consumable.line` | `nephro_core/models/consumable_line.py` | Fork : renommé `nephro.consumable.line` |
| `acs_hms_base/security/security.xml` | Groupes | `nephro_core/security/security.xml` | Reconstruit de zéro, catégorie dédiée |
| `acs_hms_base/security/ir.model.access.csv` | ACL | `nephro_core/security/ir.model.access.csv` | Reconstruit, deny by default |

## nephro_dialysis ← acs_hms_nephrology

| Fichier ACS source | Fichier v2 | Notes |
|---|---|---|
| `acs_hms_nephrology/models/nephrology.py` | `nephro_dialysis/models/procedure.py` | Extension `_inherit`, champs dialyse |
| `acs_hms_nephrology/models/nephrology.py` | `nephro_dialysis/models/schedule.py` | Extrait `nephro.schedule` |
| `acs_hms_nephrology/models/nephrology.py` | `nephro_dialysis/models/station.py` | Extrait `nephro.station` |
| `acs_hms_nephrology/models/session_generator.py` | `nephro_dialysis/models/session_generator.py` | Simplifié, flux unique |
| (nouveau) | `nephro_dialysis/models/vital_sign.py` | Nouveau modèle |
| (nouveau) | `nephro_dialysis/models/dry_weight.py` | Nouveau modèle |

## nephro_bilans ← acs_hms_nephrology_bilans

| Fichier ACS source | Fichier v2 | Notes |
|---|---|---|
| `acs_hms_nephrology_bilans/models/bilan.py` | `nephro_bilans/models/bilan.py` | `chlore` corrigé Char → Float |
| (nouveau) | `nephro_bilans/models/threshold.py` | Seuils configurables |

## nephro_complications ← acs_hms_nephrology_complications

| Fichier ACS source | Fichier v2 | Notes |
|---|---|---|
| `acs_hms_nephrology_complications/models/complication.py` | `nephro_complications/models/complication.py` | Renommé `nephro.complication` |

## nephro_billing ← acs_hms_nephrology_billing

| Fichier ACS source | Fichier v2 | Notes |
|---|---|---|
| `acs_hms_nephrology_billing/models/pricing_rule.py` | `nephro_billing/models/pricing_rule.py` | Simplifié, sans insurer |
| `acs_hms_nephrology_billing/models/procedure.py` | `nephro_billing/models/procedure.py` | Sans `except Exception: pass` |

## Modèles ACS supprimés (non portés)

| Modèle ACS | Raison de suppression |
|---|---|
| `hms.treatment` | Inutile en dialyse chronique (W3) |
| `procedure.group` | Lié au treatment |
| `acs.patient.evaluation` | Doublonne avec bilans (W4) |
| `acs.pain.level` | TransientModel vide sans dépendance |
| `nephro.insurer` | Supprimé (D9), tarification via pricing_rule |
| `nephro.insurer.claim` | Supprimé (D9) |
