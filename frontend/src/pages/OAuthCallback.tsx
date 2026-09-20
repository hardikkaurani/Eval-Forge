import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConnection } from '../context/ConnectionContext';
import { ErrorNotice, Loading } from '../components/ui';

export default function OAuthCallback() {
  const { connect } = useConnection();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function handleAuth() {
      try {
        // 1. Check URL hash first (recommended for token transport: #api_key=...&return_to=...)
        const hashStr = window.location.hash.startsWith('#')
          ? window.location.hash.slice(1)
          : window.location.hash;
        const hashParams = new URLSearchParams(hashStr);

        // 2. Check search query params fallback (?api_key=...&return_to=...)
        const searchParams = new URLSearchParams(window.location.search);

        const apiKey = hashParams.get('api_key') || searchParams.get('api_key');
        const returnTo = hashParams.get('return_to') || searchParams.get('return_to') || '/overview';
        const errParam = hashParams.get('error') || searchParams.get('error');

        if (errParam) {
          if (!active) return;
          setError(
            errParam === 'oauth_cancelled'
              ? 'Google sign-in was cancelled.'
              : errParam === 'account_conflict'
                ? 'Identity conflict: this email is already registered to a different Google account.'
                : 'Google authentication failed. Please try again.'
          );
          setTimeout(() => {
            if (active) {
              navigate(`/login?error=${encodeURIComponent(errParam)}`, { replace: true });
            }
          }, 2000);
          return;
        }

        if (!apiKey) {
          if (!active) return;
          navigate('/login', { replace: true });
          return;
        }

        // Connect workspace using the issued session API key
        await connect(apiKey);

        // Strip credentials from URL history for security
        window.history.replaceState(null, '', window.location.pathname);

        if (!active) return;
        // Verify return destination is safe relative path
        const safeDestination = returnTo.startsWith('/') && !returnTo.startsWith('//') ? returnTo : '/overview';
        navigate(safeDestination, { replace: true });
      } catch (err: unknown) {
        if (!active) return;
        const msg = err instanceof Error ? err.message : 'Failed to establish session.';
        setError(msg);
        setTimeout(() => {
          if (active) {
            navigate('/login?error=connection_failed', { replace: true });
          }
        }, 2000);
      }
    }

    handleAuth();

    return () => {
      active = false;
    };
  }, [connect, navigate]);

  if (error) {
    return (
      <div className="login-page bg-[#F6F4EE] dark:bg-[#182026] flex items-center justify-center p-6">
        <div className="max-w-md w-full p-6 bg-white dark:bg-[#202A32] rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] shadow-sm">
          <h2 className="text-lg font-semibold text-[#2E3A44] dark:text-[#F6F4EE] mb-3">
            Authentication Error
          </h2>
          <ErrorNotice error={error} />
          <p className="text-xs text-muted mt-4">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="login-page bg-[#F6F4EE] dark:bg-[#182026] flex flex-col items-center justify-center min-h-screen">
      <Loading />
      <p className="text-sm font-sans text-[#4C5F6B] dark:text-[#B0C2C6] mt-4">
        Establishing your workspace session...
      </p>
    </div>
  );
}
