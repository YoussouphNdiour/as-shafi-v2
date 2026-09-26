# 02 — Features

## Vue par module

### nephro_core
- Dossier patient complet (identité, néphrologie, médical)
- Numéro HMS auto-généré (séquence)
- Fiche médecin avec lien utilisateur Odoo
- Procédure (séance) avec workflow 4 états : scheduled → running → done | cancel
- Consultation (RDV) avec workflow 4 états : draft → confirmed → done | cancel
- Ordonnance avec lignes de prescription (médicament, dosage, fréquence, voie)
- Consommables par séance (rein, lignes, aiguilles)
- Groupes de sécurité dédiés (user, secretary, nurse, billing, doctor, manager)
- Smart buttons sur fiche patient (séances, bilans, ordonnances, RDV, solde)

### nephro_dialysis
- Séance enrichie : pré-dialyse (poids, TA, température, arrivée), paramètres machine, fin de séance
- Signes vitaux multiples par séance (TA, FC, FR, SpO2, temp, glycémie) avec horodatage
- Alerte automatique si TA systolique < 90 mmHg
- Calcul KT/V automatique (Daugirdas II) avec badge adéquat/insuffisant
- Calcul URR automatique
- Calcul UF réelle (poids arrivée - poids sortie)
- Historique poids sec avec traçabilité (qui, quand, pourquoi)
- Planning dialyse : jours, horaires, poste, médecin, infirmières
- Postes de dialyse : nom, salle, type (standard/isolement), équipement
- Générateur de séances en masse : sélection patients, période, exclusion jours fériés, prévisualisation
- Tables de configuration : dialyseurs, dialysats, accès vasculaires, jours fériés, allergies

### nephro_bilans
- Bilan biologique complet : hématologie, biochimie rénale, électrolytes, minéraux-os, nutrition/inflammation, sérologies
- Type de bilan : mensuel, trimestriel, semestriel, annuel, ponctuel
- Seuils configurables par paramètre (valeur min/max)
- Badges automatiques : vert (normal), orange (limite), rouge (hors cible)
- Statut global computed : normal / warning / critical
- Cron quotidien : alerte bilans en retard (> 30 jours)
- Pièces jointes PDF laboratoire

### nephro_complications
- Complication liée à une séance : type, heure, TA, action prise, résolution
- 8 types : hypotension, crampes, nausées, douleur thoracique, fièvre, prurit, arrêt prématuré, autre
- Résolution : résolue / partielle / non résolue
- Alerte dashboard médecin si non résolue à la clôture

### nephro_billing
- Règles tarifaires : nom, prix, TVA, couverture, part patient
- Facturation automatique optionnelle à la fin de séance
- Facturation groupée par wizard : sélection patients + période + prévisualisation
- Solde patient computed (factures dues - paiements)
- Consommables → lignes de facture automatiques

### nephro_dashboard
- Dashboard médecin OWL : KPIs jour, tableau postes temps réel, panel alertes, slide panel patient, graphiques mensuels
- Interface infirmier tablette OWL : cartes patients, séance en cours, popup complication, fin de séance
- Widget secrétaire : résumé du jour (compteurs)
- Alertes temps réel via bus.Bus Odoo

### nephro_portal
- Tableau de bord patient : prochain RDV, dernier bilan, solde, ordonnances
- Mes séances : historique avec détail (signes vitaux, paramètres, complications)
- Mes bilans : résultats avec badges + graphique évolution
- Mes RDV : liste + bouton annulation
- Mes ordonnances : liste actives
- Mes factures : historique + solde + téléchargement PDF
- Mobile-first, pagination, langage simplifié

### nephro_whatsapp
- Rappel J-1 (cron 18h) et J (cron 6h30)
- Notification fin de séance
- Alerte bilan critique
- Confirmation annulation patient
- Notification absence au médecin

### nephro_fr
- Traductions françaises complètes (.po) pour tous les modules

### payment_wave
- Paiement Wave sans frais cachés
- Webhook signé HMAC SHA-256
- Codes HTTP corrects (200/400/500)

### payment_orange_money
- Paiement Orange Money sans frais cachés
- Webhook signé HMAC SHA-256
- Codes HTTP corrects
