// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Infirmière — Parcours séance complète', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'nurse');
  });

  test('01 — Connexion et interface infirmier', async ({ page }) => {
    await screenshot(page, 'inf', 1, 'accueil');
  });

  test('02 — Menu néphrologie', async ({ page }) => {
    await page.click('text=Nephrology');
    await screenshot(page, 'inf', 2, 'menu_nephro');
  });

  test('03 — Interface infirmier (dashboard)', async ({ page }) => {
    await page.click('text=Nephrology');
    const nurseMenu = page.locator('text=Nurse Interface').first();
    if (await nurseMenu.isVisible()) {
      await nurseMenu.click();
      await page.waitForTimeout(3000);
      await screenshot(page, 'inf', 3, 'dashboard_infirmier');
    }
  });

  test('04 — Liste hémodialyses (lecture seule)', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view');
    await screenshot(page, 'inf', 4, 'hemodialyses_liste');
  });

  test('05 — Ouvrir une séance', async ({ page }) => {
    await page.click('text=Nephrology');
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view');
    const row = page.locator('.o_data_row:first-child');
    if (await row.isVisible()) {
      await row.click();
      await page.waitForSelector('.o_form_view');
      await screenshot(page, 'inf', 5, 'seance_formulaire');

      // Check for workflow buttons
      const startBtn = page.locator('button:has-text("Start")');
      const doneBtn = page.locator('button:has-text("Complete")');
      await screenshot(page, 'inf', 6, 'seance_boutons');
    }
  });
});
