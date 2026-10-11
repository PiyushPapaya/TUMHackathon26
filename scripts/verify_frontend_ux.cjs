// Run with UX_PLAYWRIGHT_MODULE pointing to an installed Playwright package.
const { chromium } = require(process.env.UX_PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

async function main() {
  const base = process.env.UX_BASE_URL || 'http://localhost:3001';
  const output = path.resolve(process.env.UX_OUTPUT || 'outputs/ux-review');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true, ...(process.env.UX_CHROMIUM_PATH ? { executablePath: process.env.UX_CHROMIUM_PATH } : {}) });
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`${base}/models`);
    await page.getByText('6 of 6 model and market combinations').waitFor();
    await page.getByLabel('Region', { exact: true }).selectOption('US');
    await page.getByText('2 of 6 model and market combinations').waitFor();
    await page.getByLabel('Search models').fill('no-matching-model');
    await page.getByText('No models match these filters.').waitFor();
    await page.getByRole('button', { name: 'Clear filters' }).click();
    await page.getByText('6 of 6 model and market combinations').waitFor();
    await page.getByText('Loading price reference...', { exact: true }).first().waitFor({ state: 'hidden' });
    await page.screenshot({ path: path.join(output, 'models-desktop.png'), fullPage: true });

    await page.goto(`${base}/cockpit?scenario=G60-US`);
    await page.getByLabel('Search requirements').waitFor();
    const rowsBefore = await page.locator('tbody tr').count();
    assert(rowsBefore > 0);
    await page.getByLabel('Search requirements').fill('nothing-matches-this');
    await page.getByText('No requirements match these filters.').waitFor();
    await page.getByRole('button', { name: 'Clear filters' }).click();
    assert.equal(await page.locator('tbody tr').count(), rowsBefore);
    await page.getByLabel('Engineering effort').selectOption('M');
    assert(await page.locator('tbody tr').count() > 0);
    await page.getByRole('button', { name: 'Clear filters' }).click();
    await page.screenshot({ path: path.join(output, 'cockpit-desktop.png'), fullPage: true });
    await page.locator('tbody tr').first().click();
    await page.getByRole('heading', { name: 'Why this priority?' }).waitFor();
    const chart = await page.getByRole('heading', { name: 'Why this priority?' }).boundingBox();
    assert(chart.y < 500, `Chart starts too low: ${chart.y}`);
    const layout = await page.locator('.requirement-summary').evaluate(element => ({ display: getComputedStyle(element).display, columns: getComputedStyle(element).gridTemplateColumns }));
    assert.equal(layout.display, 'grid', `Detail summary layout: ${JSON.stringify(layout)}`);
    assert(chart.x > 700, `Desktop chart should sit alongside the requirement: ${JSON.stringify(chart)}`);
    await page.getByLabel('Exclude future relevance (preview)').check();
    await page.getByText('Preview', { exact: true }).waitFor();
    await page.getByLabel('Exclude future relevance (preview)').uncheck();
    await page.screenshot({ path: path.join(output, 'detail-desktop.png'), fullPage: true });
    const detailUrl = page.url();
    assert(detailUrl.includes('scenario=G60-US'));
    const requirementId = new URL(detailUrl).pathname.split('/').pop();
    const apiBase = process.env.UX_API_URL || 'http://localhost:8002';
    const requirement = (await (await page.request.get(`${apiBase}/api/requirements/${requirementId}`)).json()).requirement;
    await page.route('**/api/requirements/*/decision', route => route.fulfill({
      json: { requirement, ai_answer: { answer: 'Regression check: answer remains visible after refresh.', supporting_evidence_ids: [], counter_evidence_ids: [], suggested_change: null } },
    }));
    await page.getByRole('button', { name: /^challenge$/i }).click();
    await page.getByLabel('Reason', { exact: true }).fill('Check evidence before making a decision.');
    await page.getByRole('button', { name: 'Submit challenge' }).click();
    await page.getByText('Regression check: answer remains visible after refresh.').waitFor();
    await page.getByRole('button', { name: 'Submit challenge' }).waitFor();
    assert.equal(await page.getByText('Regression check: answer remains visible after refresh.').count(), 1);
    await page.unroute('**/api/requirements/*/decision');
    await page.getByRole('link', { name: 'Back to ranked list' }).click();
    assert(page.url().includes('scenario=G60-US'));

    await page.goto(`${base}/audit?scenario=G60-US`);
    await page.getByLabel('Search history').waitFor();
    await page.getByLabel('Who acted').selectOption('system');
    await page.getByLabel('Action').selectOption('PIPELINE_LOADED');
    await page.getByRole('article', { name: 'Event details' }).waitFor();
    await page.getByLabel('Search history').fill('does-not-exist');
    await page.getByText('No events match this selection.').waitFor();
    await page.getByRole('button', { name: 'Clear filters' }).click();
    await page.screenshot({ path: path.join(output, 'audit-desktop.png'), fullPage: true });

    for (const width of [390, 768]) {
      await page.setViewportSize({ width, height: 844 });
      for (const [name, url] of [['models', `${base}/models`], ['cockpit', `${base}/cockpit?scenario=G60-US`], ['detail', detailUrl], ['audit', `${base}/audit?scenario=G60-US`]]) {
        await page.goto(url);
        await page.locator('main h1').waitFor();
        if (name === 'detail') await page.getByRole('heading', { name: 'Why this priority?' }).waitFor();
        if (name === 'cockpit') await page.getByLabel('Search requirements').waitFor();
        if (name === 'audit') await page.getByLabel('Search history').waitFor();
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
        assert(!overflow, `${name} overflows at ${width}px`);
        await page.screenshot({ path: path.join(output, `${name}-${width}.png`), fullPage: true });
      }
    }
    assert.deepEqual(errors, [], 'Browser runtime errors');
    console.log('PASS: model/region filters, requirement filters, prominent score chart, preview, preserved challenge answer (mocked response), scenario navigation, audit filters, desktop/tablet/mobile overflow checks.');
  } finally { await browser.close(); }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
