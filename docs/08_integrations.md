# 08 — Integrations

## WhatsApp (WasenderAPI)

### Configuration

Paramètres système (`ir.config_parameter`) :
- `nephro_whatsapp.api_key` : clé API WasenderAPI
- `nephro_whatsapp.device_id` : ID du device WhatsApp
- `nephro_whatsapp.base_url` : URL API (default: `https://app.wasender.com/api/v1`)
- `nephro_whatsapp.enabled` : activer/désactiver (Boolean)

### Service d'envoi

`WhatsAppSender.send_message(env, phone, message, attachment=None)` — service stateless.

Principes v2 :
- Pas de wizard, pas de `cr.commit()`, pas de self-request HTTP
- Attachements via URL signée temporaire (1h), pas de `public: True` permanent
- Pas de header CORS
- Logger `%s` (pas f-string)
- Timeout 15s sur les requêtes

### Événements

| Événement | Déclencheur | Cron / Action | Message type |
|---|---|---|---|
| Rappel J-1 | Cron quotidien 18h | `_cron_send_j1_reminders()` | "Rappel : séance demain..." |
| Rappel J | Cron quotidien 6h30 | `_cron_send_j_reminders()` | "Votre séance est prévue aujourd'hui..." |
| Fin séance | `action_done()` | Direct | "Séance terminée. KT/V : {ktv}" |
| Bilan critique | Cron post-saisie | `_cron_alert_critical_bilans()` | "Résultats disponibles. Médecin informé." |
| Annulation patient | Portail POST | Direct | "Annulation confirmée." |
| Absence signalée | Secrétaire → action | Direct (vers médecin) | "Patient {nom} absent le {date}" |

---

## Paiement Wave

### Corrections vs v1

| v1 | v2 |
|---|---|
| 200 XOF frais cachés | Zéro frais |
| `base_url = 'https://as-shafi.com'` | `get_base_url()` dynamique |
| Aucune validation webhook | HMAC SHA-256 |
| Retourne toujours HTTP 200 | 200/400/404/500 |
| URL test = URL prod | Warning UI "mode test = argent réel" |
| Scripts dans le module | Scripts dans `tests/` |

### Flux

```
Portail → Payer → /payment/wave/create
  → Crée session Wave (API)
  → return_url + cancel_url avec HMAC(ref, secret)
  → Redirection Wave checkout
  → Retour /payment/wave/return?ref=X&sig=Y
    → Vérifier HMAC
    → Vérifier statut via API Wave
    → tx.state = done | pending | cancel
```

### Signature HMAC

```python
signature = hmac.new(secret.encode(), reference.encode(), hashlib.sha256).hexdigest()
# Vérification : hmac.compare_digest(expected, received)
```

---

## Paiement Orange Money

Même architecture que Wave. Corrections identiques.

Spécificités :
- Auteur manifest : `'As-Shafi Medical'` (pas `'Odoo S.A.'`)
- Référence lookup : `('reference', '=', ref)` exact (pas LIKE)
- Index SQL : dans migration script (pas dans `init()`)

---

## Exports

### PDF (QWeb natif Odoo)

| Rapport | Modèle source | Déclencheur |
|---|---|---|
| Fiche séance | nephro.procedure | Bouton "Imprimer" |
| Bilan biologique | nephro.bilan | Bouton "Imprimer" / portail |
| Ordonnance | nephro.prescription | Bouton "Imprimer" / portail |
| Facture | account.move | Bouton standard Odoo |
| Attestation soins | nephro.patient | Wizard annuel |

### Excel (xlsxwriter)

| Export | Contenu | Accès |
|---|---|---|
| Séances par période | Date, patient, durée, KT/V, UF, tolérance | Médecin / Admin |
| Rapport financier | CA, encaissé, en attente, par tarif | Facturation / Admin |
| Liste patients | Données démographiques, planning, médecin | Secrétaire / Admin |
