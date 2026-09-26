# 07 — Business Model

## Tarification

### Règles tarifaires (nephro.pricing.rule)

Chaque patient est associé à une règle tarifaire qui détermine le prix de ses séances.

| Champ | Description |
|---|---|
| name | Nom de la règle (ex: "Forfait IPRES", "AMU", "Privé", "Indigent") |
| price | Prix HT par séance |
| tax_rate | Taux TVA en % |
| insurance_coverage | % pris en charge par la couverture |
| patient_share | % à la charge du patient (computed: 100 - insurance_coverage) |

### Exemples de tarification

| Règle | Prix séance | Couverture | Part patient |
|---|---|---|---|
| Forfait IPRES | 25 000 CFA | 80% | 20% (5 000 CFA) |
| AMU | 25 000 CFA | 100% | 0% |
| Privé | 35 000 CFA | 0% | 100% (35 000 CFA) |
| Indigent | 25 000 CFA | 100% | 0% |

### Lien patient → tarif

`nephro.patient.pricing_rule_id` → Many2one vers `nephro.pricing.rule`. Appliqué automatiquement à chaque facturation.

## Flux financier

```
Séance terminée (action_done)
    │
    ├── Auto-facture activée ?
    │   ├── Oui → Crée account.move (draft)
    │   │         ├── Ligne procédure (prix selon pricing_rule)
    │   │         └── Lignes consommables (rein, lignes sang, etc.)
    │   │
    │   └── Non → Séance ajoutée à "Séances non facturées"
    │
    ▼
Agent facturation
    ├── Facture individuelle → Confirme → Enregistre paiement
    └── Facturation groupée (wizard)
        ├── Sélection patients + période
        ├── Prévisualisation (nb séances, montant, part patient)
        └── Crée N factures d'un coup
```

## Solde patient

`nephro.patient.balance_due` = somme des factures confirmées non payées.

Badges : ✅ À jour (solde = 0) / ⚠️ Retard (solde > 0) / 🔴 Impayé (solde > seuil configurable).

## Paiements acceptés

- Espèces (enregistrement manuel)
- Virement bancaire
- Chèque
- Wave (module payment_wave)
- Orange Money (module payment_orange_money)

Pas de frais cachés sur les paiements mobiles.
