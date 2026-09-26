# 15 — Orchestration

## Ordre d'installation des modules

L'ordre respecte les dépendances. Chaque module doit être installé après ses dépendances.

```
1. nephro_core           ← socle (patient, physician, procedure, appointment, prescription)
2. nephro_dialysis       ← séances enrichies (dépend de nephro_core)
3. nephro_bilans         ← bilans biologiques (dépend de nephro_dialysis)
4. nephro_complications  ← complications (dépend de nephro_dialysis)
5. nephro_billing        ← facturation (dépend de nephro_dialysis + account)
6. nephro_dashboard      ← dashboards OWL (dépend de nephro_dialysis + bilans + complications)
7. nephro_portal         ← portail patient (dépend de nephro_dialysis + bilans + billing + website)
8. nephro_whatsapp       ← notifications (dépend de nephro_dialysis)
9. nephro_fr             ← traductions (dépend de tous les modules nephro)
10. payment_wave         ← paiement Wave (dépend de payment, indépendant de nephro)
11. payment_orange_money ← paiement Orange Money (dépend de payment)
```

## Installation complète (première fois)

```bash
docker exec odoo-container odoo-bin -d asshafi \
    -i nephro_core,nephro_dialysis,nephro_bilans,nephro_complications,\
nephro_billing,nephro_dashboard,nephro_portal,nephro_whatsapp,nephro_fr,\
payment_wave,payment_orange_money \
    --stop-after-init
```

## Mise à jour

```bash
# Mise à jour d'un module spécifique
docker exec odoo-container odoo-bin -d asshafi -u nephro_dialysis --stop-after-init

# Mise à jour de tous les modules nephro
docker exec odoo-container odoo-bin -d asshafi \
    -u nephro_core,nephro_dialysis,nephro_bilans,nephro_complications,\
nephro_billing,nephro_dashboard,nephro_portal,nephro_whatsapp,nephro_fr \
    --stop-after-init
```

## Tests

```bash
# Tests sur une base dédiée
docker exec odoo-container odoo-bin -d test_asshafi \
    --test-enable \
    -i nephro_core,nephro_dialysis,nephro_bilans,nephro_complications,\
nephro_billing,nephro_portal \
    --stop-after-init

# Tests Playwright (depuis le host)
cd tests && npx playwright test
```

## Environnement

| Aspect | Valeur |
|---|---|
| Serveur | VPS Contabo PRO4 (12 vCPU / 24 GB RAM) |
| Container | Docker — Odoo 19 |
| Base de données | PostgreSQL (container séparé) |
| Port | 19019 |
| Proxy | Nginx reverse proxy + SSL Let's Encrypt |
| Addons path | `/mnt/extra-addons/` dans le container |

## Copie des modules vers le serveur

```bash
# Depuis la machine locale
docker cp nephro_core odoo-container:/mnt/extra-addons/
docker cp nephro_dialysis odoo-container:/mnt/extra-addons/
# ... etc pour chaque module

# Ou via rsync si accès SSH
rsync -avz --exclude='__pycache__' --exclude='.git' \
    nephro_*/ payment_*/ \
    user@server:/path/to/addons/
```

## Données de démonstration

Après l'installation, créer les comptes utilisateur :

| Rôle | Login | Groupe |
|---|---|---|
| Admin | admin@clinique.test | group_nephro_manager |
| Médecin | medecin@clinique.test | group_nephro_doctor |
| Infirmière | infirmiere@clinique.test | group_nephro_nurse |
| Secrétaire | secretaire@clinique.test | group_nephro_secretary |
| Facturation | facturation@clinique.test | group_nephro_billing |
| Patient | patient@clinique.test | base.group_portal |
