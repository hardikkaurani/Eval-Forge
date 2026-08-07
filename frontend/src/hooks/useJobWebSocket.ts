import { useEffect, useState, useRef, useCallback } from 'react';

interface WebSocketProgressEventBase {
  job_id: string;
  status?: string;
  current_step?: string;
  timestamp: string;
}

export type WebSocketProgressEvent =
  | (WebSocketProgressEventBase & {
      event: 'started';
    })
  | (WebSocketProgressEventBase & {
      event: 'progress';
      progress?: number;
    })
  | (WebSocketProgressEventBase & {
      event: 'completed';
      result?: Record<string, unknown> | null;
    })
  | (WebSocketProgressEventBase & {
      event: 'failed';
      error?: string;
    })
  | (WebSocketProgressEventBase & {
      event: 'retrying';
      retry_count?: number;
    })
  | (WebSocketProgressEventBase & {
      event: 'cancelled';
    });

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
          const parsed = JSON.parse(event.data);
          if (!parsed || typeof parsed !== 'object' || typeof parsed.event !== 'string') {
            console.warn('Received invalid WebSocket message frame:', parsed);
            return;
          }

          const data = parsed as WebSocketProgressEvent;
          setLastEvent(data);

          if (data.current_step) {
            setCurrentStep(data.current_step);
          }

          switch (data.event) {
            case 'progress':
              if (typeof data.progress === 'number') {
                setProgress(data.progress);
              }
              break;
            case 'completed':
              setProgress(100);
              break;
            case 'started':
            case 'failed':
            case 'retrying':
            case 'cancelled':
              break;
            default:
              // Fallback log for unknown event types
              console.warn(`Unhandled WebSocket event type: ${(data as { event: string }).event}`);
              break;
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
