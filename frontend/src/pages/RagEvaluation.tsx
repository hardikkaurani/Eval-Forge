import { Sparkles, FileText, Search, CheckCircle, Layers } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { MetricCard } from '../components/common/MetricCard';

export default function RagEvaluation() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-brand-terracotta" />
            RAG Retrieval & Generation Evaluation
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Faithfulness, relevance, context precision, and hallucination scoring for RAG pipelines.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Sparkles}>
          Run RAG Benchmark
        </Button>
      </div>

      {/* RAG Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Context Faithfulness"
          value="96.4%"
          subtitle="Grounding accuracy"
          trend="+1.2%"
          trendDirection="up"
          icon={CheckCircle}
        />
        <MetricCard
          title="Answer Relevance"
          value="91.2%"
          subtitle="Prompt match score"
          trend="+0.8%"
          trendDirection="up"
          icon={FileText}
        />
        <MetricCard
          title="Context Precision"
          value="88.7%"
          subtitle="Retrieved chunk ranking"
          trend="-0.4%"
          trendDirection="down"
          icon={Search}
        />
        <MetricCard
          title="Context Recall"
          value="94.0%"
          subtitle="Golden document coverage"
          trend="+2.1%"
          trendDirection="up"
          icon={Layers}
        />
      </div>

      {/* RAG Results Table */}
      <Card padding="none" title="Retrieval Context Trace Records">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">User Query</th>
                <th className="px-5 py-3 font-medium">Retrieved Chunks</th>
                <th className="px-5 py-3 font-medium">Faithfulness</th>
                <th className="px-5 py-3 font-medium">Relevance</th>
                <th className="px-5 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              <tr className="hover:bg-workbench-card/50 transition-colors">
                <td className="px-5 py-3.5 font-semibold text-workbench-text max-w-xs truncate">
                  What is the SLA for enterprise API endpoints?
                </td>
                <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                  3 chunks (doc_id: 4812)
                </td>
                <td className="px-5 py-3.5 font-mono text-emerald-600 font-semibold">98.5%</td>
                <td className="px-5 py-3.5 font-mono text-emerald-600 font-semibold">95.0%</td>
                <td className="px-5 py-3.5">
                  <Badge variant="success">passed</Badge>
                </td>
              </tr>
              <tr className="hover:bg-workbench-card/50 transition-colors">
                <td className="px-5 py-3.5 font-semibold text-workbench-text max-w-xs truncate">
                  How does worker queue failover operate during network partitions?
                </td>
                <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                  5 chunks (doc_id: 1092)
                </td>
                <td className="px-5 py-3.5 font-mono text-emerald-600 font-semibold">94.2%</td>
                <td className="px-5 py-3.5 font-mono text-amber-600 font-semibold">86.1%</td>
                <td className="px-5 py-3.5">
                  <Badge variant="warning">review</Badge>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
