// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Médecin — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'doctor');
  });

  test('01 — Connexion et accueil médecin', async ({ page }) => {
    await screenshot(page, 'med', 1, 'accueil');
    await expect(page.locator('.o_main_navbar')).toContainText('Nephrology');
  });

  test('02 — Liste patients avec filtre néphro', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await screenshot(page, 'med', 2, 'patients_liste');
  });

  test('03 — Ouvrir dossier patient', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view');
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view');
    await screenshot(page, 'med', 3, 'patient_dossier');
    // Should see smart buttons
    await expect(page.locator('.oe_button_box, .o_button_box')).toBeVisible();
  });

  test('04 — Créer une ordonnance', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Prescriptions');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await page.click('button:has-text("New")');
    await page.waitForSelector('.o_form_view');
    await screenshot(page, 'med', 4, 'ordonnance_creation');
  });

  test('05 — Liste hémodialyses', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await screenshot(page, 'med', 5, 'hemodialyses_liste');
  });

  test('06 — Ouvrir fiche séance', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view');
    const row = page.locator('.o_data_row:first-child');
    if (await row.isVisible()) {
      await row.click();
      await page.waitForSelector('.o_form_view');
      await screenshot(page, 'med', 6, 'seance_formulaire');
    }
  });

  test('07 — Bilans biologiques', async ({ page }) => {
    await page.click('text=Nephrology');
    const bilanMenu = page.locator('text=Biological Results, text=Bilans').first();
    if (await bilanMenu.isVisible()) {
      await bilanMenu.click();
      await page.waitForSelector('.o_list_view, .o_kanban_view');
      await screenshot(page, 'med', 7, 'bilans_liste');
    }
  });

  test('08 — Dashboard médecin', async ({ page }) => {
    await page.click('text=Nephrology');
    const dashMenu = page.locator('text=Doctor Dashboard').first();
    if (await dashMenu.isVisible()) {
      await dashMenu.click();
      await page.waitForTimeout(3000);
      await screenshot(page, 'med', 8, 'dashboard_medecin');
    }
  });
});
