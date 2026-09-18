import { Component, Suspense, lazy, type ReactNode } from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConnectionProvider, useConnection } from './context/ConnectionContext';
import { ThemeProvider } from './context/ThemeContext';
import { Button, Empty, Loading } from './components/ui';
const Shell = lazy(() => import('./layouts/WorkspaceShell'));
const Landing = lazy(() => import('./pages/Landing'));
const Connect = lazy(() => import('./pages/Connect'));
const Overview = lazy(() => import('./pages/Overview'));
const ResourcePage = lazy(() => import('./pages/ResourcePage'));
const ImportDataset = lazy(() =>
  import('./pages/EvaluationFlow').then((m) => ({ default: m.ImportDataset }))
);
const NewEvaluation = lazy(() =>
  import('./pages/EvaluationFlow').then((m) => ({ default: m.NewEvaluation }))
);
const DatasetView = lazy(() =>
  import('./pages/EvaluationFlow').then((m) => ({ default: m.DatasetView }))
);
const EvaluationView = lazy(() =>
  import('./pages/EvaluationFlow').then((m) => ({ default: m.EvaluationView }))
);
const JobView = lazy(() => import('./pages/JobView'));
const Settings = lazy(() =>
  import('./pages/SettingsPages').then((m) => ({ default: m.WorkspaceSettingsPage }))
);
const Connection = lazy(() =>
  import('./pages/SettingsPages').then((m) => ({ default: m.ConnectionPage }))
);
const System = lazy(() => import('./pages/SettingsPages').then((m) => ({ default: m.SystemPage })));
const Guide = lazy(() =>
  import('./pages/SettingsPages').then((m) => ({ default: m.DeveloperGuide }))
);
const cache = new QueryClient({
  defaultOptions: {
    queries: { retry: false, refetchOnWindowFocus: false, staleTime: 15000 },
    mutations: { retry: false },
  },
});
function Protected() {
  const { connected, checking } = useConnection();
  return checking ? <Loading /> : connected ? <Outlet /> : <Navigate to="/login" replace />;
}
class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <Empty
        title="This page could not be displayed"
        description="Reload to recover your workspace. If the problem persists, contact your administrator."
        action={<Button onClick={() => location.reload()}>Reload workspace</Button>}
      />
    ) : (
      this.props.children
    );
  }
}
export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={cache}>
        <ThemeProvider>
          <ConnectionProvider>
            <BrowserRouter>
              <Suspense fallback={<Loading />}>
                <Routes>
                  <Route path="/" element={<Landing />} />
                  {['/login', '/register', '/forgot-password'].map((path) => (
                    <Route key={path} path={path} element={<Connect />} />
                  ))}
                  <Route element={<Protected />}>
                    <Route element={<Shell />}>
                      <Route path="overview" element={<Overview />} />
                      <Route path="app" element={<Overview />} />
                      <Route path="projects" element={<ResourcePage kind="projects" />} />
                      <Route path="projects/:projectId">
                        <Route path="datasets/import" element={<ImportDataset />} />
                        <Route path="datasets/:datasetId" element={<DatasetView />} />
                        <Route path="evaluations/new" element={<NewEvaluation />} />
                        <Route path="evaluations/:evaluationId" element={<EvaluationView />} />
                        <Route path="jobs/:jobId" element={<JobView />} />
                        {[
                          'datasets',
                          'evaluations',
                          'benchmarks',
                          'rag',
                          'safety',
                          'policy',
                          'reports',
                          'jobs',
                          'logs',
                        ].map((kind) => (
                          <Route key={kind} path={kind} element={<ResourcePage kind={kind} />} />
                        ))}
                      </Route>
                      <Route path="providers" element={<ResourcePage kind="providers" />} />
                      <Route path="scheduled-jobs" element={<ResourcePage kind="schedules" />} />
                      <Route path="developer" element={<Guide />} />
                      <Route path="profile" element={<Connection />} />
                      <Route path="settings/workspace" element={<Settings />} />
                      <Route path="settings/system" element={<System />} />
                      {[
                        ['keys', 'webhooks'],
                        ['members', 'members'],
                        ['audit', 'audit'],
                        ['billing', 'billing'],
                      ].map(([path, kind]) => (
                        <Route
                          key={path}
                          path={`settings/${path}`}
                          element={<ResourcePage kind={kind} />}
                        />
                      ))}
                      <Route
                        path="*"
                        element={
                          <Empty
                            title="Page not found"
                            description="The requested page does not exist."
                            action={
                              <a className="button" href="/overview">
                                Return to overview
                              </a>
                            }
                          />
                        }
                      />
                    </Route>
                  </Route>
                </Routes>
              </Suspense>
            </BrowserRouter>
          </ConnectionProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
