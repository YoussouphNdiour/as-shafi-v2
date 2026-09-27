// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot, goToNephrology } = require('../helpers/login');

test.describe('Infirmière — Parcours séance complète', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'nurse');
  });

  test('01 — Dashboard infirmière', async ({ page }) => {
    await goToNephrology(page);
    const nurseMenu = page.locator('.o_menu_sections a:has-text("Nurse Interface"), .o_menu_sections a:has-text("Nurse")').first();
    if (await nurseMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await nurseMenu.click();
      await page.waitForTimeout(3000);
    }
    await screenshot(page, 'inf', 1, 'dashboard');
  });

  test('02 — Liste hémodialyses', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'inf', 2, 'hemodialyses_liste');
  });

  test('03 — Séance en cours — Pré-dialyse', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Pre-dialysis")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'inf', 3, 'seance_pre_dialyse');
  });

  test('04 — Signes vitaux pendant la séance', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Vital Signs")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'inf', 4, 'seance_signes_vitaux');
  });

  test('05 — Paramètres machine', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Machine Parameters")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'inf', 5, 'seance_parametres_machine');
  });

  test('06 — Séance terminée — Post-dialyse', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Post-dialysis")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'inf', 6, 'seance_post_dialyse');
  });

  test('07 — Complications', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Complications")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'inf', 7, 'seance_complications');
  });

  test('08 — Bilans biologiques (consultation)', async ({ page }) => {
    await goToNephrology(page);
    const bilanMenu = page.locator('.o_menu_sections a:has-text("Biological Results"), .o_menu_sections a:has-text("Bilans")').first();
    if (await bilanMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await bilanMenu.click();
      await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    }
    await screenshot(page, 'inf', 8, 'bilans_liste');
  });
});
