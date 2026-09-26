// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Secrétaire — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'secretary');
  });

  test('01 — Connexion et accueil', async ({ page }) => {
    await screenshot(page, 'sec', 1, 'accueil');
    // Should see Nephrology menu
    await expect(page.locator('.o_main_navbar')).toContainText('Nephrology');
  });

  test('02 — Accès liste patients', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await screenshot(page, 'sec', 2, 'patients_liste');
    // List should be visible
    await expect(page.locator('.o_list_view, .o_kanban_view')).toBeVisible();
  });

  test('03 — Créer un patient', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await page.click('button:has-text("New")');
    await page.waitForSelector('.o_form_view');

    // Fill required fields
    await page.fill('div[name="name"] input', 'Fatou Ba');
    await page.selectOption('select[name="gender"]', 'female');
    await page.fill('div[name="birth_date"] input', '01/15/1990');
    await page.fill('div[name="phone"] input', '+221771234567');
    await page.fill('div[name="emergency_contact"] input', '+221779876543');

    await screenshot(page, 'sec', 3, 'patient_creation');

    // Save
    await page.click('button.o_form_button_save, .o_form_button_save');
    await page.waitForTimeout(2000);
    await screenshot(page, 'sec', 4, 'patient_sauvegarde');

    // Verify HMS ID was generated
    const hmsId = page.locator('div[name="hms_id"] span, div[name="hms_id"] input');
    await expect(hmsId).not.toBeEmpty();
  });

  test('04 — Activer soins néphrologiques', async ({ page }) => {
    // Navigate to existing patient
    await page.click('text=Nephrology');
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view');
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view');

    // Check is_nephro checkbox if not already checked
    const checkbox = page.locator('div[name="is_nephro"] input[type="checkbox"]');
    if (!(await checkbox.isChecked())) {
      await checkbox.click();
    }
    await screenshot(page, 'sec', 5, 'patient_nephro_active');
  });

  test('05 — Créer un rendez-vous', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Appointments');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await page.click('button:has-text("New")');
    await page.waitForSelector('.o_form_view');

    await screenshot(page, 'sec', 6, 'rdv_creation');
  });

  test('06 — Accès menu Hémodialyses', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await screenshot(page, 'sec', 7, 'hemodialyses_liste');
  });

  test('07 — Générer séances en masse', async ({ page }) => {
    await page.click('text=Nephrology');
    // Look for session generator menu
    const genMenu = page.locator('text=Generate Sessions, text=Session Generator').first();
    if (await genMenu.isVisible()) {
      await genMenu.click();
      await page.waitForSelector('.o_form_view');
      await screenshot(page, 'sec', 8, 'generateur_seances');
    }
  });
});
