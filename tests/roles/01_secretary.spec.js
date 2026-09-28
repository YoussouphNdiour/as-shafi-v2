// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot, goToNephrology } = require('../helpers/login');

test.describe('Secrétaire — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'secretary');
  });

  test('01 — Connexion et accueil', async ({ page }) => {
    await screenshot(page, 'sec', 1, 'accueil');
    await goToNephrology(page);
    await screenshot(page, 'sec', 2, 'nephro_accueil');
  });

  test('02 — Accès liste patients', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'sec', 3, 'patients_liste');
    await expect(page.locator('.o_list_view, .o_kanban_view')).toBeVisible();
  });

  test('03 — Créer un patient', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await page.click('button:has-text("New")');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    await page.fill('div[name="name"] input', 'Fatou Ba Test');
    await screenshot(page, 'sec', 4, 'patient_creation');
    await page.click('.o_form_button_save');
    await page.waitForTimeout(2000);
    await screenshot(page, 'sec', 5, 'patient_sauvegarde');
  });

  test('04 — Créer un rendez-vous', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Appointments');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await page.click('button:has-text("New")');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    await screenshot(page, 'sec', 6, 'rdv_creation');
  });

  test('05 — Accès menu Hémodialyses', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'sec', 7, 'hemodialyses_liste');
  });

  test('06 — Générer séances en masse', async ({ page }) => {
    await goToNephrology(page);
    const genMenu = page.locator('a:has-text("Generate Sessions"), span:has-text("Generate Sessions")').first();
    if (await genMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await genMenu.click();
      await page.waitForSelector('.o_form_view', { timeout: 15000 });
      await screenshot(page, 'sec', 8, 'generateur_seances');
    } else {
      await screenshot(page, 'sec', 8, 'menu_nephro_complet');
    }
  });
});
