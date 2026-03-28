import { beforeEach, describe, expect, it, vi } from 'vitest';

const fetchMock = vi.fn();
vi.stubGlobal('fetch', fetchMock);

describe('api base resolution', () => {
  beforeEach(() => {
    fetchMock.mockReset();
    vi.resetModules();
  });

  it('skips HTML health responses and falls back to a JSON API base', async () => {
    fetchMock
      .mockResolvedValueOnce(
        new Response('<html>dev server</html>', {
          status: 200,
          headers: { 'Content-Type': 'text/html' },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ llm_configured: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ llm_configured: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      );

    const { api } = await import('./client');
    const result = await api.health();

    expect(result).toEqual({ llm_configured: true });
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      '/chat/api/health',
      expect.objectContaining({ method: 'GET' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      '/api/health',
      expect.objectContaining({ method: 'GET' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      '/api/health',
      expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'application/json' }) }),
    );
  });
  it('surfaces a friendly error when no candidate returns JSON', async () => {
    fetchMock
      .mockResolvedValueOnce(
        new Response('<html>chat fallback</html>', {
          status: 200,
          headers: { 'Content-Type': 'text/html' },
        }),
      )
      .mockResolvedValueOnce(
        new Response('missing', {
          status: 404,
          headers: { 'Content-Type': 'text/plain' },
          statusText: 'Not Found',
        }),
      )
      .mockResolvedValueOnce(
        new Response('<html>chat fallback</html>', {
          status: 200,
          headers: { 'Content-Type': 'text/html' },
        }),
      );

    const { api } = await import('./client');

    await expect(api.health()).rejects.toThrow('API 서버 응답 형식을 확인할 수 없습니다. 백엔드 연결 상태를 점검해 주세요.');
  });
});

