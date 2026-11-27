import { readFile } from 'node:fs/promises';
import { expect, test } from '@playwright/test';

const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAMAAAACCAIAAAASFvFNAAAAEUlEQVR4nGP8v5QBApgYYAAAHsMBqGMfgmwAAAAASUVORK5CYII=',
  'base64'
);

test('creates a recipe, reconnects after reload, and saves favorites and exports', async ({ page, context }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'canShare', { value: () => true });
    Object.defineProperty(navigator, 'share', {
      value: async (data: ShareData) => {
        const files = await Promise.all(
          (data.files ?? []).map(async (file) => ({
            name: file.name,
            signature: Array.from(new Uint8Array(await file.slice(0, 4).arrayBuffer())),
          }))
        );
        sessionStorage.setItem('fixture-share', JSON.stringify({ title: data.title, text: data.text, files }));
      },
    });
  });
  await page.goto('./');
  await expect(page.getByRole('heading', { name: 'What’s in your kitchen?' })).toBeVisible();
  await page
    .getByLabel('Add an ingredient photo')
    .setInputFiles({ name: 'carrot.png', mimeType: 'image/png', buffer: png });
  await expect(page.getByLabel('Ingredients', { exact: true })).toHaveValue('carrots, cumin');
  if (test.info().project.name === 'phone') {
    const camera = page.getByLabel('Photograph ingredients');
    await expect(camera).toHaveAttribute('capture', 'environment');
    await camera.setInputFiles({ name: 'camera.png', mimeType: 'image/png', buffer: png });
    await expect(page.getByLabel('Ingredients', { exact: true })).toHaveValue('carrots, cumin, carrots, cumin');
  }
  await page.getByLabel('Never use').fill('pork');
  await page.getByRole('button', { name: 'Browse cuisines', exact: true }).click();
  const browser = page.getByRole('dialog', { name: 'Browse cuisines' });
  await browser.getByRole('button', { name: 'The Americas', exact: true }).click();
  await browser.getByRole('button', { name: 'United States', exact: true }).click();
  await browser.getByRole('button', { name: 'Cajun', exact: true }).click();
  await expect(page.getByRole('dialog', { name: 'Cajun', exact: true })).toBeVisible();
  await expect(page.getByText('Classic flavors', { exact: true })).toBeVisible();
  await expect(page.getByRole('img', { name: 'Cajun region highlighted' })).toBeVisible();
  await page.getByRole('button', { name: 'Use Cajun' }).click();
  await page.getByLabel('Pantry defaults').check();
  const accepted = page.waitForResponse(
    (response) => new URL(response.url()).pathname === '/api/jobs' && response.status() === 202
  );
  await page.getByRole('button', { name: 'Make a recipe' }).click();
  const { job_id } = await (await accepted).json();
  await expect(page.getByRole('heading', { name: 'Writing your recipe' })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Cumin Carrots', level: 1, exact: true })).toBeVisible();
  await expect(page.getByText('Roast the carrots.', { exact: true })).toBeVisible();
  const visitor = await page.evaluate(() => localStorage.getItem('chefbot.visitor')!);
  await expect
    .poll(async () =>
      (
        await page.request.get(`http://localhost:8911/api/jobs/${job_id}/events`, {
          headers: { 'X-Visitor-ID': visitor },
        })
      ).status()
    )
    .toBe(404);
  await page.getByRole('button', { name: 'Picture', exact: true }).click();
  await expect(page.getByRole('img', { name: 'Cumin Carrots' })).toBeVisible();
  await page.getByRole('button', { name: 'View picture of Cumin Carrots' }).click();
  const imageReady = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Save picture' }).click();
  expect((await imageReady).suggestedFilename()).toBe('Cumin-Carrots.png');
  await page.getByRole('button', { name: 'Close', exact: true }).click();
  await page.getByRole('button', { name: 'Share', exact: true }).click();
  await page.getByRole('button', { name: 'Share files' }).click();
  await expect(page.getByRole('dialog', { name: 'Share this reply' })).toHaveCount(0);
  const shared = await page.evaluate(() => JSON.parse(sessionStorage.getItem('fixture-share')!));
  expect(shared.title).toBe('Cumin Carrots');
  expect(shared.text).toContain('Roast the carrots.');
  expect(shared.files).toEqual([
    { name: 'Cumin-Carrots.pdf', signature: [37, 80, 68, 70] },
    { name: 'Cumin-Carrots.png', signature: [137, 80, 78, 71] },
  ]);
  await page.getByRole('button', { name: 'Add to favorites' }).click();
  await expect(page.getByRole('button', { name: 'Remove from favorites' })).toHaveAttribute('aria-pressed', 'true');

  const pdfReady = page.waitForEvent('download');
  await page.getByRole('button', { name: 'PDF', exact: true }).click();
  const pdf = await pdfReady;
  expect(pdf.suggestedFilename()).toBe('Cumin-Carrots.pdf');
  expect((await readFile((await pdf.path())!)).subarray(0, 4).toString()).toBe('%PDF');

  await page.getByLabel('Ask a follow-up').fill('Make it spicy');
  await page.getByRole('button', { name: 'Send reply' }).click();
  await expect(page.getByRole('heading', { name: 'Spicy Cumin Carrots', level: 1 })).toBeVisible();
  await page.getByRole('button', { name: 'Edit', exact: true }).click();
  await expect(page.getByLabel('Edit your follow-up')).toHaveValue('Make it spicy');
  await page.getByRole('button', { name: 'Cancel edit' }).click();
  await page.getByRole('button', { name: 'Delete', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Cumin Carrots', level: 1, exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Undo delete' }).click();
  await expect(page.getByRole('heading', { name: 'Spicy Cumin Carrots', level: 1 })).toBeVisible();

  await page.getByRole('button', { name: 'Settings' }).click();
  const backupReady = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export all recipes' }).click();
  const exported = await backupReady;
  const data = await readFile((await exported.path())!);
  const json = JSON.parse(data.toString());
  expect(json.conversations[0].messages).toHaveLength(4);
  expect(json.conversations[0].photos['1']).toMatch(/^data:image\/png;base64,/);
  expect(json.conversations[0].favorite).toBe(true);

  const cdp = await context.newCDPSession(page);
  await cdp.send('Storage.clearDataForOrigin', { origin: new URL(page.url()).origin, storageTypes: 'all' });
  await page.reload();
  await expect(page.getByText('Recipes you make appear here.')).toBeVisible();
  await page.getByRole('button', { name: 'Settings' }).click();
  const chooser = page.getByLabel('Import recipes');
  await chooser.setInputFiles({ name: 'backup.json', mimeType: 'application/json', buffer: data });
  await expect(page.getByText('Added 1, updated 0.')).toBeVisible();
  await chooser.setInputFiles({ name: 'backup.json', mimeType: 'application/json', buffer: data });
  await expect(page.getByText('Added 0, updated 0.')).toBeVisible();
  json.conversations[0].updated += 1;
  await chooser.setInputFiles({
    name: 'newer-backup.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(json)),
  });
  await expect(page.getByText('Added 0, updated 1.')).toBeVisible();
  await page.getByRole('button', { name: 'Back to recipes' }).click();
  await page.getByRole('button', { name: 'Favorites', exact: true }).click();
  await page.getByRole('button', { name: /^Spicy Cumin Carrots/ }).click();
  await expect(page.getByRole('img', { name: 'Cumin Carrots' })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBe(page.viewportSize()!.width);
});
