import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Datasets from './pages/Datasets';
import Evaluations from './pages/Evaluations';
import Benchmarks from './pages/Benchmarks';
import Providers from './pages/Providers';
import { Login, Register, ForgotPassword, Profile } from './pages/AuthPages';
import { seedMockData } from './services/api';

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
      </Router>
    </QueryClientProvider>
  );
}

export default App;
