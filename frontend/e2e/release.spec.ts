import { expect, test, type Page } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
const project='11111111-1111-4111-8111-111111111111';
const second='22222222-2222-4222-8222-222222222222';
const job='33333333-3333-4333-8333-333333333333';
async function connect(page:Page){await page.goto('/login');await page.getByLabel('API key',{exact:true}).fill('ef_browser_test_only');await page.getByRole('button',{name:'Connect workspace'}).click();await expect(page.getByRole('heading',{name:'Overview',exact:true})).toBeVisible();}

test('real authentication, dataset import, evaluation execution, results and project isolation',async({page})=>{
  await page.goto('/login');await page.getByLabel('API key',{exact:true}).fill('invalid-key');await page.getByRole('button',{name:'Connect workspace'}).click();await expect(page.getByRole('alert')).toContainText('invalid');
  await connect(page);
  await expect(page.locator('.stat-value').first()).toHaveText('0');
  await page.goto(`/projects/${project}/datasets/import`);
  await page.getByLabel('Dataset name',{exact:true}).fill('Support quality test');
  await page.getByLabel('Dataset file',{exact:true}).setInputFiles({name:'support.csv',mimeType:'text/csv',buffer:Buffer.from('prompt,candidate_output,reference_output\nWhat is 2 plus 2?,4,4\nName the capital of France.,Paris,Paris')});
  await page.getByRole('button',{name:'Import dataset'}).click();
  await expect(page.getByText('Support quality test',{exact:true})).toBeVisible();
  await page.goto(`/projects/${project}/evaluations/new`);
  await page.getByLabel('Evaluation name',{exact:true}).fill('Support baseline');
  await page.getByLabel('Dataset',{exact:true}).selectOption({label:'Support quality test'});
  await expect(page.getByLabel('Version',{exact:true}).locator('option')).toHaveCount(2);
  await page.getByLabel('Version',{exact:true}).selectOption({index:1});
  await page.getByLabel('Judge',{exact:true}).selectOption('rubric');
  await page.getByLabel('Provider',{exact:true}).selectOption('mock');
  await page.getByLabel('Model',{exact:true}).fill('mock-model');
  await page.getByRole('button',{name:'Run evaluation',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Support baseline'})).toBeVisible();
  await expect(page.getByText('Completed',{exact:true})).toBeVisible();
  await expect(page.getByRole('heading',{name:'Test case results'})).toBeVisible();
  await page.getByLabel('Active project',{exact:true}).selectOption(second);
  await expect(page.getByText('No evaluations yet',{exact:true})).toBeVisible();
  await page.getByRole('button',{name:'Disconnect',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Connect your workspace'})).toBeVisible();
  expect(await page.evaluate(()=>sessionStorage.getItem('evalforge_connection'))).toBeNull();
});

test('create project dialog traps focus, saves and restores context',async({page})=>{
  await connect(page);await page.goto('/projects');await page.getByRole('button',{name:'New project',exact:true}).click();
  const dialog=page.getByRole('dialog');await expect(dialog).toBeVisible();
  await dialog.getByLabel('Name',{exact:true}).fill('Browser-created project');
  for(let i=0;i<8;i++){await page.keyboard.press('Tab');expect(await dialog.evaluate(d=>d.contains(document.activeElement))).toBeTruthy();}
  await dialog.getByRole('button',{name:'New project',exact:true}).click();
  await expect(dialog).not.toBeVisible();await expect(page.getByRole('cell',{name:'Browser-created project',exact:true})).toBeVisible();
});

test('API failure stays an error, malformed responses do not become empty or mock data',async({page})=>{
  await connect(page);
  await page.route('**/api/v1/datasets/**',route=>route.fulfill({status:500,contentType:'application/json',body:'{}'}));
  await page.goto(`/projects/${project}/datasets`);await expect(page.getByRole('alert')).toBeVisible();await expect(page.getByText('No datasets yet')).toHaveCount(0);
  await page.unroute('**/api/v1/datasets/**');
  await page.route('**/api/v1/datasets/**',route=>route.fulfill({status:200,contentType:'application/json',body:'{"unexpected":true}'}));
  await page.getByRole('button',{name:'Retry'}).click();await expect(page.getByRole('alert')).toContainText('unexpected list format');
});

for(const theme of ['light','dark']) for(const width of [375,768,1440]){
  test(`all routes, overflow and accessibility · ${theme} · ${width}`,async({page})=>{
    test.setTimeout(240000);await page.setViewportSize({width,height:1000});await connect(page);
    await page.getByLabel('Color theme').selectOption(theme);
    const datasetList=await page.request.get(`/api/v1/datasets/?project_id=${project}`,{headers:{'X-API-Key':'ef_browser_test_only'}});
    const datasets=(await datasetList.json()).datasets;
    const evaluationList=await page.request.get(`/api/v1/experiments/?project_id=${project}`,{headers:{'X-API-Key':'ef_browser_test_only'}});
    const evaluations=(await evaluationList.json()).experiments;
    const detailRoutes=[...datasets.slice(0,1).map((d:{id:string})=>`/projects/${project}/datasets/${d.id}`),...evaluations.slice(0,1).map((d:{id:string})=>`/projects/${project}/evaluations/${d.id}`)];
    const routes=[...detailRoutes,'/','/projects',...['datasets','evaluations','benchmarks','rag','safety','policy','reports','jobs','logs'].map(r=>`/projects/${project}/${r}`),`/projects/${project}/datasets/import`,`/projects/${project}/evaluations/new`,`/projects/${project}/jobs/${job}`,'/providers','/scheduled-jobs','/developer','/profile','/settings/workspace','/settings/system','/settings/keys','/settings/members','/settings/audit','/settings/billing'];
    const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
    for(const route of routes){
      await page.goto(route);await expect(page.locator('main h1')).toBeVisible();await expect(page.locator('.loading')).toHaveCount(0);
      await page.evaluate(()=>document.fonts.ready);await expect.poll(()=>page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),{message:route}).toBeTruthy();
      const report=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
      expect(report.violations.map(v=>`${v.id}: ${v.nodes.map(n=>n.target).join(',')}`),route).toEqual([]);
      await page.screenshot({path:`test-results/routes/${theme}-${width}-${routes.indexOf(route)}.png`,fullPage:true});
    }
    expect(errors).toEqual([]);
    await page.goto('/');await expect(page.locator('.stat-value').first()).toBeVisible();await page.screenshot({path:`test-results/overview-${theme}-${width}.png`,fullPage:true});
    if(width===375){await page.getByRole('button',{name:'Open navigation',exact:true}).click();await expect(page.getByRole('dialog',{name:'Workspace navigation'})).toBeVisible();await page.keyboard.press('Escape');await expect(page.getByRole('button',{name:'Open navigation',exact:true})).toBeFocused();}
  });
}


test('session invalidation, forbidden resources, network loss and rapid project switching',async({page})=>{
  await connect(page);
  await page.route('**/api/v1/datasets/**',route=>route.fulfill({status:403,contentType:'application/json',body:'{}'}));
  await page.goto(`/projects/${project}/datasets`);
  await expect(page.getByRole('alert')).toContainText('permission');
  await page.unroute('**/api/v1/datasets/**');
  await page.route('**/api/v1/datasets/**',route=>route.abort('connectionfailed'));
  await page.getByRole('button',{name:'Retry'}).click();
  await expect(page.getByRole('alert')).toContainText('Unable to reach');
  await page.unroute('**/api/v1/datasets/**');
  await page.route('**/api/v1/datasets/**',async route=>{
    if(route.request().url().includes(project)){await new Promise(r=>setTimeout(r,700));}
    await route.continue();
  });
  await page.goto(`/projects/${project}/datasets`);
  await page.getByLabel('Active project',{exact:true}).selectOption(second);
  await expect(page.getByRole('heading',{name:'No datasets yet'})).toBeVisible();
  await page.waitForTimeout(1000);
  await expect(page.getByRole('cell',{name:'Support quality test'})).toHaveCount(0);
  await page.route('**/api/v1/projects?**',route=>route.fulfill({status:401,contentType:'application/json',body:'{}'}));
  await page.reload();
  await expect(page.getByRole('heading',{name:'Connect your workspace'})).toBeVisible();
  expect(await page.evaluate(()=>sessionStorage.getItem('evalforge_connection'))).toBeNull();
});

for(const theme of ['light','dark'])for(const width of [375,768,1440]){
  test(`connection routes and reduced motion · ${theme} · ${width}`,async({page})=>{
    await page.setViewportSize({width,height:1000});await page.emulateMedia({reducedMotion:'reduce'});
    for(const route of ['/login','/register','/forgot-password']){
      await page.goto(route);await page.getByLabel('Color theme').selectOption(theme);
      await expect(page.getByRole('heading',{name:'Connect your workspace'})).toBeVisible();
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
      expect((await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze()).violations).toEqual([]);
      await page.screenshot({path:`test-results/routes/${theme}-${width}-${route.slice(1)}.png`,fullPage:true});
    }
  });
}


test('authenticated SSE and polling fallback stop on navigation',async({page})=>{
  await connect(page);
  const route=`/projects/${project}/jobs/44444444-4444-4444-8444-444444444444`;
  const streamRequest=page.waitForRequest(r=>r.url().includes('/progress/sse'));
  await page.goto(route);
  const request=await streamRequest;
  expect(request.headers()['x-api-key']).toBe('ef_browser_test_only');
  expect(request.url()).not.toContain('ef_browser_test_only');
  await expect(page.getByText('Live updates',{exact:true})).toBeVisible();
  await page.goto('/projects');
  await page.route('**/progress/sse',r=>r.fulfill({status:503,body:''}));
  await page.goto(route);
  await expect(page.getByText('Polling every 5 seconds',{exact:true})).toBeVisible();
  await page.goto('/projects');
  let requests=0;
  page.on('request',r=>{if(r.url().includes('/jobs/44444444'))requests++;});
  await page.waitForTimeout(5500);
  expect(requests).toBe(0);
});
