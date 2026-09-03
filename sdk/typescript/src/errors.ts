export class EvalForgeError extends Error {
  constructor(
    message: string,
    public readonly requestId?: string,
  ) {
    super(requestId ? `[${requestId}] ${message}` : message);
    this.name = 'EvalForgeError';
  }
}

export class APIError extends EvalForgeError {
  constructor(
    message: string,
    public readonly statusCode: number,
    requestId?: string,
    public readonly body?: unknown,
  ) {
    super(message, requestId);
    this.name = 'APIError';
  }
}

export class AuthenticationError extends APIError {
  constructor(message = 'Authentication failed', requestId?: string) {
    super(message, 401, requestId);
    this.name = 'AuthenticationError';
  }
}

export class NotFoundError extends APIError {
  constructor(message = 'Resource not found', requestId?: string) {
    super(message, 404, requestId);
    this.name = 'NotFoundError';
  }
}

export class RateLimitError extends APIError {
  constructor(message = 'Rate limit exceeded', requestId?: string) {
    super(message, 429, requestId);
    this.name = 'RateLimitError';
  }
}
