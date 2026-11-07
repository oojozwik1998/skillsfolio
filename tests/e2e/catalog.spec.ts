import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import { site } from '../../src/config';
import { installCommand } from '../../src/lib/skills';

const routes = ['/', '/skills/example-skill/', '/skills/tailor-my-cv/'];
const skillCommand = installCommand(site.repository, 'example-skill');

test('the catalog links to a skill', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { level: 1, name: site.name })).toBeVisible();
  await page.getByRole('link', { name: /example-skill/ }).click();

  await expect(page).toHaveURL('/skills/example-skill/');
  await expect(page.getByRole('heading', { level: 1, name: 'example-skill' })).toBeVisible();
});

test('a skill page shows its instructions and goes back to the catalog', async ({ page }) => {
  await page.goto('/skills/example-skill/');

  await expect(page.getByRole('heading', { name: 'When to use' })).toBeVisible();
  await page.getByRole('link', { name: 'All skills' }).click();

  await expect(page).toHaveURL('/');
});

test('the copy button copies the install command', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/skills/example-skill/');

  await expect(page.getByText(skillCommand)).toBeVisible();
  await page.getByRole('button', { name: 'Copy' }).click();

  await expect(page.getByRole('button', { name: 'Copied' })).toBeVisible();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(skillCommand);
});

for (const route of routes) {
  test(`${route} has no horizontal scroll at phone width`, async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(route);

    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);

    const { violations } = await new AxeBuilder({ page }).analyze();
    const blocking = violations.filter(({ impact }) => impact === 'serious' || impact === 'critical');
    expect(blocking.map(({ id, help }) => `${id}: ${help}`)).toEqual([]);
  });

  for (const colorScheme of ['light', 'dark'] as const) {
    test(`${route} has no serious accessibility issues in ${colorScheme} mode`, async ({ page }) => {
      await page.emulateMedia({ colorScheme });
      await page.goto(route);

      const { violations } = await new AxeBuilder({ page }).analyze();
      const blocking = violations.filter(({ impact }) => impact === 'serious' || impact === 'critical');

      expect(blocking.map(({ id, help }) => `${id}: ${help}`)).toEqual([]);
    });
  }
}
