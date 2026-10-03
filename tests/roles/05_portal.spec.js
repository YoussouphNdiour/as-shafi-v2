// @ts-check
const { test, expect } = require('@playwright/test');
const { loginAs, screenshot } = require('../helpers/login');

test.describe('Patient — Portail complet', () => {

  test.beforeEach(async ({ page }) => {
    await loginAs(page, 'patient');
  });

  test('01 — Accueil du portail', async ({ page }) => {
    await screenshot(page, 'pat', 1, 'accueil_portail');
  });

  test('02 — Mes séances de dialyse', async ({ page }) => {
    await page.goto('/my/seances');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 2, 'mes_seances');
  });

  test('03 — Mes bilans biologiques', async ({ page }) => {
    await page.goto('/my/bilans');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 3, 'mes_bilans');
  });

  test('04 — Mes ordonnances', async ({ page }) => {
    await page.goto('/my/ordonnances');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 4, 'mes_ordonnances');
  });

  test('05 — Mes rendez-vous', async ({ page }) => {
    await page.goto('/my/rdv');
    await page.waitForTimeout(2000);
    await screenshot(page, 'pat', 5, 'mes_rdv');
  });
});
