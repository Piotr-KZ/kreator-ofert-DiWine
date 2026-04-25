import { test, expect } from '@playwright/test';

// Mock API before each test
test.beforeEach(async ({ page }) => {
  // Mock listSiteTypes (Vite proxies /api/* to backend)
  await page.route('http://localhost:8002/api/v1/site-types', route =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { value: 'company_card', label: 'Strona firmowa' },
        { value: 'portfolio', label: 'Portfolio' },
        { value: 'landing', label: 'Landing page' },
      ]),
    })
  );
});

test('homepage redirects to /lab/create', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/lab\/create/);
});

test('CreateProject page renders form elements', async ({ page }) => {
  await page.goto('/lab/create');

  await expect(page.getByText('Lab Creator')).toBeVisible();
  await expect(page.getByPlaceholder('np. Firma XYZ')).toBeVisible();
  await expect(page.getByRole('button', { name: /stworz projekt/i })).toBeVisible();
});

test('submit button is disabled without project name', async ({ page }) => {
  await page.goto('/lab/create');
  const btn = page.getByRole('button', { name: /stworz projekt/i });
  await expect(btn).toBeDisabled();
});

test('submit button enables after typing name', async ({ page }) => {
  await page.goto('/lab/create');
  await page.getByPlaceholder('np. Firma XYZ').fill('Kawiarnia Miętowa');
  const btn = page.getByRole('button', { name: /stworz projekt/i });
  await expect(btn).toBeEnabled();
});

test('site type dropdown is rendered', async ({ page }) => {
  await page.goto('/lab/create');
  // Select element should render immediately (options load async)
  await expect(page.locator('select')).toBeVisible();
});
