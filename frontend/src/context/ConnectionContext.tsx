import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { client, DEMO_MODE, SESSION_KEY, storedKey, pageData } from '../services/client';

type Connection = {
  connected: boolean;
  checking: boolean;
  connect: (key: string) => Promise<void>;
  disconnect: () => void;
};
const Context = createContext<Connection | null>(null);
export function ConnectionProvider({ children }: { children: ReactNode }) {
  const cache = useQueryClient();
  const [connected, setConnected] = useState(DEMO_MODE);
  const [checking, setChecking] = useState(!DEMO_MODE && !!storedKey());
  const disconnect = useCallback(() => {
    sessionStorage.removeItem(SESSION_KEY);
    sessionStorage.removeItem('evalforge_project');
    cache.clear();
    setConnected(false);
    setChecking(false);
  }, [cache]);
  useEffect(() => {
    // Remove credentials from the old, fabricated login flow.
    ['auth_token', 'auth_user', 'token'].forEach((key) => localStorage.removeItem(key));
    window.addEventListener('evalforge:disconnected', disconnect);
    return () => window.removeEventListener('evalforge:disconnected', disconnect);
  }, [disconnect]);
  useEffect(() => {
    const key = storedKey();
    if (!key || DEMO_MODE) return;
    const controller = new AbortController();
    client
      .get('/projects?page_size=1', { signal: controller.signal })
      .then((res) => {
        pageData(res.data);
        if (storedKey() === key) setConnected(true);
      })
      .catch(() => {
        if (!controller.signal.aborted && storedKey() === key) disconnect();
      })
      .finally(() => {
        if (!controller.signal.aborted) setChecking(false);
      });
    return () => controller.abort();
  }, [disconnect]);
  const connect = async (key: string) => {
    const cleaned = key.trim();
    if (!cleaned) throw new Error('Enter an API key.');
    const res = await client.get('/projects?page_size=1', { headers: { 'X-API-Key': cleaned } });
    pageData(res.data);
    cache.clear();
    sessionStorage.removeItem('evalforge_project');
    sessionStorage.setItem(SESSION_KEY, cleaned);
    setChecking(false);
    setConnected(true);
  };
  return (
    <Context.Provider value={{ connected, checking, connect, disconnect }}>
      {children}
    </Context.Provider>
  );
}
export function useConnection() {
  const context = useContext(Context);
  if (!context) throw new Error('ConnectionProvider is required');
  return context;
}
