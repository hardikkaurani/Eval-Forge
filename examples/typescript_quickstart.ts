/**
 * Eval-Forge TypeScript SDK Quickstart Example.
 *
 * Demonstrates:
 * 1. Initializing the @evalforge/sdk client.
 * 2. Creating an evaluation project.
 * 3. Dispatching an automated evaluation run with metrics.
 * 4. Inspecting scored evaluation outputs.
 */

import { EvalForge } from '@evalforge/sdk';

async function runQuickstart() {
  const apiKey = process.env.EVALFORGE_API_KEY || 'ef_live_example_key';
  const baseUrl = process.env.EVALFORGE_BASE_URL || 'http://localhost:8000';

  console.log('='.repeat(60));
  console.log('🚀 Eval-Forge TypeScript SDK — End-to-End Evaluation');
  console.log(`Target Base URL: ${baseUrl}`);
  console.log('='.repeat(60));

  const client = new EvalForge({
    apiKey,
    baseUrl,
  });

  try {
    // 1. Create or list projects
    console.log('\n[1/3] Fetching evaluation projects...');
    const projects = await client.projects.list(1, 5);
    console.log(`✓ Found ${projects.length} existing projects.`);

    const projectId = projects[0]?.id || '00000000-0000-0000-0000-000000000001';

    // 2. Dispatch evaluation run
    console.log('\n[2/3] Submitting evaluation test cases...');
    const testCases = [
      {
        input: 'Summarize the return policy for international orders.',
        actual_output: 'International orders are eligible for return within 30 days. Shipping fees apply.',
        expected_output: '30-day return window for international orders with customer covering return shipping.',
      },
    ];

    const evalRun = await client.evaluations.create(
      projectId,
      'TypeScript SDK Benchmark Run',
      testCases,
      ['accuracy', 'semantic_similarity']
    );

    console.log(`✓ Evaluation Run Triggered: ID=${evalRun.id}`);

    // 3. Inspect results
    console.log('\n[3/3] Inspecting evaluation results...');
    const results = await client.evaluations.listResults(evalRun.id, 10);
    console.log(`✓ Fetched ${results.length} result records.`);

    console.log('\n' + '='.repeat(60));
    console.log('✅ TypeScript SDK workflow finished successfully.');
    console.log('='.repeat(60));
  } catch (error) {
    console.error('Error during execution:', error);
  }
}

runQuickstart();
