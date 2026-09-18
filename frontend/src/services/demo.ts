import type { PageData } from './client';

// Explicit read-only development fixtures. Never used as an API error fallback.
export function demoPage(path: string): PageData {
  const items = path.startsWith('/projects')
    ? [
        {
          id: 'demo-project',
          name: 'Support assistant',
          description: 'Sample evaluation workspace',
          status: 'active',
        },
      ]
    : path.startsWith('/datasets')
      ? [
          {
            id: 'demo-data-1',
            name: 'Customer support questions',
            description: 'Sample prompts for response quality',
            status: 'active',
            visibility: 'private',
            created_at: '2026-09-01T10:00:00Z',
          },
          {
            id: 'demo-data-2',
            name: 'Product knowledge',
            description: 'Sample grounded answers and references',
            status: 'active',
            visibility: 'private',
            created_at: '2026-09-02T10:00:00Z',
          },
        ]
      : path.startsWith('/experiments')
        ? [
            {
              id: 'demo-run-1',
              name: 'Support quality baseline',
              status: 'COMPLETED',
              judge: 'rubric',
              provider: 'openai',
              model: 'Sample model',
              created_at: '2026-09-05T10:00:00Z',
            },
            {
              id: 'demo-run-2',
              name: 'Response consistency',
              status: 'FAILED',
              judge: 'geval',
              provider: 'openai',
              model: 'Sample model',
              created_at: '2026-09-06T10:00:00Z',
            },
          ]
        : [];
  const params = new URL(path, 'https://demo.invalid').searchParams;
  const filtered = items.filter(
    (item) =>
      (!params.get('status') || item.status === params.get('status')) &&
      (!params.get('search') ||
        item.name.toLowerCase().includes(params.get('search')!.toLowerCase()))
  );
  const start = Number(params.get('skip') || 0);
  const limit = Number(params.get('limit') || params.get('page_size') || 20);
  return { items: filtered.slice(start, start + limit), total: filtered.length };
}
