import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from './layouts/DashboardLayout';
import { AuthProvider } from './context/AuthContext';
import { WorkspaceProvider } from './context/WorkspaceContext';
import { seedMockData } from './services/api';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// 23 Production Page Views corresponding to all 23 Stitch product screens
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Datasets = lazy(() => import('./pages/Datasets'));
const DatasetDetail = lazy(() => import('./pages/DatasetDetail'));
const NewExperiment = lazy(() => import('./pages/NewExperiment'));
const Evaluations = lazy(() => import('./pages/Evaluations'));
const Benchmarks = lazy(() => import('./pages/Benchmarks'));
const RagEvaluation = lazy(() => import('./pages/RagEvaluation'));
const Providers = lazy(() => import('./pages/Providers'));
const JobsDashboard = lazy(() => import('./pages/JobsDashboard'));
const JobDetail = lazy(() => import('./pages/JobDetail'));
const LogViewer = lazy(() => import('./pages/LogViewer'));
const ScheduledJobs = lazy(() => import('./pages/ScheduledJobs'));
const MembersAccess = lazy(() => import('./pages/MembersAccess'));
const ApiWebhooks = lazy(() => import('./pages/ApiWebhooks'));
const AuditLogs = lazy(() => import('./pages/AuditLogs'));
const WorkspaceSettings = lazy(() => import('./pages/WorkspaceSettings'));
const DeveloperPortal = lazy(() => import('./pages/DeveloperPortal'));
const AiSafety = lazy(() => import('./pages/AiSafety'));
const PolicyEvaluation = lazy(() => import('./pages/PolicyEvaluation'));
const ReportGenerator = lazy(() => import('./pages/ReportGenerator'));
const BillingUsage = lazy(() => import('./pages/BillingUsage'));
const SystemSettings = lazy(() => import('./pages/SystemSettings'));

// Auth Views (Public)
const Login = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Login })));
const Register = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Register })));
const ForgotPassword = lazy(() =>
  import('./pages/AuthPages').then((m) => ({ default: m.ForgotPassword }))
);
const Profile = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Profile })));

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="w-8 h-8 border-4 border-brand-terracotta border-t-transparent rounded-full animate-spin font-mono text-xs"></div>
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
      <AuthProvider>
        <WorkspaceProvider>
          <Router>
            <Suspense fallback={<PageLoader />}>
              <Routes>
                {/* Public Auth Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />

                {/* Protected Dashboard & Profile */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Dashboard />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Profile />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Protected Infrastructure */}
                <Route
                  path="/providers"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Providers />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/scheduled-jobs"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <ScheduledJobs />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Protected Project Scoped Routes */}
                <Route
                  path="/projects/:projectId/datasets"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Datasets />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/datasets/:datasetId"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <DatasetDetail />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/evaluations"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Evaluations />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/evaluations/new"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <NewExperiment />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/benchmarks"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <Benchmarks />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/rag"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <RagEvaluation />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/policy"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <PolicyEvaluation />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/safety"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <AiSafety />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/jobs"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <JobsDashboard />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/jobs/:jobId"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <JobDetail />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/logs"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <LogViewer />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/projects/:projectId/reports"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <ReportGenerator />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Protected Settings & Admin Routes */}
                <Route
                  path="/settings/workspace"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <WorkspaceSettings />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings/members"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <MembersAccess />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings/keys"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <ApiWebhooks />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings/audit"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <AuditLogs />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings/billing"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <BillingUsage />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings/system"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <SystemSettings />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Protected Developer Portal */}
                <Route
                  path="/developer"
                  element={
                    <ProtectedRoute>
                      <DashboardLayout>
                        <DeveloperPortal />
                      </DashboardLayout>
                    </ProtectedRoute>
                  }
                />

                {/* Fallback Catch-all */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </Router>
        </WorkspaceProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
