// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Patient — Portail complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'patient');
  });

  test('01 — Connexion portail', async ({ page }) => {
    await screenshot(page, 'pat', 1, 'accueil_portail');
  });

  test('02 — Dashboard néphro', async ({ page }) => {
    await page.goto('/my/nephro');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 2, 'dashboard_nephro');
  });

  test('03 — Mes séances', async ({ page }) => {
    await page.goto('/my/seances');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 3, 'mes_seances');
  });

  test('04 — Mes bilans', async ({ page }) => {
    await page.goto('/my/bilans');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 4, 'mes_bilans');
  });

  test('05 — Mes rendez-vous', async ({ page }) => {
    await page.goto('/my/rdv');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 5, 'mes_rdv');
  });

  test('06 — Mes ordonnances', async ({ page }) => {
    await page.goto('/my/ordonnances');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 6, 'mes_ordonnances');
  });

  test('07 — Mes factures', async ({ page }) => {
    await page.goto('/my/factures');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 7, 'mes_factures');
  });
});
