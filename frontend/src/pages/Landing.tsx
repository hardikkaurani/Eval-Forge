import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  CheckCircle2,
  Database,
  ExternalLink,
  FlaskConical,
  Github,
  Layers,
  Menu,
  ShieldCheck,
  Terminal,
  X,
  Zap,
} from 'lucide-react';
import { useConnection } from '../context/ConnectionContext';
import { ThemeControl } from '../layouts/WorkspaceShell';

export default function Landing() {
  const { connected } = useConnection();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeCodeTab, setActiveCodeTab] = useState<'python' | 'cli' | 'rest'>('python');

  return (
    <div className="editorial-landing min-h-screen bg-[var(--bg)] text-[var(--text)] selection:bg-[#B0C2C6]/30 transition-colors duration-200">
      {/* ─── Top Editorial Notification / Status Bar ─── */}
      <div className="border-b border-[var(--border)] bg-[var(--surface)]/80 px-4 py-2 text-xs text-[var(--muted)]">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-[#0284C7] animate-pulse" />
            <span className="font-mono font-medium">Evalium v1.0.0 Released</span>
            <span className="hidden sm:inline text-[#7E939C]">|</span>
            <span className="hidden sm:inline">Production-grade AI Evaluation Infrastructure</span>
          </div>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/hardikkaurani/Evalium"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#0284C7] transition-colors flex items-center gap-1 font-mono"
            >
              <Github size={13} />
              <span>GitHub</span>
              <ExternalLink size={11} />
            </a>
            <ThemeControl />
          </div>
        </div>
      </div>

      {/* ─── Main Minimal Header ─── */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[var(--bg)]/90 border-b border-[var(--border)]">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          {/* Brand Monogram & Wordmark */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 rounded-lg overflow-hidden border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#2E3A44] p-1 shadow-sm transition-transform duration-200 group-hover:scale-105">
              <img src="/logo.png" alt="Evalium Emblem" className="w-full h-full object-contain" />
            </div>
            <div className="flex flex-col">
              <span className="font-serif text-2xl font-semibold tracking-tight text-[#2E3A44] dark:text-[#F6F4EE] leading-none">
                Evalium
              </span>
              <span className="text-[10px] font-mono tracking-widest uppercase text-[#7E939C] mt-1">
                AI Infrastructure
              </span>
            </div>
          </Link>

          {/* Desktop Minimal Nav */}
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-[#4C5F6B] dark:text-[#B0C2C6]">
            <a
              href="#platform"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Platform
            </a>
            <a
              href="#capabilities"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Capabilities
            </a>
            <a
              href="#workflow"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Workflow
            </a>
            <a
              href="#code"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Developer SDK
            </a>
            <a
              href="#architecture"
              className="hover:text-[#0284C7] dark:hover:text-[#38BDF8] transition-colors"
            >
              Architecture
            </a>
          </nav>

          {/* Primary Action CTA */}
          <div className="hidden md:flex items-center gap-4">
            {connected ? (
              <Link
                to="/overview"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#2E3A44] hover:bg-[#1C252C] dark:bg-[#F6F4EE] dark:hover:bg-[#EFECE4] text-[#F6F4EE] dark:text-[#2E3A44] text-xs font-semibold uppercase tracking-wider transition-all duration-200 shadow-sm"
              >
                <span>Enter Workspace</span>
                <ArrowRight size={14} />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-xs font-semibold uppercase tracking-wider text-[#4C5F6B] hover:text-[#0284C7] dark:text-[#B0C2C6] dark:hover:text-[#38BDF8] transition-colors px-3 py-2"
                >
                  Sign In
                </Link>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-[#0284C7] hover:bg-[#0369A1] text-white text-xs font-semibold uppercase tracking-wider transition-all duration-200 shadow-sm hover:shadow"
                >
                  <span>Connect Workspace</span>
                  <ArrowRight size={14} />
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-2">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-[#4C5F6B] dark:text-[#B0C2C6] border border-[#DDE4E1] dark:border-[#2E3A44] rounded-md"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden px-6 py-6 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026] space-y-4">
            <a
              href="#platform"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Platform
            </a>
            <a
              href="#capabilities"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Capabilities
            </a>
            <a
              href="#workflow"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Workflow
            </a>
            <a
              href="#code"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Developer SDK
            </a>
            <a
              href="#architecture"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-base font-medium text-[#4C5F6B] dark:text-[#B0C2C6]"
            >
              Architecture
            </a>
            <div className="pt-4 border-t border-[#DDE4E1] dark:border-[#2E3A44] flex flex-col gap-3">
              <Link
                to={connected ? '/overview' : '/login'}
                className="w-full text-center py-3 rounded-full bg-[#0284C7] text-white text-sm font-semibold uppercase tracking-wider"
              >
                {connected ? 'Enter Workspace' : 'Connect Workspace'}
              </Link>
            </div>
          </div>
        )}
      </header>

      {/* ─── Hero Section: Alpaca Editorial Composition ─── */}
      <section className="relative overflow-hidden pt-12 pb-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
            {/* Left Column: Editorial Typography & Value */}
            <div className="lg:col-span-7 space-y-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] text-[11px] font-mono tracking-wider uppercase text-[#7E939C] dark:text-[#B0C2C6] bg-white/50 dark:bg-black/20">
                <ShieldCheck size={13} className="text-[#0284C7]" />
                <span>Deterministic AI Quality & Benchmark Suite</span>
              </div>

              <h1 className="font-serif text-5xl sm:text-6xl lg:text-7xl font-light tracking-tight text-[#2E3A44] dark:text-[#F6F4EE] leading-[1.08]">
                Evaluate AI <br />
                <span className="italic font-normal text-[#0284C7] dark:text-[#38BDF8]">
                  with unyielding rigor.
                </span>
              </h1>

              <p className="text-lg sm:text-xl text-[#4C5F6B] dark:text-[#B0C2C6] font-normal leading-relaxed max-w-2xl">
                Production-grade infrastructure for evaluating LLMs, RAG pipelines, and agentic
                systems. Benchmark reasoning, measure grounding, and enforce safety across
                reproducible datasets.
              </p>

              <div className="pt-2 flex flex-wrap items-center gap-4">
                <Link
                  to={connected ? '/overview' : '/login'}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-[#2E3A44] hover:bg-[#1C252C] dark:bg-[#F6F4EE] dark:hover:bg-[#EFECE4] text-[#F6F4EE] dark:text-[#2E3A44] text-sm font-semibold uppercase tracking-wider transition-all duration-200 shadow-md group"
                >
                  <span>{connected ? 'Open Workspace' : 'Get Started with Workspace'}</span>
                  <ArrowRight
                    size={16}
                    className="transition-transform group-hover:translate-x-1"
                  />
                </Link>

                <a
                  href="https://github.com/hardikkaurani/Evalium"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-7 py-4 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] hover:border-[#2E3A44] dark:hover:border-[#F6F4EE] text-sm font-medium text-[#2E3A44] dark:text-[#F6F4EE] bg-transparent transition-all duration-200"
                >
                  <Github size={17} />
                  <span>Star on GitHub</span>
                  <ArrowUpRight size={14} className="text-[#7E939C]" />
                </a>
              </div>

              {/* Technical Credibility Strip */}
              <div className="pt-6 border-t border-[#DDE4E1] dark:border-[#2E3A44] grid grid-cols-3 gap-6 font-mono text-xs text-[#7E939C] dark:text-[#B0C2C6]">
                <div>
                  <div className="text-xl sm:text-2xl font-serif text-[#2E3A44] dark:text-[#F6F4EE]">
                    180+
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">Automated Tests</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-serif text-[#2E3A44] dark:text-[#F6F4EE]">
                    114
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">REST Endpoints</div>
                </div>
                <div>
                  <div className="text-xl sm:text-2xl font-serif text-[#2E3A44] dark:text-[#F6F4EE]">
                    v1.0.0
                  </div>
                  <div className="text-[11px] uppercase tracking-wider mt-0.5">
                    Production Ready
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Live Product Card Showcase */}
            <div className="lg:col-span-5 relative">
              <div className="relative rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] p-6 shadow-xl space-y-6">
                {/* Header of Preview Box */}
                <div className="flex items-center justify-between border-b border-[#DDE4E1] dark:border-[#2E3A44] pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-md bg-[#2E3A44] flex items-center justify-center p-1 border border-[#DDE4E1]">
                      <img src="/logo.png" alt="Evalium" className="w-full h-full object-contain" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                        Live Evaluation Dashboard
                      </div>
                      <div className="text-[10px] font-mono text-[#7E939C]">
                        Project: Chatbot Alignment
                      </div>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[11px] font-mono font-medium flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    Completed
                  </span>
                </div>

                {/* Score Summary Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026]">
                    <div className="text-[11px] font-mono uppercase text-[#7E939C]">Pass Rate</div>
                    <div className="text-3xl font-serif font-bold text-[#0284C7] dark:text-[#38BDF8] mt-1">
                      94.2%
                    </div>
                    <div className="text-[10px] text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                      48 of 51 test criteria passed
                    </div>
                  </div>
                  <div className="p-4 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#F6F4EE] dark:bg-[#182026]">
                    <div className="text-[11px] font-mono uppercase text-[#7E939C]">
                      Mean Latency
                    </div>
                    <div className="text-3xl font-serif font-bold text-[#2E3A44] dark:text-[#F6F4EE] mt-1">
                      342ms
                    </div>
                    <div className="text-[10px] text-[#4C5F6B] dark:text-[#B0C2C6] mt-1">
                      p95 @ 610ms across runs
                    </div>
                  </div>
                </div>

                {/* Live Model Comparison Row */}
                <div className="space-y-3">
                  <div className="text-xs font-mono uppercase tracking-wider text-[#7E939C]">
                    Recent Judge Evaluations
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          Claude 3.5 Sonnet Alignment
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">G-Eval Score: 4.85 / 5.0</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          GPT-4o RAG Grounding
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">Precision: 92.4%</span>
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#1C252C] text-xs">
                      <div className="flex items-center gap-2">
                        <CheckCircle2 size={15} className="text-emerald-500" />
                        <span className="font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                          Safety & Toxicity Filter v2
                        </span>
                      </div>
                      <span className="font-mono text-[#7E939C]">0 Violations</span>
                    </div>
                  </div>
                </div>

                {/* Quick Link into Overview */}
                <Link
                  to={connected ? '/overview' : '/login'}
                  className="block text-center text-xs font-medium text-[#0284C7] dark:text-[#38BDF8] hover:underline pt-1"
                >
                  Inspect complete evaluation results in workspace →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Editorial Problem & Philosophy Statement ─── */}
      <section className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
            The Engineering Dilemma
          </div>
          <h2 className="font-serif text-3xl sm:text-5xl font-light text-[#2E3A44] dark:text-[#F6F4EE] leading-snug">
            “AI systems look impressive in isolation. <br />
            <span className="italic font-normal">
              Production systems demand empirical evidence.”
            </span>
          </h2>
          <div className="w-16 h-[1px] bg-[#0284C7] mx-auto" />
          <p className="text-base sm:text-lg text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed max-w-3xl mx-auto font-normal">
            Without structured benchmarks and automated evaluation pipelines, teams deploy updates
            into the dark. Evalium introduces continuous statistical verification across reasoning
            quality, retrieval faithfulness, hallucination detection, and safety policies.
          </p>
        </div>
      </section>

      {/* ─── Numbered Editorial Capabilities (01 - 06) ─── */}
      <section id="capabilities" className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="mb-16 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C] mb-2">
                01 — 06 Pillars
              </div>
              <h2 className="font-serif text-4xl sm:text-5xl font-light text-[#2E3A44] dark:text-[#F6F4EE]">
                Architected for precision.
              </h2>
            </div>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6] max-w-md">
              Every capability is built as a first-class citizen of the evaluation lifecycle.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                num: '01',
                title: 'Versioned Datasets',
                desc: 'Upload CSV, JSON, and JSONL datasets with validated schemas, golden references, and schema mapping.',
                icon: Database,
              },
              {
                num: '02',
                title: 'G-Eval & LLM Judges',
                desc: 'Run multi-criteria rubrics with chain-of-thought explanations. Quantify alignment, coherence, and accuracy.',
                icon: FlaskConical,
              },
              {
                num: '03',
                title: 'RAG Faithfulness',
                desc: 'Measure retrieval precision, context recall, and output groundedness against your reference knowledge base.',
                icon: Layers,
              },
              {
                num: '04',
                title: 'Deep Analytics & Drift',
                desc: 'Observe score distributions, monitor model regressions, detect failure slices, and export audit trails.',
                icon: BarChart3,
              },
              {
                num: '05',
                title: 'Distributed Async Jobs',
                desc: 'Decoupled Celery and Redis queuing handles high-volume asynchronous batch evaluation workloads.',
                icon: Zap,
              },
              {
                num: '06',
                title: 'Developer Platform',
                desc: 'Command-line CLI, Model Context Protocol (MCP), webhooks, and SDKs in Python, TypeScript, Java, and Go.',
                icon: Terminal,
              },
            ].map((cap) => (
              <div
                key={cap.num}
                className="group relative p-8 rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] hover:border-[#0284C7] dark:hover:border-[#38BDF8] transition-all duration-200"
              >
                <div className="flex items-center justify-between mb-6">
                  <span className="font-serif text-3xl font-light text-[#7E939C] group-hover:text-[#0284C7] transition-colors">
                    {cap.num}
                  </span>
                  <div className="p-2.5 rounded-lg border border-[#DDE4E1] dark:border-[#2E3A44] text-[#4C5F6B] dark:text-[#B0C2C6]">
                    <cap.icon size={18} />
                  </div>
                </div>
                <h3 className="font-serif text-2xl font-medium text-[#2E3A44] dark:text-[#F6F4EE] mb-3">
                  {cap.title}
                </h3>
                <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                  {cap.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Workflow Section: Connected Journey ─── */}
      <section
        id="workflow"
        className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/50 dark:bg-[#1C252C]/40"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Execution Pipeline
            </div>
            <h2 className="font-serif text-4xl sm:text-5xl font-light text-[#2E3A44] dark:text-[#F6F4EE]">
              The Evaluation Lifecycle
            </h2>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              From dataset ingestion to production release gating in a single unified protocol.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 relative">
            {[
              { step: '01', title: 'Dataset', desc: 'Versioned golden questions and contexts' },
              { step: '02', title: 'Evaluation', desc: 'G-Eval rubrics and LLM judge models' },
              { step: '03', title: 'Async Job', desc: 'Distributed queue execution on Celery' },
              { step: '04', title: 'Verdict', desc: 'Score distributions and reasoning logs' },
              { step: '05', title: 'Decision', desc: 'Automated CI/CD pass/fail gates' },
            ].map((st) => (
              <div
                key={st.step}
                className="p-6 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="font-mono text-xs text-[#0284C7] dark:text-[#38BDF8] font-bold">
                    STEP {st.step}
                  </div>
                  <h4 className="font-serif text-xl font-medium text-[#2E3A44] dark:text-[#F6F4EE] mt-2">
                    {st.title}
                  </h4>
                </div>
                <p className="text-xs text-[#4C5F6B] dark:text-[#B0C2C6] leading-normal">
                  {st.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Developer SDK & Code Showcase ─── */}
      <section id="code" className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-5 space-y-6">
              <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
                First-Party Tooling
              </div>
              <h2 className="font-serif text-4xl sm:text-5xl font-light text-[#2E3A44] dark:text-[#F6F4EE]">
                Designed for engineers, <br />
                <span className="italic font-normal text-[#0284C7] dark:text-[#38BDF8]">
                  native to your stack.
                </span>
              </h2>
              <p className="text-sm sm:text-base text-[#4C5F6B] dark:text-[#B0C2C6] leading-relaxed">
                Integrate evaluation steps directly into your unit tests, regression pipelines, or
                agent loops. Use our lightweight Python SDK, TypeScript client, or CLI to trigger
                runs in one line.
              </p>

              <div className="space-y-3 pt-2">
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>Python SDK with async client support</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>TypeScript / JavaScript SDK for Next.js & Node</span>
                </div>
                <div className="flex items-center gap-3 text-xs font-medium text-[#2E3A44] dark:text-[#F6F4EE]">
                  <CheckCircle2 size={16} className="text-[#0284C7]" />
                  <span>Standalone terminal CLI (`evalium run ...`)</span>
                </div>
              </div>
            </div>

            <div className="lg:col-span-7">
              <div className="rounded-2xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#2E3A44] text-[#F6F4EE] overflow-hidden shadow-xl">
                {/* Code Tabs */}
                <div className="flex items-center justify-between border-b border-[#4C5F6B]/40 px-4 py-3 bg-[#232E37]">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/80" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                    <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  </div>
                  <div className="flex items-center gap-2">
                    {(['python', 'cli', 'rest'] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveCodeTab(tab)}
                        className={`px-3 py-1 rounded text-xs font-mono uppercase tracking-wider transition-colors ${
                          activeCodeTab === tab
                            ? 'bg-[#0284C7] text-white'
                            : 'text-[#B0C2C6] hover:text-white'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Code Block */}
                <div className="p-6 font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto">
                  {activeCodeTab === 'python' && (
                    <pre className="text-[#DDE4E1]">
                      <span className="text-[#7E939C]"># pip install evalforge</span>
                      <br />
                      <span className="text-[#38BDF8]">from</span> evalforge{' '}
                      <span className="text-[#38BDF8]">import</span> Evalium
                      <br />
                      <br />
                      client = Evalium(api_key=
                      <span className="text-emerald-400">&quot;ef_live_...&quot;</span>)
                      <br />
                      <br />
                      <span className="text-[#7E939C]"># Trigger asynchronous G-Eval run</span>
                      <br />
                      job = client.evaluations.create(
                      <br />
                      &nbsp;&nbsp;project_id=
                      <span className="text-emerald-400">&quot;proj_chatbot_v1&quot;</span>,<br />
                      &nbsp;&nbsp;dataset_id=
                      <span className="text-emerald-400">&quot;ds_qa_golden&quot;</span>,<br />
                      &nbsp;&nbsp;metrics=[
                      <span className="text-emerald-400">
                        &quot;g_eval_faithfulness&quot;
                      </span>,{' '}
                      <span className="text-emerald-400">&quot;context_precision&quot;</span>],
                      <br />
                      &nbsp;&nbsp;judge_model=
                      <span className="text-emerald-400">&quot;gpt-4o&quot;</span>
                      <br />
                      )
                      <br />
                      <br />
                      results = job.wait_for_completion()
                      <br />
                      <span className="text-[#38BDF8]">print</span>(f
                      <span className="text-emerald-400">
                        &quot;Pass rate: &#123;results.pass_rate&#125;%&quot;
                      </span>
                      )
                    </pre>
                  )}

                  {activeCodeTab === 'cli' && (
                    <pre className="text-[#DDE4E1]">
                      <span className="text-[#7E939C]"># Install Evalium CLI</span>
                      <br />
                      $ pip install evalforge-cli
                      <br />
                      <br />
                      <span className="text-[#7E939C]"># Authenticate workspace</span>
                      <br />
                      $ evalium login --api-key ef_live_...
                      <br />
                      <br />
                      <span className="text-[#7E939C]"># Run evaluation against dataset</span>
                      <br />
                      $ evalium run \
                      <br />
                      &nbsp;&nbsp;--project &quot;proj_chatbot_v1&quot; \
                      <br />
                      &nbsp;&nbsp;--dataset &quot;./tests/benchmarks.jsonl&quot; \
                      <br />
                      &nbsp;&nbsp;--metric g-eval \
                      <br />
                      &nbsp;&nbsp;--threshold 0.85
                    </pre>
                  )}

                  {activeCodeTab === 'rest' && (
                    <pre className="text-[#DDE4E1]">
                      curl -X POST https://evalforge-backend.onrender.com/api/v1/evaluations/run \
                      <br />
                      &nbsp;&nbsp;-H{' '}
                      <span className="text-emerald-400">
                        &quot;Authorization: Bearer ef_live_...&quot;
                      </span>{' '}
                      \
                      <br />
                      &nbsp;&nbsp;-H{' '}
                      <span className="text-emerald-400">
                        &quot;Content-Type: application/json&quot;
                      </span>{' '}
                      \
                      <br />
                      &nbsp;&nbsp;-d &apos;&#123;
                      <br />
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      <span className="text-[#38BDF8]">&quot;project_id&quot;</span>:{' '}
                      <span className="text-emerald-400">&quot;proj_chatbot_v1&quot;</span>,
                      <br />
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      <span className="text-[#38BDF8]">&quot;dataset_id&quot;</span>:{' '}
                      <span className="text-emerald-400">&quot;ds_qa_golden&quot;</span>,
                      <br />
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      <span className="text-[#38BDF8]">&quot;judge_model&quot;</span>:{' '}
                      <span className="text-emerald-400">&quot;claude-3-5-sonnet&quot;</span>
                      <br />
                      &nbsp;&nbsp;&#125;&apos;
                    </pre>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Architecture & Open Source ─── */}
      <section
        id="architecture"
        className="py-24 border-b border-[#DDE4E1] dark:border-[#2E3A44] bg-[#EFECE4]/30 dark:bg-[#1C252C]/20"
      >
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16 space-y-3">
            <div className="text-xs font-mono uppercase tracking-widest text-[#7E939C]">
              Infrastructure Topology
            </div>
            <h2 className="font-serif text-4xl sm:text-5xl font-light text-[#2E3A44] dark:text-[#F6F4EE]">
              Full-Stack Architecture
            </h2>
            <p className="text-sm text-[#4C5F6B] dark:text-[#B0C2C6]">
              Modular, transparent, and battle-tested on standard production primitives.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-center font-mono text-xs">
            {[
              { name: 'FastAPI', role: 'Backend Core', badge: 'Python 3.12' },
              { name: 'PostgreSQL', role: 'State Store', badge: 'SQLAlchemy' },
              { name: 'Redis', role: 'Queue & Cache', badge: 'In-Memory' },
              { name: 'Celery', role: 'Async Workers', badge: 'Distributed' },
              { name: 'React 18', role: 'Web Interface', badge: 'TypeScript' },
              { name: 'Stripe', role: 'Billing & RBAC', badge: 'Enterprise' },
            ].map((tech) => (
              <div
                key={tech.name}
                className="p-5 rounded-xl border border-[#DDE4E1] dark:border-[#2E3A44] bg-white dark:bg-[#202A32] space-y-2"
              >
                <div className="text-sm font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
                  {tech.name}
                </div>
                <div className="text-[11px] text-[#4C5F6B] dark:text-[#B0C2C6]">{tech.role}</div>
                <span className="inline-block px-2 py-0.5 rounded bg-[#DDE4E1] dark:bg-[#2E3A44] text-[10px] text-[#7E939C] dark:text-[#B0C2C6]">
                  {tech.badge}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Final Editorial Call-To-Action ─── */}
      <section className="py-24">
        <div className="max-w-5xl mx-auto px-6 text-center space-y-8">
          <div className="w-16 h-16 rounded-2xl mx-auto border border-[#DDE4E1] dark:border-[#2E3A44] bg-[#2E3A44] p-2 shadow-lg">
            <img src="/logo.png" alt="Evalium Emblem" className="w-full h-full object-contain" />
          </div>

          <h2 className="font-serif text-4xl sm:text-6xl font-light text-[#2E3A44] dark:text-[#F6F4EE]">
            Ready to evaluate <br />
            <span className="italic font-normal text-[#0284C7] dark:text-[#38BDF8]">
              with complete confidence?
            </span>
          </h2>

          <p className="text-base sm:text-lg text-[#4C5F6B] dark:text-[#B0C2C6] max-w-xl mx-auto">
            Connect your workspace, import your first dataset, and benchmark your models today.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to={connected ? '/overview' : '/login'}
              className="px-8 py-4 rounded-full bg-[#0284C7] hover:bg-[#0369A1] text-white text-sm font-semibold uppercase tracking-wider transition-all duration-200 shadow-md"
            >
              {connected ? 'Enter Workspace Now →' : 'Launch Workspace →'}
            </Link>
            <a
              href="https://github.com/hardikkaurani/Evalium/blob/main/docs/api.md"
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 rounded-full border border-[#B0C2C6] dark:border-[#4C5F6B] hover:border-[#2E3A44] text-sm font-medium text-[#2E3A44] dark:text-[#F6F4EE] transition-colors"
            >
              Read Documentation ↗
            </a>
          </div>
        </div>
      </section>

      {/* ─── Minimal Editorial Footer ─── */}
      <footer className="border-t border-[#DDE4E1] dark:border-[#2E3A44] py-12 bg-[#EFECE4] dark:bg-[#151D23] text-xs text-[#7E939C]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Evalium" className="w-6 h-6 object-contain" />
            <span className="font-serif text-base font-semibold text-[#2E3A44] dark:text-[#F6F4EE]">
              Evalium.
            </span>
            <span className="text-[#B0C2C6]">·</span>
            <span>Production-grade AI Evaluation Infrastructure</span>
          </div>

          <div className="flex items-center gap-6">
            <a
              href="https://github.com/hardikkaurani/Evalium"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#0284C7] transition-colors"
            >
              GitHub
            </a>
            <a
              href="https://github.com/hardikkaurani/Evalium/blob/main/docs/ARCHITECTURE.md"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#0284C7] transition-colors"
            >
              Architecture
            </a>
            <a
              href="https://github.com/hardikkaurani/Evalium/blob/main/LICENSE"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#0284C7] transition-colors"
            >
              MIT License
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
