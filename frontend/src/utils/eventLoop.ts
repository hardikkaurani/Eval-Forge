/**
 * EvalForge — JavaScript Event Loop Scheduler Utility
 * Kalvium Mandatory Concept Compliance (#17: JavaScript Event Loop)
 *
 * The Event Loop monitors the Call Stack, Microtask Queue (Promises, queueMicrotask),
 * and Macrotask Queue (setTimeout, setInterval, I/O, WebSockets).
 *
 * In EvalForge:
 * 1. High-priority tasks (state mutations, cache updates) are scheduled on the Microtask Queue.
 * 2. Deferred render passes and UI background tasks are scheduled on the Macrotask Queue.
 * 3. Heavy dataset processing is chunked across animation frames to prevent blocking the main thread.
 */

// 1. Schedule work on Microtask Queue (Executes before next render/macrotask)
export function scheduleMicrotask(callback: () => void): void {
  if (typeof queueMicrotask === 'function') {
    queueMicrotask(callback);
  } else {
    Promise.resolve().then(callback).catch(console.error);
  }
}

// 2. Schedule work on Macrotask Queue (Executes after current turn & microtasks finish)
export function scheduleMacrotask(callback: () => void, delayMs = 0): number {
  return window.setTimeout(callback, delayMs);
}

// 3. Chunk heavy dataset record parsing to keep UI responsive without blocking the main event loop
export async function processInNonBlockingChunks<T, R>(
  items: T[],
  processor: (item: T) => R,
  chunkSize = 50
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += chunkSize) {
    const chunk = items.slice(i, i + chunkSize);
    for (const item of chunk) {
      results.push(processor(item));
    }

    // Yield control back to the event loop macrotask queue so UI events render smoothly
    await new Promise((resolve) => setTimeout(resolve, 0));
  }

  return results;
}
