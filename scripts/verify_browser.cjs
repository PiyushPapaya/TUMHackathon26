// Real browser/API integration. Use a separate AUDIT_DB on the backend: this test makes PM decisions.
// BROWSER_PLAYWRIGHT_MODULE may point to an existing Playwright installation.
const { chromium } = require(process.env.BROWSER_PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

async function main() {
  const base = process.env.BROWSER_BASE_URL || 'http://127.0.0.1:3100';
  const api = process.env.BROWSER_API_URL || 'http://127.0.0.1:8100';
  const output = path.resolve(process.env.BROWSER_OUTPUT || 'outputs/repo-audit/browser-current');
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch({ headless: true,
    ...(process.env.BROWSER_CHROMIUM_PATH ? { executablePath: process.env.BROWSER_CHROMIUM_PATH } : {}) });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
  const reason = page.locator('label').filter({ hasText: /^Reason/ }).locator('textarea');
  page.setDefaultTimeout(30000);
  page.setDefaultNavigationTimeout(120000);
  const report = { base, api, checks: [], errors: [], consoleErrors: [], failedResponses: [], started: new Date().toISOString() };
  const criterion = `Browser verification: complete in 1 step. (${report.started})`;
  page.on('pageerror', error => report.errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') report.consoleErrors.push(message.text()); });
  page.on('response', response => {
    if (response.status() >= 400) report.failedResponses.push({ url: response.url(), status: response.status() });
  });
  const check = name => { report.checks.push(name); console.log(`PASS: ${name}`); };
  async function json(route) {
    const response = await page.request.get(`${api}${route}`);
    assert.equal(response.status(), 200, `${route}: ${await response.text()}`);
    return response.json();
  }
  async function open(route, ready) {
    const response = await page.goto(`${base}${route}`, { waitUntil: 'domcontentloaded' });
    assert.equal(response.status(), 200, route);
    await ready.waitFor();
    await page.waitForFunction(() => !Array.from(document.querySelectorAll('main p')).some(p => /^Loading.*\.\.\.$/.test(p.textContent.trim())));
    assert.equal(await page.locator('main').getByRole('alert').count(), 0, `Alert on ${route}`);
  }
  try {
    const scenarios = await json('/api/scenarios');
    assert.equal(scenarios.length, 6);
    if (process.argv.includes('--replay')) {
      const saved = JSON.parse(fs.readFileSync(path.join(output, 'state-before-restart.json'), 'utf8'));
      for (const [sid, requirements] of Object.entries(saved)) {
        assert.deepEqual(await json(`/api/scenarios/${sid}/requirements`), requirements, `Restart state ${sid}`);
        await open(`/cockpit?scenario=${sid}`, page.getByLabel('Search requirements'));
        const edited = requirements.find(r => r.acceptance_criterion.startsWith('Browser verification: complete in 1 step.'));
        assert(edited);
        await open(`/requirements/${edited.id}?scenario=${sid}`, page.getByRole('heading', { name: 'Why this priority?' }));
        await page.locator('.summary-criterion').getByText(edited.acceptance_criterion, { exact: true }).waitFor();
      }
      assert((await json('/api/audit/verify')).valid);
      check('Exact API state and edited criterion visible in browser after backend restart, all six scenarios');
    } else {
      await open('/models', page.getByText('6 of 6 model and market combinations'));
      await page.getByLabel('Region', { exact: true }).selectOption('US');
      await page.getByText('2 of 6 model and market combinations').waitFor();
      await page.getByLabel('Search models').fill('no-matching-model');
      await page.getByText('No models match these filters.').waitFor();
      await page.getByRole('button', { name: 'Clear filters' }).click();
      await page.getByText('6 of 6 model and market combinations').waitFor();
      check('Model and market filters, empty result and reset');

      const saved = {};
      for (const scenario of scenarios) {
        const sid = scenario.id;
        await open(`/cockpit?scenario=${sid}`, page.getByLabel('Search requirements'));
        assert.equal(await page.getByLabel('Scenario', { exact: true }).inputValue(), sid);
        const initial = await json(`/api/scenarios/${sid}/requirements`);
        assert.equal(await page.locator('tbody tr').count(), initial.length);
        await page.getByLabel('Search requirements').fill('nothing-matches-this');
        await page.getByText('No requirements match these filters.').waitFor();
        await page.getByRole('button', { name: 'Clear filters' }).click();
        assert.equal(await page.locator('tbody tr').count(), initial.length);

        // CSV is a file download; the decision memo opens a text document in a new tab.
        for (const label of ['Export CSV']) {
          const link = page.getByRole('link', { name: label, exact: true });
          const downloadPromise = page.waitForEvent('download');
          await link.click();
          const download = await downloadPromise;
          const file = path.join(output, `${sid}-${download.suggestedFilename()}`);
          await download.saveAs(file);
          const content = fs.readFileSync(file, 'utf8');
          assert(content.includes(initial[0].id), `${label} misses requirement ID`);
        }
        const popupPromise = page.waitForEvent('popup');
        await page.getByRole('link', { name: 'Decision memo', exact: true }).click();
        const memoPage = await popupPromise;
        await memoPage.waitForFunction(id => document.body?.innerText.includes(id), initial[0].id);
        const memo = await memoPage.locator('body').innerText();
        assert(memo.includes(initial[0].id), 'Decision memo misses requirement ID');
        fs.writeFileSync(path.join(output, `${sid}-memo.md`), memo);
        await memoPage.close();

        await page.locator('tbody tr').first().click();
        await page.waitForURL(`**/requirements/*?scenario=${sid}`);
        await page.getByRole('heading', { name: 'Why this priority?' }).waitFor();
        assert(new URL(page.url()).searchParams.get('scenario') === sid);
        const rid = new URL(page.url()).pathname.split('/').pop();
        const submit = page.getByRole('button', { name: 'Submit approve', exact: true });
        assert(await submit.isDisabled(), 'Approval without reason must be disabled');
        await reason.fill('   ');
        assert(await submit.isDisabled(), 'Whitespace reason must be disabled');
        const beforePreview = await json(`/api/scenarios/${sid}/requirements`);
        const beforeAudit = await json('/api/audit/verify');
        const previewToggle = page.getByLabel('Exclude future relevance (preview)');
        await previewToggle.focus();
        await previewToggle.press('Space');
        assert(await previewToggle.isChecked(), 'Preview toggle responds to keyboard');
        await page.getByText('Preview', { exact: true }).waitFor();
        await previewToggle.press('Space');
        assert(!(await previewToggle.isChecked()));
        assert.deepEqual(await json(`/api/scenarios/${sid}/requirements`), beforePreview);
        assert.equal((await json('/api/audit/verify')).checked, beforeAudit.checked);

        const finding = page.locator('[id^="signal-"]').first();
        await finding.getByRole('button').first().click();
        assert(await finding.locator('[id^="evidence-"]').count() > 0, `No evidence ${rid}`);

        for (const action of ['approve', 'reject', 'challenge', 'edit']) {
          await page.getByRole('button', { name: action, exact: true }).click();
          if (action === 'challenge') await page.getByLabel('Challenge question').fill('What speaks against it?');
          if (action === 'edit') {
            await reason.fill('Browser verification: unchanged edit.');
            assert(await page.getByRole('button', { name: 'Submit edit', exact: true }).isDisabled(), 'Unchanged edit must be disabled');
            await page.locator('label').filter({ hasText: /^Acceptance criterion/ }).locator('textarea').fill(criterion);
            await page.locator('label').filter({ hasText: /^Effort/ }).locator('select').selectOption('S');
          }
          await reason.fill(`Browser verification: ${action} with evidence review.`);
          const responsePromise = page.waitForResponse(r => r.url().endsWith(`/api/requirements/${rid}/decision`) && r.request().method() === 'POST');
          await page.getByRole('button', { name: `Submit ${action}`, exact: true }).click();
          const response = await responsePromise;
          assert.equal(response.status(), 200, await response.text());
          const result = await response.json();
          await page.getByRole('button', { name: `Submit ${action}`, exact: true }).waitFor();
          if (action === 'challenge') {
            await page.getByText('AI challenge answer', { exact: true }).waitFor();
            await page.getByText(result.ai_answer.answer, { exact: true }).waitFor();
            assert.equal(await page.getByText(result.ai_answer.answer, { exact: true }).count(), 1);
            for (const id of [...result.ai_answer.supporting_evidence_ids.slice(0, 1), ...result.ai_answer.counter_evidence_ids.slice(0, 1)]) {
              await page.getByRole('link', { name: id, exact: true }).first().click();
              await page.locator(`[id="evidence-${id}"]`).first().waitFor();
            }
          } else if (action === 'edit') {
            await page.locator('.summary-criterion').getByText(criterion, { exact: true }).waitFor();
          } else {
            await page.locator('.summary-intro').getByText(action === 'approve' ? 'Approved' : 'Rejected', { exact: true }).waitFor();
          }
        }
        await page.getByRole('link', { name: 'Back to ranked list' }).click();
        await page.getByLabel('Search requirements').waitFor();
        await page.getByText('Fine-tune weights', { exact: true }).click();
        const range = page.getByRole('slider').first();
        await range.focus();
        await range.press('ArrowRight');
        const weightsResponse = page.waitForResponse(r => r.url().endsWith(`/api/scenarios/${sid}/weights`) && r.request().method() === 'PUT');
        await page.getByRole('button', { name: 'Apply weights', exact: true }).click();
        assert.equal((await weightsResponse).status(), 200);
        await page.getByRole('button', { name: 'Apply weights', exact: true }).waitFor();
        saved[sid] = await json(`/api/scenarios/${sid}/requirements`);
        check(`${sid}: exact list count, search/reset, CSV download/memo tab, evidence, score preview without mutation, approve/reject/challenge/edit, weights`);
      }
      fs.writeFileSync(path.join(output, 'state-before-restart.json'), JSON.stringify(saved, null, 2));

      await open('/cockpit?scenario=G60-US', page.getByLabel('Search requirements'));
      await page.getByLabel('Scenario', { exact: true }).selectOption('G68-CN');
      await page.waitForURL('**/cockpit?scenario=G68-CN');
      await page.getByLabel('Search requirements').waitFor();
      assert.equal(await page.locator('tbody tr').count(), saved['G68-CN'].length);
      check('Header scenario switching updates URL and actual requirement list');

      await page.getByText('Ask a prioritization question', { exact: true }).click();
      const beforeLens = await json('/api/audit/verify');
      await page.getByLabel('Question for the prioritization lens').fill('What matters most for the 2030 successor?');
      await page.getByRole('button', { name: 'Ask', exact: true }).click();
      await page.getByRole('button', { name: 'Apply & re-rank', exact: true }).waitFor();
      assert.equal((await json('/api/audit/verify')).checked, beforeLens.checked + 1);
      assert.deepEqual(await json('/api/scenarios/G68-CN/requirements'), saved['G68-CN']);
      const lensApplyResponse = page.waitForResponse(r => r.url().endsWith('/api/scenarios/G68-CN/weights') && r.request().method() === 'PUT');
      await page.getByRole('button', { name: 'Apply & re-rank', exact: true }).click();
      assert.equal((await lensApplyResponse).status(), 200);
      saved['G68-CN'] = await json('/api/scenarios/G68-CN/requirements');
      fs.writeFileSync(path.join(output, 'state-before-restart.json'), JSON.stringify(saved, null, 2));
      check('Real prioritization lens: suggestion logged, state unchanged until Apply, actual re-ranking');

      await open('/evidence?scenario=G60-US', page.getByLabel('Search evidence'));
      await page.getByText('Page 1 of', { exact: false }).waitFor();
      await page.getByRole('button', { name: 'Next', exact: true }).click();
      await page.getByText('Page 2 of', { exact: false }).waitFor();
      await page.getByLabel('Search evidence').fill('nothing-matches-this');
      await page.getByRole('button', { name: 'Search', exact: true }).click();
      await page.getByText('0 results', { exact: true }).waitFor();
      check('Evidence pagination and empty text search');

      await open('/audit?scenario=G60-US', page.getByLabel('Search history'));
      await page.getByText(/Integrity verified/).waitFor();
      await page.getByLabel('Action').selectOption('PM_APPROVE');
      await page.getByRole('article', { name: 'Event details' }).waitFor();
      await page.getByLabel('Search history').fill('does-not-exist');
      await page.getByText('No events match this selection.').waitFor();
      await page.getByRole('button', { name: 'Clear filters' }).click();
      check('Audit integrity, decision action filter and empty search/reset');

      for (const route of ['/', '/overview', '/portfolio', '/benchmarks', '/guide', '/insights?scenario=G60-US']) {
        await open(route, page.locator('main h1').first());
      }
      for (const tab of await page.getByRole('tab').all()) {
        await tab.click();
        assert.equal(await tab.getAttribute('aria-selected'), 'true');
        await page.getByText('Loading insights...', { exact: true }).waitFor({ state: 'hidden' });
        assert.equal(await page.locator('main').getByRole('alert').count(), 0);
      }
      check('Home, overview, portfolio, benchmarks, guide and all insights tabs load');

      const detailRoute = `/requirements/${saved['G60-US'][0].id}?scenario=G60-US`;
      for (const width of [1440, 768, 390]) {
        await page.setViewportSize({ width, height: 1000 });
        for (const [name, route] of [['models', '/models'], ['cockpit', '/cockpit?scenario=G60-US'], ['detail', detailRoute], ['audit', '/audit?scenario=G60-US'], ['portfolio', '/portfolio'], ['evidence', '/evidence?scenario=G60-US']]) {
          console.log(`Checking ${name} at ${width}px`);
          await open(route, page.locator('main h1').first());
          if (name === 'cockpit') await page.getByLabel('Search requirements').waitFor();
          if (name === 'detail') await page.getByRole('heading', { name: 'Why this priority?' }).waitFor();
          if (name === 'audit') await page.getByText(/Integrity verified/).waitFor();
          assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), `${name}: horizontal overflow at ${width}`);
          await page.screenshot({ path: path.join(output, `${name}-${width}.png`), fullPage: true, animations: 'disabled', timeout: 10000 });
        }
        if (width === 390) {
          await page.getByRole('button', { name: 'Open menu', exact: true }).click();
          await page.getByRole('navigation', { name: 'Mobile', exact: true }).getByRole('link', { name: 'Cockpit', exact: true }).click();
          await page.getByLabel('Search requirements').waitFor();
          await page.getByRole('button', { name: 'Open menu', exact: true }).waitFor();
        }
      }
      check('Desktop, tablet and mobile: six views without document overflow; mobile menu navigation');
    }
    assert.deepEqual(report.errors, [], 'Browser runtime errors');
    assert.deepEqual(report.consoleErrors, [], 'Browser console errors');
    assert.deepEqual(report.failedResponses, [], 'Failed browser responses');
    check('No runtime errors or HTTP failures');
    report.passed = true;
  } catch (error) {
    report.passed = false;
    report.failure = error.stack;
    await page.screenshot({ path: path.join(output, 'failure.png'), fullPage: true, timeout: 5000 }).catch(() => {});
    fs.writeFileSync(path.join(output, 'failure-page.txt'), await page.locator('body').innerText({ timeout: 5000 }).catch(() => ''));
    throw error;
  } finally {
    report.finished = new Date().toISOString();
    fs.writeFileSync(path.join(output, process.argv.includes('--replay') ? 'replay-report.json' : 'report.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
