import { FileText, Download, Printer } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { CodeBlock } from '../components/common/CodeBlock';

export default function ReportGenerator() {
  const reportMarkdown = `# EVAL-FORGE EXECUTIVE EVALUATION REPORT
Project: Enterprise AI Assistant
Date: September 1, 2026

## Executive Summary
The overall evaluation pass rate across 3 benchmark suites is 94.2%. Model response latencies average 182ms (P95).

### Key Metrics
- Context Faithfulness: 96.4%
- Answer Relevance: 91.2%
- Jailbreak Resistance: 99.2%

## Recommendations
Model candidate GPT-4 Turbo exhibits superior reasoning scores across RAG benchmarks. Recommend deploying to staging.`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-terracotta" />
            Evaluation Report Generator
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Generate executive compliance PDF/Markdown reports summarizing evaluation runs and model telemetry.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" icon={Printer}>
            Print Report
          </Button>
          <Button variant="primary" size="sm" icon={Download}>
            Download Markdown (.md)
          </Button>
        </div>
      </div>

      {/* Report Preview */}
      <Card title="Report Preview" subtitle="Executive Evaluation Summary Markdown Output" padding="none">
        <CodeBlock code={reportMarkdown} language="markdown" maxHeight="max-h-[500px]" />
      </Card>
    </div>
  );
}
