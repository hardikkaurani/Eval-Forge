import { describe, expect, it } from 'vitest';
import { errorMessage, pageData, unwrap } from './client';
describe('API response normalization', () => {
  it('preserves zero counts', () =>
    expect(pageData({ success: true, data: { items: [], meta: { total_items: 0 } } })).toEqual({
      items: [],
      total: 0,
    }));
  it('reads offset pagination totals', () =>
    expect(pageData({ datasets: [{ id: 'a' }], total: 21 })).toEqual({
      items: [{ id: 'a' }],
      total: 21,
    }));
  it('does not silently treat malformed responses as empty', () =>
    expect(() => pageData({ data: { unknown: true } })).toThrow('unexpected list format'));
  it('rejects false success', () => expect(() => unwrap({ success: false, data: [] })).toThrow());
  it('does not show response secrets in generic errors', () =>
    expect(errorMessage({ response: { data: { secret: 'private' } } })).not.toContain('private'));
});
