// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot, goToNephrology } = require('../helpers/login');

test.describe('Facturation — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'billing');
  });

  test('01 — Connexion et accueil facturation', async ({ page }) => {
    await screenshot(page, 'fac', 1, 'accueil');
    await goToNephrology(page);
    await screenshot(page, 'fac', 2, 'nephro_accueil');
  });

  test('02 — Menu Hémodialyses', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'fac', 3, 'hemodialyses_liste');
  });
});
