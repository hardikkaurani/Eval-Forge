import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { API_URL, getRecord, storedKey } from '../services/client';

export function useJobProgress(jobId?: string, terminal = false) {
  const cache = useQueryClient();
  const [status, setStatus] = useState('Connecting');
  useEffect(() => {
    if (!jobId || terminal) {
      setStatus('Not streaming');
      return;
    }
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let attempts = 0;
    const poll = async () => {
      if (controller.signal.aborted) return;
      try {
        const record = await getRecord(`/jobs/${jobId}`, controller.signal);
        cache.setQueryData(['job', jobId], record);
        if (['COMPLETED', 'FAILED', 'CANCELLED', 'EXPIRED'].includes(String(record.status))) {
          setStatus('Finished');
          return;
        }
        setStatus('Polling every 5 seconds');
      } catch {
        if (!controller.signal.aborted) setStatus('Connection interrupted');
      }
      if (!controller.signal.aborted && ++attempts < 60)
        timer = setTimeout(() => void poll(), 5000);
      else if (!controller.signal.aborted) setStatus('Paused · Refresh to reconnect');
    };
    const stream = async () => {
      try {
        const response = await fetch(`${API_URL}/jobs/${jobId}/progress/sse`, {
          headers: { 'X-API-Key': storedKey() ?? '' },
          signal: controller.signal,
        });
        if (response.status === 401) {
          window.dispatchEvent(new Event('evalforge:disconnected'));
          return;
        }
        if (response.status === 403 || response.status === 404) {
          setStatus('Access unavailable');
          return;
        }
        if (!response.ok || !response.body) throw new Error('Stream unavailable');
        setStatus('Live updates');
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        while (!controller.signal.aborted) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');
          if (buffer.length > 1_000_000) throw new Error('Invalid stream frame');
          let boundary;
          while ((boundary = buffer.indexOf('\n\n')) >= 0) {
            const frame = buffer.slice(0, boundary);
            buffer = buffer.slice(boundary + 2);
            const data = frame
              .split('\n')
              .filter((line) => line.startsWith('data:'))
              .map((line) => line.slice(5).trim())
              .join('\n');
            if (!data) continue;
            try {
              const event = JSON.parse(data);
              if (event.job_id !== jobId) continue;
              void cache.invalidateQueries({ queryKey: ['job', jobId] });
              if (event.event === 'ended') {
                setStatus('Finished');
                await reader.cancel();
                return;
              }
            } catch {
              continue;
            }
          }
        }
        if (!controller.signal.aborted) void poll();
      } catch {
        if (!controller.signal.aborted) void poll();
      }
    };
    void stream();
    return () => {
      controller.abort();
      if (timer) clearTimeout(timer);
    };
  }, [jobId, terminal, cache]);
  return status;
}
