# 04 — API Spec

## Endpoints JSON internes (OWL dashboards)

### Dashboard médecin

**GET** `/nephro/dashboard/doctor/data`
- Auth : `user` (group_nephro_doctor)
- Rafraîchissement : 30s (setInterval) + alertes temps réel (bus.Bus)
- Response :

```json
{
  "kpis": {
    "total_today": 12,
    "done_today": 10,
    "running": 1,
    "alerts": 2
  },
  "stations": [
    {
      "station_id": 1,
      "station_name": "Poste 1-A",
      "patient_name": "A. Fall",
      "procedure_id": 142,
      "state": "done",
      "duration": "4h02",
      "ktv": 1.4,
      "has_alert": false
    }
  ],
  "alerts": [
    {
      "type": "critical",
      "category": "hypotension",
      "patient_name": "S. Diouf",
      "station": "Poste 3-B",
      "detail": "TA 85/50 à 10:00",
      "procedure_id": 145
    }
  ],
  "charts": {
    "monthly_ktv": [1.32, 1.35, 1.38, 1.34, 1.36, 1.35],
    "complications_by_type": {"hypotension": 8, "cramps": 3, "nausea": 1},
    "occupancy_by_day": {"mon": 92, "tue": 0, "wed": 88, "thu": 0, "fri": 95}
  }
}
```

### Interface infirmier

**GET** `/nephro/dashboard/nurse/data`
- Auth : `user` (group_nephro_nurse)
- Filtrage automatique par planning de l'infirmière (record rules)
- Response :

```json
{
  "patients": [
    {
      "procedure_id": 145,
      "patient_name": "S. Diouf",
      "station": "Poste 3-B",
      "state": "running",
      "start_time": "2026-06-12 08:30:00",
      "elapsed_minutes": 155,
      "duration_planned": 240,
      "has_complication": false,
      "vital_signs_count": 4
    }
  ]
}
```

### Widget secrétaire

**GET** `/nephro/dashboard/secretary/data`
- Auth : `user` (group_nephro_secretary)
- Response :

```json
{
  "total": 12,
  "done": 8,
  "running": 3,
  "scheduled": 1,
  "absent": 0,
  "stations_occupied": 4,
  "stations_total": 5,
  "next_session": {"patient": "I. Niang", "time": "13:00"}
}
```

## Portail patient (routes QWeb)

| Route | Méthode | Auth | Description |
|---|---|---|---|
| `/my/nephro` | GET | user (portal) | Tableau de bord patient |
| `/my/seances` | GET | user (portal) | Liste séances paginée |
| `/my/seances/<int:id>` | GET | user (portal) | Détail séance |
| `/my/bilans` | GET | user (portal) | Liste bilans + graphique |
| `/my/bilans/<int:id>` | GET | user (portal) | Détail bilan |
| `/my/rdv` | GET | user (portal) | Liste RDV |
| `/my/rdv/<int:id>/cancel` | POST | user (portal) | Annuler un RDV |
| `/my/ordonnances` | GET | user (portal) | Liste ordonnances |
| `/my/factures` | GET | user (portal) | Liste factures + solde |

Toutes les routes utilisent les record rules (pas de sudo). Pagination : 20 items/page.

## Webhooks paiement

### Wave

| Route | Méthode | Auth | Description |
|---|---|---|---|
| `/payment/wave/return` | GET | public | Retour après paiement (ref + sig HMAC) |
| `/payment/wave/cancel` | GET | public | Annulation paiement (ref + sig HMAC) |
| `/payment/wave/webhook` | POST | public | Notification async Wave |

### Orange Money

| Route | Méthode | Auth | Description |
|---|---|---|---|
| `/payment/orange/return` | GET | public | Retour après paiement (ref + sig HMAC) |
| `/payment/orange/cancel` | GET | public | Annulation paiement (ref + sig HMAC) |
| `/payment/orange/webhook` | POST | public | Notification async Orange Money |

Signature HMAC SHA-256 : `hmac(secret_key, reference)`. Vérification obligatoire avant traitement. Codes HTTP : 200 (OK), 400 (signature invalide), 404 (transaction inconnue), 500 (erreur serveur).
