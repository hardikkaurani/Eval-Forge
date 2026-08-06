/**
 * EvalForge — JavaScript Closures Utility Module
 * Kalvium Mandatory Concept Compliance (#16: JavaScript Closures)
 *
 * A closure is the combination of a function bundled together (enclosed)
 * with references to its surrounding state (the lexical environment).
 * In EvalForge, closures are leveraged for:
 * 1. Private state encapsulation (API token storage & rate limit counters).
 * 2. Memoized request caching factories.
 * 3. Event handler currying and state persistence.
 */

// 1. Stateful Memoized Cache Factory utilizing Lexical Closure Scope
export function createMemoizedFetcher<T>(fetcherFn: (key: string) => Promise<T>, ttlMs = 30000) {
  // Encapsulated private state in closure context
  const cache = new Map<string, { data: T; timestamp: number }>();

  return async function getOrFetch(key: string): Promise<T> {
    const cached = cache.get(key);
    const now = Date.now();

    if (cached && now - cached.timestamp < ttlMs) {
      return cached.data;
    }

    const freshData = await fetcherFn(key);
    cache.set(key, { data: freshData, timestamp: now });
    return freshData;
  };
}

// 2. Closure-based Rate Limiter enforcing client-side request throttling
export function createRateLimiter(maxRequests: number, windowMs: number) {
  let timestamps: number[] = []; // Encapsulated private state

  return function allowRequest(): boolean {
    const now = Date.now();
    // Filter out timestamps outside the sliding window
    timestamps = timestamps.filter((t) => now - t < windowMs);

    if (timestamps.length < maxRequests) {
      timestamps.push(now);
      return true;
    }
    return false;
  };
}

// 3. Encapsulated Token Manager using Closure Lexical Scope
export function createTokenManager(initialToken: string = '') {
  let secretToken = initialToken; // Private variable hidden from window/global object

  return {
    getToken: () => secretToken,
    setToken: (newToken: string) => {
      secretToken = newToken;
    },
    clearToken: () => {
      secretToken = '';
    },
    hasToken: () => Boolean(secretToken && secretToken.trim().length > 0),
  };
}
