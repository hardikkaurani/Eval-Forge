import { useEffect, useState, useRef, useCallback } from 'react';

export interface WebSocketProgressEvent {
  event: 'started' | 'progress' | 'completed' | 'failed' | 'retrying' | 'cancelled';
  job_id: string;
  status?: string;
  progress?: number;
  current_step?: string;
  result?: Record<string, unknown> | null;
  error?: string;
  retry_count?: number;
  timestamp: string;
}

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export function useJobWebSocket(jobId?: string | null, projectId?: string | null) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const [lastEvent, setLastEvent] = useState<WebSocketProgressEvent | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [currentStep, setCurrentStep] = useState<string>('');
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!jobId && !projectId) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host.includes(':5173') ? 'localhost:8000' : window.location.host;

    let path = '';
    if (jobId) {
      path = `/api/v1/jobs/${jobId}/progress?token=dev-token`;
    } else if (projectId) {
      path = `/api/v1/projects/${projectId}/jobs/progress?token=dev-token`;
    }

    const wsUrl = `${protocol}//${host}${path}`;

    setStatus('connecting');

    try {
      const ws = new WebSocket(wsUrl);
      socketRef.current = ws;

      ws.onopen = () => {
        setStatus('connected');
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketProgressEvent = JSON.parse(event.data);
          setLastEvent(data);
          if (typeof data.progress === 'number') {
            setProgress(data.progress);
          }
          if (data.current_step) {
            setCurrentStep(data.current_step);
          }
        } catch (err) {
          console.error('Failed to parse WebSocket message frame', err);
        }
      };

      ws.onerror = () => {
        setStatus('error');
      };

      ws.onclose = () => {
        setStatus('disconnected');
      };
    } catch (e) {
      setStatus('error');
    }
  }, [jobId, projectId]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [connect]);

  return {
    status,
    lastEvent,
    progress,
    currentStep,
    reconnect: connect,
  };
}
