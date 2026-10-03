// @ts-check
/**
 * Script autonome pour generer tous les screenshots du guide utilisateur.
 * Usage: cd tests && node generate_guide.js
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const BASE_URL = 'http://localhost:8069';
const GUIDE_DIR = path.resolve(__dirname, '../docs/guide/screenshots');

if (!fs.existsSync(GUIDE_DIR)) {
  fs.mkdirSync(GUIDE_DIR, { recursive: true });
}

const CREDENTIALS = {
  admin: { login: 'admin@clinique.test', password: 'Nephro2024!' },
  secretary: { login: 'secretaire@clinique.test', password: 'Nephro2024!' },
  doctor: { login: 'medecin@clinique.test', password: 'Nephro2024!' },
  nurse: { login: 'infirmiere@clinique.test', password: 'Nephro2024!' },
  billing: { login: 'facturation@clinique.test', password: 'Nephro2024!' },
  patient: { login: 'patient@clinique.test', password: 'Nephro2024!' },
};

// Noms exacts des onglets tels qu'affiches dans l'interface Odoo 19 FR
const SESSION_TABS = {
  consumables: 'Consommables',
  pre_dialysis: 'Pré-dialyse',
  machine_params: 'Paramètres machine',
  vital_signs: 'Signes vitaux',
  post_dialysis: 'Post-dialyse',
  machine_readings: 'Relevés machine',
  complications: 'Complications',
};

const BILAN_TABS = {
  hematology: 'Hématologie',
  biochemistry: 'Biochimie',
  electrolytes: 'Électrolytes',
  mineral_bone: 'Minéral-Osseux',
  nutrition: 'Nutrition / Inflammation',
  serology: 'Sérologie',
  documents: 'Documents',
};

// ============================================================
// HELPERS
// ============================================================

async function loginAs(page, role) {
  const creds = CREDENTIALS[role];
  await page.goto(`${BASE_URL}/web/session/logout`).catch(() => {});
  await page.waitForTimeout(1000);
  await page.goto(`${BASE_URL}/web/login`);
  await page.waitForLoadState('domcontentloaded');

  const loginForm = page.locator('form.oe_login_form');
  const isHidden = await loginForm.evaluate(el => el.classList.contains('d-none')).catch(() => false);
  if (isHidden) await loginForm.evaluate(el => el.classList.remove('d-none'));

  await page.fill('form.oe_login_form input[name="login"]', creds.login);
  await page.fill('form.oe_login_form input[name="password"]', creds.password);
  await page.click('form.oe_login_form button[type="submit"]');

  if (role === 'patient') {
    await page.waitForURL('**/my**', { timeout: 30000 });
  } else {
    await page.waitForSelector('.o_main_navbar', { timeout: 30000 });
    await page.waitForTimeout(2500);
  }
  console.log(`  [LOGIN] ${role}`);
}

async function goToNephrology(page) {
  // Use the app switcher
  const switcher = page.locator('.o_navbar_apps_menu button, .o_menu_toggle').first();
  await switcher.click();
  await page.waitForTimeout(1000);

  // Click Nephrologie in the dropdown menu
  const nephro = page.locator('[role="menuitem"]:has-text("Néphrologie")').first();
  if (await nephro.isVisible({ timeout: 3000 }).catch(() => false)) {
    await nephro.click();
  } else {
    // Try app card
    const nephroApp = page.locator('.o_app:has-text("Néphrologie"), .o_app:has-text("Nephrology")').first();
    await nephroApp.click();
  }
  await page.waitForSelector('.o_action_manager', { timeout: 15000 });
  await page.waitForTimeout(2000);
}

async function clickMenu(page, text) {
  const menu = page.locator(`.o_menu_sections [role="menuitem"]:has-text("${text}")`).first();
  if (await menu.isVisible({ timeout: 5000 }).catch(() => false)) {
    await menu.click();
    await page.waitForTimeout(2000);
    return true;
  }
  // Try the "more" dropdown
  const moreBtn = page.locator('.o_menu_sections .o_menu_sections_more, .o_menu_sections .dropdown-toggle').first();
  if (await moreBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await moreBtn.click();
    await page.waitForTimeout(500);
    const subMenu = page.locator(`.dropdown-menu [role="menuitem"]:has-text("${text}"), .dropdown-menu a:has-text("${text}")`).first();
    if (await subMenu.isVisible({ timeout: 3000 }).catch(() => false)) {
      await subMenu.click();
      await page.waitForTimeout(2000);
      return true;
    }
  }
  console.log(`  [WARN] Menu "${text}" non trouve`);
  return false;
}

async function clickTab(page, tabText) {
  // Odoo 19 uses [role="tab"] inside the notebook
  const tab = page.locator(`.o_notebook [role="tab"]:has-text("${tabText}")`).first();
  if (await tab.isVisible({ timeout: 5000 }).catch(() => false)) {
    await tab.click();
    await page.waitForTimeout(800);
    return true;
  }
  // Fallback: nav-link
  const navLink = page.locator(`.o_notebook .nav-link:has-text("${tabText}")`).first();
  if (await navLink.isVisible({ timeout: 2000 }).catch(() => false)) {
    await navLink.click();
    await page.waitForTimeout(800);
    return true;
  }
  console.log(`  [WARN] Onglet "${tabText}" non trouve`);
  return false;
}

async function clickFirstRow(page) {
  await page.waitForSelector('.o_data_row', { timeout: 10000 });
  await page.click('.o_data_row:first-child');
  await page.waitForSelector('.o_form_view', { timeout: 15000 });
  await page.waitForTimeout(1500);
}

async function clickRow(page, text) {
  const row = page.locator(`.o_data_row:has-text("${text}")`).first();
  if (await row.isVisible({ timeout: 5000 }).catch(() => false)) {
    await row.click();
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    await page.waitForTimeout(1500);
    return true;
  }
  return false;
}

async function screenshot(page, prefix, step, description) {
  const filename = `${prefix}_${String(step).padStart(2, '0')}_${description}.png`;
  const filepath = path.join(GUIDE_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`  [SCREENSHOT] ${filename}`);
  return filename;
}

async function enableEdit(page) {
  const editBtn = page.locator('button.o_form_button_edit').first();
  if (await editBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await editBtn.click();
    await page.waitForTimeout(800);
  }
}

async function fillField(page, fieldName, value) {
  const field = page.locator(`div.o_field_widget[name="${fieldName}"] input`).first();
  if (await field.isVisible({ timeout: 2000 }).catch(() => false)) {
    const currentVal = await field.inputValue();
    if (!currentVal || currentVal === '0' || currentVal === '0,00' || currentVal === '0.00') {
      await field.click();
      await field.fill('');
      await field.type(value, { delay: 20 });
      await page.keyboard.press('Tab');
      await page.waitForTimeout(400);
    }
  }
}

async function setSelect(page, fieldName, value) {
  const field = page.locator(`div.o_field_widget[name="${fieldName}"] select`).first();
  if (await field.isVisible({ timeout: 2000 }).catch(() => false)) {
    await field.selectOption({ label: value }).catch(async () => {
      await field.selectOption(value).catch(() => {});
    });
    await page.waitForTimeout(300);
  }
}

async function saveForm(page) {
  // In Odoo 19, click outside or use the discard/save breadcrumb
  const saveBtn = page.locator('.o_form_button_save').first();
  if (await saveBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await saveBtn.click();
    await page.waitForTimeout(2000);
    return;
  }
  // Auto-save: click on breadcrumb or press Enter
  await page.keyboard.press('Escape');
  await page.waitForTimeout(1000);
}

// ============================================================
// SETUP: Fill data as admin
// ============================================================

async function setupData(page) {
  console.log('\n=== SETUP: Remplir les donnees ===');
  await loginAs(page, 'admin');

  // --- Fill session DP/2026/0002 ---
  console.log('  Remplissage seance DP/2026/0002...');
  await page.goto(`${BASE_URL}/odoo/action-405`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);

  if (await clickRow(page, 'DP/2026/0002')) {
    await enableEdit(page);

    // Pre-dialyse
    if (await clickTab(page, SESSION_TABS.pre_dialysis)) {
      await fillField(page, 'pre_weight', '72.5');
      await fillField(page, 'pre_bp', '140/85');
      await fillField(page, 'pre_temp', '36.8');
      // arrival_status - try select
      await setSelect(page, 'arrival_status', 'Stable');
    }

    // Parametres machine
    if (await clickTab(page, SESSION_TABS.machine_params)) {
      await fillField(page, 'blood_flow', '300');
      await fillField(page, 'dialysate_flow', '500');
      await fillField(page, 'anticoag_dose', '4000');
    }

    // Post-dialyse
    if (await clickTab(page, SESSION_TABS.post_dialysis)) {
      await fillField(page, 'post_weight', '70.3');
      await fillField(page, 'post_bp', '130/80');
    }

    // Releves machine
    if (await clickTab(page, SESSION_TABS.machine_readings)) {
      await fillField(page, 'pv_arterial', '-180');
      await fillField(page, 'ptm', '120');
      await fillField(page, 'conductivity', '14.2');
      await fillField(page, 'uf_rate', '800');
      await fillField(page, 'vst_start', '4500');
    }

    await saveForm(page);
    console.log('  Seance mise a jour.');
  }

  // --- Fill bilan BIL/2026/0002 ---
  console.log('  Remplissage bilan BIL/2026/0002...');
  await page.goto(`${BASE_URL}/odoo/action-430`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);

  if (await clickRow(page, 'BIL/2026/0002')) {
    await enableEdit(page);

    // Hematologie
    if (await clickTab(page, BILAN_TABS.hematology)) {
      await fillField(page, 'hemoglobin', '10.5');
      await fillField(page, 'hematocrit', '32');
      await fillField(page, 'wbc', '7.2');
      await fillField(page, 'platelets', '220');
      await fillField(page, 'ferritin', '350');
    }

    // Biochimie
    if (await clickTab(page, BILAN_TABS.biochemistry)) {
      await fillField(page, 'creatinine', '850');
      await fillField(page, 'urea_pre', '25.3');
      await fillField(page, 'urea_post', '8.5');
      await fillField(page, 'uric_acid', '420');
    }

    // Electrolytes
    if (await clickTab(page, BILAN_TABS.electrolytes)) {
      await fillField(page, 'sodium', '138');
      await fillField(page, 'potassium', '5.2');
      await fillField(page, 'calcium', '2.25');
      await fillField(page, 'phosphorus', '1.8');
      await fillField(page, 'bicarbonate', '22');
      await fillField(page, 'chloride', '102');
    }

    // Mineral-Osseux
    if (await clickTab(page, BILAN_TABS.mineral_bone)) {
      await fillField(page, 'pth', '450');
      await fillField(page, 'vitamin_d', '18');
      await fillField(page, 'alkaline_phosphatase', '120');
    }

    // Nutrition / Inflammation
    if (await clickTab(page, BILAN_TABS.nutrition)) {
      await fillField(page, 'albumin', '35');
      await fillField(page, 'total_protein', '65');
      await fillField(page, 'crp', '8.5');
      await fillField(page, 'prealbumin', '280');
    }

    // Serologie
    if (await clickTab(page, BILAN_TABS.serology)) {
      await setSelect(page, 'hbs_ag', 'Négatif');
      await setSelect(page, 'anti_hbs', 'Positif');
      await setSelect(page, 'anti_hbc', 'Négatif');
      await setSelect(page, 'anti_hcv', 'Négatif');
      await setSelect(page, 'anti_hiv', 'Négatif');
    }

    await saveForm(page);
    console.log('  Bilan mis a jour.');
  }
}

// ============================================================
// SECRETAIRE
// ============================================================

async function screenshotsSecretary(page) {
  console.log('\n=== SECRETAIRE ===');
  await loginAs(page, 'secretary');
  await goToNephrology(page);

  // 1. Liste patients
  await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
  await screenshot(page, 'sec', 1, 'patients_liste');

  // 2. Dossier patient
  await clickFirstRow(page);
  await screenshot(page, 'sec', 2, 'patient_dossier');

  // 3. Liste rendez-vous
  await goToNephrology(page);
  if (await clickMenu(page, 'Rendez-vous')) {
    await page.waitForTimeout(2000);
    await screenshot(page, 'sec', 3, 'rendez_vous_liste');

    // 4. Formulaire rendez-vous
    const rdvRow = page.locator('.o_data_row:first-child');
    if (await rdvRow.isVisible({ timeout: 3000 }).catch(() => false)) {
      await rdvRow.click();
      await page.waitForSelector('.o_form_view', { timeout: 15000 });
      await page.waitForTimeout(1000);
      await screenshot(page, 'sec', 4, 'rendez_vous_form');
    } else {
      await screenshot(page, 'sec', 4, 'rendez_vous_form');
    }
  }

  // 5. Liste hemodialyses
  await goToNephrology(page);
  if (await clickMenu(page, 'Hémodialyse')) {
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await screenshot(page, 'sec', 5, 'hemodialyses_liste');
  }

  // 6. Generateur de seances
  await goToNephrology(page);
  if (await clickMenu(page, 'Générer les séances')) {
    await page.waitForTimeout(2000);
    await screenshot(page, 'sec', 6, 'generateur_seances');
  }
}

// ============================================================
// MEDECIN
// ============================================================

async function screenshotsDoctor(page) {
  console.log('\n=== MEDECIN ===');
  await loginAs(page, 'doctor');
  await goToNephrology(page);

  // 1. Liste patients
  await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
  await screenshot(page, 'med', 1, 'patients_liste');

  // 2. Dossier patient
  await clickFirstRow(page);
  await screenshot(page, 'med', 2, 'patient_dossier');

  // 3. Liste hemodialyses
  await goToNephrology(page);
  await clickMenu(page, 'Hémodialyse');
  await page.waitForSelector('.o_list_view', { timeout: 15000 });
  await screenshot(page, 'med', 3, 'hemodialyses_liste');

  // Open session DP/2026/0002
  if (!(await clickRow(page, 'DP/2026/0002'))) {
    await clickFirstRow(page);
  }

  // 4-10: All 7 session tabs
  let step = 4;
  const sessionTabOrder = [
    ['consumables', 'seance_consommables'],
    ['pre_dialysis', 'seance_pre_dialyse'],
    ['machine_params', 'seance_parametres_machine'],
    ['vital_signs', 'seance_signes_vitaux'],
    ['post_dialysis', 'seance_post_dialyse'],
    ['machine_readings', 'seance_releves_machine'],
    ['complications', 'seance_complications'],
  ];
  for (const [key, desc] of sessionTabOrder) {
    if (await clickTab(page, SESSION_TABS[key])) {
      await screenshot(page, 'med', step, desc);
    }
    step++;
  }

  // 11. Prescriptions
  await goToNephrology(page);
  if (await clickMenu(page, 'Ordonnances')) {
    await page.waitForTimeout(2000);
    await screenshot(page, 'med', 11, 'prescriptions_liste');

    // 12. Prescription form
    const rxRow = page.locator('.o_data_row:first-child');
    if (await rxRow.isVisible({ timeout: 3000 }).catch(() => false)) {
      await rxRow.click();
      await page.waitForSelector('.o_form_view', { timeout: 15000 });
      await page.waitForTimeout(1000);
      await screenshot(page, 'med', 12, 'prescription_form');
    }
  }

  // 13. Liste bilans biologiques
  await goToNephrology(page);
  await clickMenu(page, 'Bilans biologiques');
  await page.waitForSelector('.o_list_view', { timeout: 15000 });
  await screenshot(page, 'med', 13, 'bilans_liste');

  // Open bilan BIL/2026/0002
  if (!(await clickRow(page, 'BIL/2026/0002'))) {
    await clickFirstRow(page);
  }

  // 14-19: All 6 bilan tabs (skip Documents)
  step = 14;
  const bilanTabOrder = [
    ['hematology', 'bilan_hematologie'],
    ['biochemistry', 'bilan_biochimie'],
    ['electrolytes', 'bilan_electrolytes'],
    ['mineral_bone', 'bilan_mineral_osseux'],
    ['nutrition', 'bilan_nutrition_inflammation'],
    ['serology', 'bilan_serologie'],
  ];
  for (const [key, desc] of bilanTabOrder) {
    if (await clickTab(page, BILAN_TABS[key])) {
      await screenshot(page, 'med', step, desc);
    }
    step++;
  }

  // 20. Dashboard - check if accessible via more menu or config
  await goToNephrology(page);
  // The "more" button that may contain dashboard
  const moreBtn = page.locator('.o_menu_sections .o_menu_sections_more, .o_menu_sections button[data-hotkey]').last();
  if (await moreBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await moreBtn.click();
    await page.waitForTimeout(500);
    const dashItem = page.locator('.dropdown-menu a:has-text("Dashboard"), .dropdown-menu a:has-text("Tableau de bord")').first();
    if (await dashItem.isVisible({ timeout: 2000 }).catch(() => false)) {
      await dashItem.click();
      await page.waitForTimeout(3000);
      await screenshot(page, 'med', 20, 'dashboard');
    }
  }
}

// ============================================================
// INFIRMIERE
// ============================================================

async function screenshotsNurse(page) {
  console.log('\n=== INFIRMIERE ===');
  await loginAs(page, 'nurse');
  await goToNephrology(page);

  // 1. Vue initiale (dashboard ou patients)
  await page.waitForTimeout(2000);
  await screenshot(page, 'inf', 1, 'dashboard');

  // 2. Liste hemodialyses
  await clickMenu(page, 'Hémodialyse');
  await page.waitForTimeout(2000);
  // Check if list has data
  const hasRows = await page.locator('.o_data_row').first().isVisible({ timeout: 5000 }).catch(() => false);
  await screenshot(page, 'inf', 2, 'hemodialyses_liste');

  if (hasRows) {
    // Open session DP/2026/0002
    if (!(await clickRow(page, 'DP/2026/0002'))) {
      await clickFirstRow(page);
    }

    // 3-7: Session tabs
    let step = 3;
    const nurseTabs = [
      ['pre_dialysis', 'seance_pre_dialyse'],
      ['vital_signs', 'seance_signes_vitaux'],
      ['machine_params', 'seance_parametres_machine'],
      ['post_dialysis', 'seance_post_dialyse'],
      ['complications', 'seance_complications'],
    ];
    for (const [key, desc] of nurseTabs) {
      if (await clickTab(page, SESSION_TABS[key])) {
        await screenshot(page, 'inf', step, desc);
      }
      step++;
    }
  } else {
    console.log('  [INFO] Pas de seances visibles pour l\'infirmiere');
  }

  // 8. Bilans (consultation)
  await goToNephrology(page);
  if (await clickMenu(page, 'Bilans biologiques')) {
    await page.waitForTimeout(2000);
    await screenshot(page, 'inf', 8, 'bilans_liste');
  }
}

// ============================================================
// FACTURATION
// ============================================================

async function screenshotsBilling(page) {
  console.log('\n=== FACTURATION ===');
  await loginAs(page, 'billing');
  await goToNephrology(page);

  // 1. Vue initiale
  await page.waitForTimeout(2000);
  await screenshot(page, 'fac', 1, 'hemodialyses_liste');

  // Try clicking on Hemodialyse menu
  await clickMenu(page, 'Hémodialyse');
  await page.waitForTimeout(2000);
  await screenshot(page, 'fac', 2, 'seances_liste');

  // 3. Check for invoices/factures menu
  const factMenu = await clickMenu(page, 'Factures');
  if (!factMenu) {
    // Screenshot whatever is visible
    await screenshot(page, 'fac', 3, 'factures_liste');
  }
}

// ============================================================
// PATIENT PORTAIL
// ============================================================

async function screenshotsPatient(page) {
  console.log('\n=== PATIENT PORTAIL ===');
  await loginAs(page, 'patient');

  // 1. Accueil portail nephro (page dediee)
  await page.goto(`${BASE_URL}/my/nephro`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  // If redirected to /my, take that screenshot instead
  await screenshot(page, 'pat', 1, 'accueil_portail');

  // 2. Mes seances (direct URL)
  await page.goto(`${BASE_URL}/my/seances`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await screenshot(page, 'pat', 2, 'mes_seances');

  // 3. Mes bilans
  await page.goto(`${BASE_URL}/my/bilans`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await screenshot(page, 'pat', 3, 'mes_bilans');

  // 4. Mes ordonnances
  await page.goto(`${BASE_URL}/my/ordonnances`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await screenshot(page, 'pat', 4, 'mes_ordonnances');

  // 5. Mes rendez-vous
  await page.goto(`${BASE_URL}/my/rdv`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(2000);
  await screenshot(page, 'pat', 5, 'mes_rdv');
}

// ============================================================
// MAIN
// ============================================================

(async () => {
  console.log('========================================');
  console.log('Generation des screenshots du guide');
  console.log('========================================');

  const browser = await chromium.launch({
    headless: true,
    args: ['--window-size=1440,900'],
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    locale: 'fr-FR',
  });

  const page = await context.newPage();

  try {
    await setupData(page);
    await screenshotsSecretary(page);
    await screenshotsDoctor(page);
    await screenshotsNurse(page);
    await screenshotsBilling(page);
    await screenshotsPatient(page);

    console.log('\n========================================');
    console.log('TERMINE!');
    console.log('========================================');

    const files = fs.readdirSync(GUIDE_DIR).filter(f => f.endsWith('.png')).sort();
    console.log(`\n${files.length} screenshots generes:`);
    files.forEach(f => console.log(`  - ${f}`));
  } catch (err) {
    console.error('ERREUR:', err.message);
    await page.screenshot({ path: path.join(GUIDE_DIR, 'ERROR.png'), fullPage: true });
  } finally {
    await browser.close();
  }
})();
