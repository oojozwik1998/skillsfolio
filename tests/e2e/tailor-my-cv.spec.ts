import { expect, test } from '@playwright/test';
import { installFolder, repository } from '../../src/data/tailor-my-cv';
import { cloneCommand, repositoryUrl } from '../../src/lib/skills';

const command = cloneCommand(repository, installFolder);

test('the catalog card opens the skill page', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('link', { name: /tailor-my-cv/ }).click();

  await expect(page).toHaveURL('/skills/tailor-my-cv/');
  await expect(page.getByRole('heading', { level: 1, name: 'How tailor-my-cv works' })).toBeVisible();
});

test('the install section copies the clone command and links to the repository', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/skills/tailor-my-cv/');

  await page.getByRole('button', { name: 'Copy' }).click();

  await expect(page.getByRole('button', { name: 'Copied' })).toBeVisible();
  expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(command);
  await expect(page.getByRole('link', { name: 'View repository on GitHub' })).toHaveAttribute(
    'href',
    repositoryUrl(repository),
  );
});

test('clicking a stage opens its step', async ({ page }) => {
  await page.goto('/skills/tailor-my-cv/');
  const step = page.locator('#step-5');

  await expect(step).not.toHaveAttribute('open');
  await page.getByRole('link', { name: /Assesses the fit/ }).click();

  await expect(step).toHaveAttribute('open');
  await expect(page).toHaveURL(/#step-5$/);
});

test('steps expand and collapse, and only the first starts open', async ({ page }) => {
  await page.goto('/skills/tailor-my-cv/');

  await expect(page.locator('details[open]')).toHaveCount(1);
  await expect(page.locator('details')).toHaveCount(9);

  await page.locator('#step-9 summary').click();
  await expect(page.getByText('It does not apply.')).toBeVisible();
});

test('the layout comparison images load', async ({ page }) => {
  await page.goto('/skills/tailor-my-cv/');

  for (const image of await page.locator('figure img').all()) {
    await image.scrollIntoViewIfNeeded();
    await expect.poll(() => image.evaluate((el: HTMLImageElement) => el.naturalWidth)).toBeGreaterThan(0);
  }
});
