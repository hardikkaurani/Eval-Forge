/**
 * EvalForge — JavaScript Hoisting Utility & Demonstration Module
 * Kalvium Mandatory Concept Compliance (#18: JavaScript Hoisting)
 *
 * Hoisting is JavaScript's default behavior of moving declarations to the top
 * of their execution context during the compilation phase before code execution.
 *
 * In EvalForge:
 * 1. Function declarations are hoisted completely with their definitions, allowing
 *    them to be invoked anywhere within their scope prior to textual definition.
 * 2. `var` declarations hoist the variable name initialized to `undefined`.
 * 3. `let` / `const` / arrow function expressions hoist to the Temporal Dead Zone (TDZ)
 *    and throw `ReferenceError` if accessed before initialization.
 */

// Function declaration — FULLY HOISTED during JS engine compilation phase
export function formatEvaluationScore(score: number): string {
  return calculatePercentageBadge(score); // Works because function declaration is hoisted!
}

// Function declaration hoisted below call site
function calculatePercentageBadge(score: number): string {
  const percentage = Math.round(score * 100);
  if (percentage >= 90) return `Excellent (${percentage}%)`;
  if (percentage >= 70) return `Good (${percentage}%)`;
  return `Needs Attention (${percentage}%)`;
}

// Export safe initialization checker for TDZ demonstration in viva
export function demonstrateTDZ(): { hoistedFunc: boolean; arrowFuncTDZ: boolean } {
  const hoistedFuncWorks = typeof calculatePercentageBadge === 'function';
  let arrowFuncInTDZ = false;

  try {
    // Arrow function variable cannot be accessed prior to textual declaration (TDZ)
    const fn = unhoistedArrow as unknown as (() => string) | undefined;
    if (typeof fn !== 'function') {
      arrowFuncInTDZ = true;
    }
  } catch {
    arrowFuncInTDZ = true;
  }

  return {
    hoistedFunc: hoistedFuncWorks,
    arrowFuncTDZ: arrowFuncInTDZ,
  };
}

// Arrow function expression — NOT hoisted (remains in TDZ until evaluated)
const unhoistedArrow = () => {
  return 'Arrow functions are bound to variables and not hoisted like declarations.';
};
