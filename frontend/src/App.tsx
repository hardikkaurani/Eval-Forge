import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import DashboardLayout from './layouts/DashboardLayout';
import { AuthProvider } from './context/AuthContext';
import { WorkspaceProvider } from './context/WorkspaceContext';
import { seedMockData } from './services/api';

// Existing Lazy Loaded Page Routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Datasets = lazy(() => import('./pages/Datasets'));
const Evaluations = lazy(() => import('./pages/Evaluations'));
const Benchmarks = lazy(() => import('./pages/Benchmarks'));
const Providers = lazy(() => import('./pages/Providers'));
const ScheduledJobs = lazy(() => import('./pages/ScheduledJobs'));

const Login = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Login })));
const Register = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Register })));
const ForgotPassword = lazy(() =>
  import('./pages/AuthPages').then((m) => ({ default: m.ForgotPassword }))
);
const Profile = lazy(() => import('./pages/AuthPages').then((m) => ({ default: m.Profile })));

// Placeholder view builder for upcoming Stitch Batch pages
const createBatchPlaceholder = (title: string, batchName: string) => {
  const PlaceholderView = () => (
    <div className="p-8 rounded-md bg-workbench-card border border-workbench-border text-center space-y-3">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-brand-terracotta/10 text-brand-terracotta border border-brand-terracotta/20">
        Scheduled for {batchName}
      </div>
      <h2 className="text-xl font-bold text-workbench-text">{title}</h2>
      <p className="text-xs text-workbench-muted max-w-md mx-auto">
        This product surface is part of the 23-screen Stitch design integration inventory and will be implemented in {batchName}.
      </p>
    </div>
  );
  PlaceholderView.displayName = `Placeholder_${title.replace(/\s+/g, '')}`;
  return PlaceholderView;
};

// Batch 2 & Batch 4-6 Route Stubs
const DatasetDetail = createBatchPlaceholder('Dataset Detail & Version Timeline', 'Batch 2');
const NewExperiment = createBatchPlaceholder('New Experiment Wizard', 'Batch 3');
const RagEvaluation = createBatchPlaceholder('RAG Evaluation Workbench', 'Batch 4');
const PolicyEvaluation = createBatchPlaceholder('Policy Evaluation & Rules', 'Batch 6');
const AiSafety = createBatchPlaceholder('AI Safety & Toxicity Guardrails', 'Batch 6');
const JobsDashboard = createBatchPlaceholder('Jobs Execution Queue', 'Batch 4');
const JobDetail = createBatchPlaceholder('Job Step Execution Viewer', 'Batch 4');
const LogViewer = createBatchPlaceholder('System & Audit Log Viewer', 'Batch 4');
const ReportGenerator = createBatchPlaceholder('Evaluation Report Generator', 'Batch 6');
const WorkspaceSettings = createBatchPlaceholder('Workspace Quota & Config', 'Batch 5');
const MembersAccess = createBatchPlaceholder('Team Members & RBAC Access', 'Batch 5');
const ApiWebhooks = createBatchPlaceholder('API Keys & Webhook Subscriptions', 'Batch 5');
const AuditLogs = createBatchPlaceholder('Workspace Security Audit Trail', 'Batch 5');
const BillingUsage = createBatchPlaceholder('Billing & License Usage (Backend Gap)', 'Batch 6');
const SystemSettings = createBatchPlaceholder('System Nodes & Worker Telemetry', 'Batch 6');
const DeveloperPortal = createBatchPlaceholder('Developer Portal & MCP Docs', 'Batch 6');

const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="w-8 h-8 border-4 border-brand-terracotta border-t-transparent rounded-full animate-spin"></div>
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
                {/* Auth Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />

                {/* Dashboard & Profile */}
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

                {/* Infrastructure */}
                <Route
                  path="/providers"
                  element={
                    <DashboardLayout>
                      <Providers />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/scheduled-jobs"
                  element={
                    <DashboardLayout>
                      <ScheduledJobs />
                    </DashboardLayout>
                  }
                />

                {/* Project Scoped Routes */}
                <Route
                  path="/projects/:projectId/datasets"
                  element={
                    <DashboardLayout>
                      <Datasets />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/datasets/:datasetId"
                  element={
                    <DashboardLayout>
                      <DatasetDetail />
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
                  path="/projects/:projectId/evaluations/new"
                  element={
                    <DashboardLayout>
                      <NewExperiment />
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
                <Route
                  path="/projects/:projectId/rag"
                  element={
                    <DashboardLayout>
                      <RagEvaluation />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/policy"
                  element={
                    <DashboardLayout>
                      <PolicyEvaluation />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/safety"
                  element={
                    <DashboardLayout>
                      <AiSafety />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/jobs"
                  element={
                    <DashboardLayout>
                      <JobsDashboard />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/jobs/:jobId"
                  element={
                    <DashboardLayout>
                      <JobDetail />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/logs"
                  element={
                    <DashboardLayout>
                      <LogViewer />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/projects/:projectId/reports"
                  element={
                    <DashboardLayout>
                      <ReportGenerator />
                    </DashboardLayout>
                  }
                />

                {/* Settings & Admin Routes */}
                <Route
                  path="/settings/workspace"
                  element={
                    <DashboardLayout>
                      <WorkspaceSettings />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/settings/members"
                  element={
                    <DashboardLayout>
                      <MembersAccess />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/settings/keys"
                  element={
                    <DashboardLayout>
                      <ApiWebhooks />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/settings/audit"
                  element={
                    <DashboardLayout>
                      <AuditLogs />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/settings/billing"
                  element={
                    <DashboardLayout>
                      <BillingUsage />
                    </DashboardLayout>
                  }
                />
                <Route
                  path="/settings/system"
                  element={
                    <DashboardLayout>
                      <SystemSettings />
                    </DashboardLayout>
                  }
                />

                {/* Developer Portal */}
                <Route
                  path="/developer"
                  element={
                    <DashboardLayout>
                      <DeveloperPortal />
                    </DashboardLayout>
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
