// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Facturation — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'billing');
  });

  test('01 — Connexion et accueil facturation', async ({ page }) => {
    await screenshot(page, 'fac', 1, 'accueil');
  });

  test('02 — Menu facturation', async ({ page }) => {
    await page.click('text=Nephrology');
    await screenshot(page, 'fac', 2, 'menu_nephro');
  });

  test('03 — Séances non facturées', async ({ page }) => {
    await page.click('text=Nephrology');
    const billingMenu = page.locator('text=Billing').first();
    if (await billingMenu.isVisible()) {
      await billingMenu.click();
      await page.waitForTimeout(1000);
      const uninvoiced = page.locator('text=Uninvoiced Sessions, text=Uninvoiced').first();
      if (await uninvoiced.isVisible()) {
        await uninvoiced.click();
        await page.waitForSelector('.o_list_view, .o_kanban_view');
        await screenshot(page, 'fac', 3, 'seances_non_facturees');
      }
    }
  });

  test('04 — Règles tarifaires', async ({ page }) => {
    await page.click('text=Nephrology');
    const configMenu = page.locator('text=Configuration').first();
    if (await configMenu.isVisible()) {
      await configMenu.click();
      await page.waitForTimeout(1000);
      const pricingMenu = page.locator('text=Pricing Rules, text=Pricing').first();
      if (await pricingMenu.isVisible()) {
        await pricingMenu.click();
        await page.waitForSelector('.o_list_view, .o_kanban_view');
        await screenshot(page, 'fac', 4, 'regles_tarifaires');
      }
    }
  });
});
