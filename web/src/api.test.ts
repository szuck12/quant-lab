import { describe, it, expect, vi, afterEach } from 'vitest';
import { fetchConfig } from './api';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('api error handling', () => {
  it('maps network failures to a friendly message', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.reject(new TypeError('Failed to fetch')),
    ));
    await expect(fetchConfig()).rejects.toThrow(/reach the server/i);
  });

  it('maps 5xx to a generic message', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({ ok: false, status: 500, json: async () => ({}) }),
    ));
    await expect(fetchConfig()).rejects.toThrow(/something went wrong/i);
  });

  it('shows a server-provided detail string', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 422,
        json: async () => ({ detail: 'No market data was returned.' }),
      }),
    ));
    await expect(fetchConfig()).rejects.toThrow(/No market data/);
  });

  it('never surfaces a raw object/array detail', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 422,
        json: async () => ({ detail: [{ loc: ['body'], msg: 'internal' }] }),
      }),
    ));
    await expect(fetchConfig()).rejects.toThrow(/Request failed \(422\)/);
  });
});
