# 05 — UI Spec

## Menus par rôle

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
    ├── Plannings dialyse
    ├── Postes de dialyse
    ├── Types de dialyseur / dialysat
    ├── Types d'accès vasculaire
    ├── Règles tarifaires
    └── Jours fériés
```

## Redirections après login

| Rôle | Redirection |
|---|---|
| Infirmière | Dashboard infirmier (OWL) |
| Facturation | Séances non facturées |
| Médecin | Liste patients |
| Secrétaire | Liste patients |
| Patient portail | `/my/nephro` |

## Fiche patient (form view)

Smart buttons en haut : Séances (count), Bilans (count), Ordonnances (count), RDV (count), Solde (montant).

Onglets : Identité, Néphrologie (is_nephro, dialyse, accès, planning, poids sec, médecin, tarif), Médical (allergies, ATCD), Notes.

## Fiche séance (form view)

Header : référence, patient, statut (badge), timer.
Boutons : Démarrer, Terminer, Annuler, Signaler complication.
Onglets : Avant séance (poids, TA, temp, arrivée), Paramètres (planning, poste, dialyseur, débits), Signes vitaux (tableau inline), Fin séance (poids post, KT/V, tolérance), Complications, Consommables.

## Dashboard médecin (OWL)

### Composants

```
DoctorDashboard (ActionComponent)
├── DoctorKpiBar              ← 4 compteurs (séances, terminées, en cours, alertes)
├── StationGrid               ← Tableau postes temps réel
│   └── StationRow            ← Ligne par poste (clic → slide panel)
├── AlertPanel                ← Sidebar alertes (critique/attention)
│   └── AlertCard             ← Carte par alerte
├── PatientSlidePanel         ← Panel latéral dossier patient
│   ├── PatientSummary
│   ├── LastSessionCard
│   ├── LastBilanCard
│   └── ActionButtons
└── MonthlyCharts             ← Graphiques Chart.js
    ├── KtvChart
    ├── ComplicationChart
    └── OccupancyChart
```

Endpoint : `/nephro/dashboard/doctor/data` (auth=user, 30s refresh, bus.Bus alertes).

## Interface infirmier (OWL)

Optimisée tactile — grands boutons, lisible à 50cm.

### Écrans

```
NurseDashboard (ActionComponent)
├── Screen 'list'          → PatientCardGrid (cartes par poste)
├── Screen 'session'       → SessionView (pré-dialyse, machine, vitaux)
├── Screen 'complication'  → ComplicationPopup (sélection rapide type)
└── Screen 'end'           → EndSessionForm (poids post, KT/V, validation)
```

Toutes transitions via `this.orm.call('nephro.procedure', 'action_*')`.

## Portail patient (QWeb templates)

### Pages

| Route | Contenu |
|---|---|
| `/my/nephro` | Tableau de bord : prochain RDV, dernier bilan, solde, ordonnances |
| `/my/seances` | Liste séances paginée (20/page) |
| `/my/seances/<id>` | Détail : signes vitaux, paramètres, complications |
| `/my/bilans` | Liste + graphique évolution 6 mois |
| `/my/bilans/<id>` | Détail bilan avec badges |
| `/my/rdv` | Liste + bouton annulation |
| `/my/ordonnances` | Liste ordonnances actives |
| `/my/factures` | Historique + solde + PDF |

### Principes

- Pas de sudo — record rules filtrent
- Langage simplifié ("Séance efficace ✅" au lieu de KT/V brut)
- Mobile-first (375px)
- Pagination 20/page
- Téléchargement PDF QWeb

## Widget secrétaire (OWL)

Petit composant en haut de la liste patients : compteurs jour (total, terminés, en cours, programmés, absents), postes occupés.
