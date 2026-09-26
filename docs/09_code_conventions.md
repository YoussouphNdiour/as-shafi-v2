# 09 — Code Conventions

## Python

### Imports

```python
# 1. stdlib
import logging
from datetime import timedelta

# 2. odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError

# 3. local
from .common import COMPLICATION_TYPES

_logger = logging.getLogger(__name__)
```

### Structure d'un modèle

```python
class NephroModel(models.Model):
    _name = 'nephro.example'
    _description = 'Example Model'
    _order = 'date desc'

    # --- Relations ---
    patient_id = fields.Many2one(...)

    # --- Data ---
    name = fields.Char(...)
    date = fields.Date(...)

    # --- Computed ---
    total = fields.Float(compute='_compute_total', store=True)

    # --- Constraints ---
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique'),
    ]

    # --- Compute methods ---
    @api.depends('field1', 'field2')
    def _compute_total(self):
        ...

    # --- CRUD overrides ---
    @api.model_create_multi
    def create(self, vals_list):
        ...

    # --- Action methods ---
    def action_confirm(self):
        ...
```

### Règles strictes

| Règle | Exemple correct | Exemple interdit |
|---|---|---|
| Logger | `_logger.info("msg %s", arg)` | `_logger.info(f"msg {arg}")` |
| Strings champs | `string="Blood Pressure"` | `string="Tension artérielle"` |
| Traductions | `raise UserError(_("Weight required"))` | `raise UserError("Poids requis")` |
| Controllers | `request.env['model'].search([])` | `request.env['model'].sudo().search([])` |
| Transactions | (jamais) | `self.env.cr.commit()` |
| Exceptions | `_logger.exception("Invoice failed for %s", id)` | `except Exception: pass` |
| HTTP interne | (jamais) | `requests.get('http://localhost:8069/...')` |
| Workflow | `self.action_cancel()` | `self.write({'state': 'cancel'})` |

### Docstrings

Uniquement sur méthodes publiques et méthodes de workflow :

```python
def action_start(self):
    """Scheduled → Running. Requires pre_weight and pre_bp."""
    ...
```

## XML

### Vues

```xml
<record id="nephro_dialysis_procedure_view_form" model="ir.ui.view">
    <field name="name">nephro.procedure.form</field>
    <field name="model">nephro.procedure</field>
    <field name="arch" type="xml">
        <form>
            ...
        </form>
    </field>
</record>
```

### Actions

```xml
<record id="nephro_dialysis_procedure_action" model="ir.actions.act_window">
    <field name="name">Hemodialysis Sessions</field>
    <field name="res_model">nephro.procedure</field>
    <field name="view_mode">list,form</field>
</record>
```

### Menus

```xml
<menuitem id="nephro_dialysis_menu_sessions"
    name="Hemodialysis"
    parent="nephro_core.menu_nephrology_root"
    action="nephro_dialysis_procedure_action"
    sequence="30"
    groups="nephro_core.group_nephro_user"/>
```

## OWL (composants JavaScript)

- Imports depuis `@odoo/owl` et `@web/*`
- Transitions d'état via `this.orm.call('model', 'action_method', [ids])` — jamais `this.orm.write()`
- Pas de `fetch()` direct — utiliser `this.rpc()` ou `this.orm`
- Cleanup des timers dans `onWillUnmount`

## Manifests

- `version` : `'19.0.2.x.y'`
- `author` : `'As-Shafi Medical'`
- `license` : `'LGPL-3'`
- `installable` : toujours explicite `True`
- `application` : `True` uniquement pour `nephro_core`
- Ordre `data` : security → data → views → report → menu

## i18n

- Champs en anglais dans le code
- Traductions en `.po` dans `nephro_fr/i18n/`
- Extraction : `odoo-bin -d db --modules=nephro_core -l fr_FR --i18n-export`
- Pas de `string="Lundi"` — le champ est `string="Monday"`, la traduction dans le .po

## Git

- Commits en anglais ou français, messages concis
- Branches : `feat/`, `fix/`, `refactor/`
- Pas de `--no-verify`, pas de `--force`
