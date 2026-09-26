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
  await page.fill('input[name="login"]', creds.login);
  await page.fill('input[name="password"]', creds.password);
  await page.click('button[type="submit"]');

  if (role === 'patient') {
    // Portal user — wait for /my page
    await page.waitForURL('**/my**', { timeout: 30000 });
  } else {
    // Backend user — wait for Odoo web client
    await page.waitForSelector('.o_main_navbar, .o_action_manager', { timeout: 30000 });
  }
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
}

module.exports = { loginAs, screenshot, CREDENTIALS };
