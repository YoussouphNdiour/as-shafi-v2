// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot, goToNephrology } = require('../helpers/login');

test.describe('Médecin — Parcours complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'doctor');
  });

  test('01 — Liste des patients', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'med', 1, 'patients_liste');
  });

  test('02 — Dossier patient détaillé', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Patients');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    await screenshot(page, 'med', 2, 'patient_dossier');
  });

  test('03 — Liste hémodialyses', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'med', 3, 'hemodialyses_liste');
  });

  test('04 — Séance — Onglet Pré-dialyse', async ({ page }) => {
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
    await screenshot(page, 'med', 4, 'seance_pre_dialyse');
  });

  test('05 — Séance — Onglet Paramètres machine', async ({ page }) => {
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
    await screenshot(page, 'med', 5, 'seance_parametres_machine');
  });

  test('06 — Séance — Onglet Signes vitaux', async ({ page }) => {
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
    await screenshot(page, 'med', 6, 'seance_signes_vitaux');
  });

  test('07 — Séance — Onglet Complications', async ({ page }) => {
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
    await screenshot(page, 'med', 7, 'seance_complications');
  });

  test('08 — Séance — Onglet Post-dialyse', async ({ page }) => {
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
    await screenshot(page, 'med', 8, 'seance_post_dialyse');
  });

  test('09 — Séance — Onglet Lectures machine', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Hemodialysis');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    await page.click('.o_data_row:first-child');
    await page.waitForSelector('.o_form_view', { timeout: 15000 });
    const tab = page.locator('.o_notebook .nav-link:has-text("Machine Readings")');
    if (await tab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await tab.click();
      await page.waitForTimeout(500);
    }
    await screenshot(page, 'med', 9, 'seance_lectures_machine');
  });

  test('10 — Liste des prescriptions', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Prescriptions');
    await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    await screenshot(page, 'med', 10, 'prescriptions_liste');
  });

  test('11 — Prescription remplie', async ({ page }) => {
    await goToNephrology(page);
    await page.click('text=Prescriptions');
    await page.waitForSelector('.o_list_view', { timeout: 15000 });
    const row = page.locator('.o_data_row:first-child');
    if (await row.isVisible({ timeout: 3000 }).catch(() => false)) {
      await row.click();
      await page.waitForSelector('.o_form_view', { timeout: 15000 });
    } else {
      await page.click('button:has-text("New")');
      await page.waitForSelector('.o_form_view', { timeout: 15000 });
    }
    await screenshot(page, 'med', 11, 'prescription_form');
  });

  test('12 — Liste des bilans biologiques', async ({ page }) => {
    await goToNephrology(page);
    const bilanMenu = page.locator('.o_menu_sections a:has-text("Biological Results"), .o_menu_sections a:has-text("Bilans")').first();
    if (await bilanMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await bilanMenu.click();
      await page.waitForSelector('.o_list_view, .o_kanban_view', { timeout: 15000 });
    }
    await screenshot(page, 'med', 12, 'bilans_liste');
  });

  test('13 — Bilan biologique rempli', async ({ page }) => {
    await goToNephrology(page);
    const bilanMenu = page.locator('.o_menu_sections a:has-text("Biological Results"), .o_menu_sections a:has-text("Bilans")').first();
    if (await bilanMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await bilanMenu.click();
      await page.waitForSelector('.o_list_view', { timeout: 15000 });
      const row = page.locator('.o_data_row:first-child');
      if (await row.isVisible({ timeout: 3000 }).catch(() => false)) {
        await row.click();
        await page.waitForSelector('.o_form_view', { timeout: 15000 });
      }
    }
    await screenshot(page, 'med', 13, 'bilan_form');
  });

  test('14 — Dashboard médecin', async ({ page }) => {
    await goToNephrology(page);
    const dashMenu = page.locator('.o_menu_sections a:has-text("Doctor Dashboard")').first();
    if (await dashMenu.isVisible({ timeout: 5000 }).catch(() => false)) {
      await dashMenu.click();
      await page.waitForTimeout(3000);
    }
    await screenshot(page, 'med', 14, 'dashboard');
  });
});
