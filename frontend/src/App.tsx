import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from './layouts/DashboardLayout';
import { seedMockData } from './services/api';

// Lazy load heavy page routes for code splitting
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Datasets = lazy(() => import('./pages/Datasets'));
const Evaluations = lazy(() => import('./pages/Evaluations'));
const Benchmarks = lazy(() => import('./pages/Benchmarks'));
const Providers = lazy(() => import('./pages/Providers'));

const Login = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Login })));
const Register = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Register })));
const ForgotPassword = lazy(() =>
  import('./pages/AuthPages').then((m) => ({ default: m.ForgotPassword }))
);
const Profile = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Profile })));

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
  </div>
);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

function App() {
  // Initialize Mock Data Seed on boot
  useEffect(() => {
    seedMockData();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Main Dashboard Workspace Routes */}
            <Route
              path="/"
              element={
                <DashboardLayout>
                  <Dashboard />
                </DashboardLayout>
              }
            />
            <Route
              path="/profile"
              element={
                <DashboardLayout>
                  <Profile />
                </DashboardLayout>
              }
            />
            <Route
              path="/providers"
              element={
                <DashboardLayout>
                  <Providers />
                </DashboardLayout>
              }
            />
            <Route
              path="/projects/:projectId/datasets"
              element={
                <DashboardLayout>
                  <Datasets />
                </DashboardLayout>
              }
            />
            <Route
              path="/projects/:projectId/evaluations"
              element={
                <DashboardLayout>
                  <Evaluations />
                </DashboardLayout>
              }
            />
            <Route
              path="/projects/:projectId/benchmarks"
              element={
                <DashboardLayout>
                  <Benchmarks />
                </DashboardLayout>
              }
            />

            {/* Fallback Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
