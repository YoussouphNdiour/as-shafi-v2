#!/bin/bash
# Launch Odoo 19 for nephro_v2 development
# Usage: bash scripts/launch_odoo.sh [init|update|run]

ODOO_DIR="/Users/yusper/Downloads/modules 19/odoo-19.0.post20260601"
ADDONS_DIR="/Users/yusper/Downloads/modules 19/as shafi 2"
VENV_DIR="$ODOO_DIR/.venv"
DB_NAME="nephro_v2"
PORT=8069

# Activate venv
source "$VENV_DIR/bin/activate"

ODOO_CMD="python3 -m odoo"
ADDONS_PATH="$ODOO_DIR/odoo/addons,$ADDONS_DIR"

NEPHRO_MODULES="nephro_core,nephro_dialysis,nephro_bilans,nephro_complications,nephro_billing,nephro_dashboard,nephro_portal,nephro_whatsapp,nephro_fr"

case "${1:-run}" in
    init)
        echo "=== Initializing database $DB_NAME with nephro modules ==="
        $ODOO_CMD -d "$DB_NAME" \
            --addons-path="$ADDONS_PATH" \
            -i "$NEPHRO_MODULES" \
            --http-port=$PORT \
            --stop-after-init \
            --without-demo=all
        ;;
    update)
        echo "=== Updating nephro modules ==="
        $ODOO_CMD -d "$DB_NAME" \
            --addons-path="$ADDONS_PATH" \
            -u "$NEPHRO_MODULES" \
            --http-port=$PORT \
            --stop-after-init
        ;;
    run)
        echo "=== Starting Odoo on port $PORT ==="
        $ODOO_CMD -d "$DB_NAME" \
            --addons-path="$ADDONS_PATH" \
            --http-port=$PORT
        ;;
    *)
        echo "Usage: $0 [init|update|run]"
        exit 1
        ;;
esac
