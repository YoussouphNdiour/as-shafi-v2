// @ts-check

const CREDENTIALS = {
  admin: { login: 'admin@clinique.test', password: 'Nephro2024!' },
  secretary: { login: 'secretaire@clinique.test', password: 'Nephro2024!' },
  doctor: { login: 'medecin@clinique.test', password: 'Nephro2024!' },
  nurse: { login: 'infirmiere@clinique.test', password: 'Nephro2024!' },
  billing: { login: 'facturation@clinique.test', password: 'Nephro2024!' },
  patient: { login: 'patient@clinique.test', password: 'Nephro2024!' },
};

/**
 * Login as a specific role and wait for the interface to load.
 * @param {import('@playwright/test').Page} page
 * @param {'admin'|'secretary'|'doctor'|'nurse'|'billing'|'patient'} role
 */
async function loginAs(page, role) {
  const creds = CREDENTIALS[role];
  if (!creds) throw new Error(`Unknown role: ${role}`);

  await page.goto('/web/login');

  // Odoo 19 with website module: login form may be hidden (d-none).
  const loginForm = page.locator('form.oe_login_form');
  const isHidden = await loginForm.evaluate(el => el.classList.contains('d-none')).catch(() => false);
  if (isHidden) {
    await loginForm.evaluate(el => el.classList.remove('d-none'));
  }

  await page.fill('form.oe_login_form input[name="login"]', creds.login);
  await page.fill('form.oe_login_form input[name="password"]', creds.password);
  await page.click('form.oe_login_form button[type="submit"]');

  if (role === 'patient') {
    // Portal user — wait for /my page
    await page.waitForURL('**/my**', { timeout: 30000 });
  } else {
    // Backend user — wait for Odoo web client
    await page.waitForSelector('.o_main_navbar', { timeout: 30000 });
    await page.waitForTimeout(2000);
  }
}

/**
 * Navigate to the Nephrology app via the app switcher (burger/grid icon).
 * @param {import('@playwright/test').Page} page
 */
async function goToNephrology(page) {
  // Click the app switcher (grid icon in top-left)
  const switcher = page.locator('.o_navbar_apps_menu button, .o_menu_toggle').first();
  await switcher.click();
  await page.waitForTimeout(1000);

  // Click on Nephrology app
  const nephroApp = page.locator('.o_app:has-text("Nephrology"), a:has-text("Nephrology")').first();
  await nephroApp.click();
  await page.waitForSelector('.o_action_manager', { timeout: 15000 });
  await page.waitForTimeout(1500);
}

/**
 * Take a numbered screenshot and save to screenshots/ directory.
 * @param {import('@playwright/test').Page} page
 * @param {string} role - Role prefix (e.g., 'sec', 'med', 'inf')
 * @param {number} step - Step number
 * @param {string} description - Short description for filename
 */
async function screenshot(page, role, step, description) {
  const filename = `${role}_${String(step).padStart(2, '0')}_${description}.png`;
  await page.screenshot({
    path: `screenshots/${filename}`,
    fullPage: true,
  });
  // Also save to the guide directory
  const path = require('path');
  const fs = require('fs');
  const guideDir = path.resolve(__dirname, '../../docs/guide/screenshots');
  if (fs.existsSync(guideDir)) {
    await page.screenshot({
      path: path.join(guideDir, filename),
      fullPage: true,
    });
  }
}

module.exports = { loginAs, screenshot, goToNephrology, CREDENTIALS };
