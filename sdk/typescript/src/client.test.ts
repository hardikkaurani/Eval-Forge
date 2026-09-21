declare const process: any;

import { EvalForge } from './client';
import { AuthenticationError } from './errors';

// Test 1: Constructor throws AuthenticationError when no key is provided
try {
  const origEnv = typeof process !== 'undefined' ? process.env.EVALFORGE_API_KEY : undefined;
  if (typeof process !== 'undefined') {
    delete process.env.EVALFORGE_API_KEY;
  }
  let threw = false;
  try {
    new EvalForge();
  } catch (e) {
    if (e instanceof AuthenticationError) {
      threw = true;
    }
  }
  if (!threw) {
    throw new Error('Expected AuthenticationError when apiKey is missing');
  }
  if (typeof process !== 'undefined' && origEnv) {
    process.env.EVALFORGE_API_KEY = origEnv;
  }
} catch (err) {
  console.error('Test 1 failed:', err);
  if (typeof process !== 'undefined') process.exit(1);
}

// Test 2: Constructor succeeds when key is provided
try {
  const client = new EvalForge({ apiKey: 'ef_live_test_key_123', baseUrl: 'http://localhost:8000' });
  if (!client.projects || !client.evaluations || !client.datasets || !client.jobs) {
    throw new Error('Expected client resources to be initialized');
  }
} catch (err) {
  console.error('Test 2 failed:', err);
  if (typeof process !== 'undefined') process.exit(1);
}

console.log('All TypeScript SDK verification assertions passed.');
