import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Database, ArrowLeft, Upload, Plus, Search, Loader2, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import type { Dataset, DatasetVersion, DatasetRecord } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Input } from '../components/common/Input';
import { Dialog } from '../components/common/Dialog';
import { CodeBlock } from '../components/common/CodeBlock';
import { Pagination } from '../components/common/Pagination';

export default function DatasetDetail() {
  const navigate = useNavigate();
  const { projectId, datasetId } = useParams<{ projectId: string; datasetId: string }>();

  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [versions, setVersions] = useState<DatasetVersion[]>([]);
  const [records, setRecords] = useState<DatasetRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<DatasetRecord | null>(null);
  const [activeVersion, setActiveVersion] = useState<string>('v1.0.0');

  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  // Import Dialog & File Validation State
  const [isImportOpen, setIsImportOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    const file = e.target.files?.[0];
    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.size === 0) {
      setUploadError('Selected file is empty (0 bytes).');
      setSelectedFile(null);
      return;
    }

    const MAX_SIZE = 50 * 1024 * 1024; // 50MB limit
    if (file.size > MAX_SIZE) {
      setUploadError('File size exceeds maximum allowed limit of 50MB.');
      setSelectedFile(null);
      return;
    }

    const ext = file.name.split('.').pop()?.toLowerCase();
    const ALLOWED = ['csv', 'json', 'jsonl', 'parquet'];
    if (!ext || !ALLOWED.includes(ext)) {
      setUploadError(
        `Unsupported file extension (.${ext || 'none'}). Supported formats: .csv, .json, .jsonl, .parquet`
      );
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile || isUploading) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();
      formData.append('project_id', projectId || '1');
      formData.append('dataset_name', dataset?.name || 'Dataset Import');
      formData.append('version_label', activeVersion);
      formData.append('file', selectedFile);

      await api.datasets.upload(formData);

      const recs = await api.datasets.records.list(datasetId || 'd1', activeVersion);
      setRecords(recs || []);

      setSelectedFile(null);
      setIsImportOpen(false);
    } catch (err: unknown) {
      console.error('File import failed:', err);
      setUploadError('Upload failed. Server rejected the import file format or payload structure.');
    } finally {
      setIsUploading(false);
    }
  };

  // Reset pagination to first page when dataset, version, or search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [datasetId, activeVersion, searchQuery]);

  useEffect(() => {
    let isSubscribed = true;
    const fetchDetails = async () => {
      if (!datasetId) return;
      try {
        const d = await api.datasets.get(datasetId);
        if (!isSubscribed) return;
        setDataset(d);
        const vers = await api.datasets.versions.list(datasetId);
        if (!isSubscribed) return;
        setVersions(vers || []);
        const recs = await api.datasets.records.list(datasetId, activeVersion);
        if (!isSubscribed) return;
        setRecords(recs || []);
      } catch (err) {
        if (isSubscribed) console.error('Failed to load dataset details:', err);
      }
    };
    fetchDetails();
    return () => {
      isSubscribed = false;
    };
  }, [datasetId, activeVersion]);

  const filteredRecords = records.filter(
    (r) =>
      r.input_prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.candidate_output && r.candidate_output.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const totalPages = Math.ceil(filteredRecords.length / pageSize) || 1;
  const paginatedRecords = filteredRecords.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div className="space-y-6">
      {/* Top Navigation & Breadcrumb */}
      <div className="flex items-center gap-3">
        <Button
          variant="outline"
          size="sm"
          icon={ArrowLeft}
          onClick={() => navigate(`/projects/${projectId || '1'}/datasets`)}
        >
          Back to Datasets
        </Button>
      </div>

      {/* Dataset Header Card */}
      <Card padding="lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <Database className="w-6 h-6 text-brand-terracotta" />
              <h1 className="text-xl font-bold tracking-tight text-workbench-text">
                {dataset?.name || 'Golden Evaluation Dataset'}
              </h1>
              <Badge variant="sky">{dataset?.visibility || 'private'}</Badge>
            </div>
            <p className="text-xs text-workbench-muted">
              {dataset?.description || 'Curated evaluation prompts and reference outputs.'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              icon={Upload}
              onClick={() => {
                setSelectedFile(null);
                setUploadError(null);
                setIsImportOpen(true);
              }}
            >
              Import Version
            </Button>
            <Button variant="primary" size="sm" icon={Plus}>
              Add Case
            </Button>
          </div>
        </div>
      </Card>

      {/* Main Records Table Card */}
      <Card
        title="Dataset Test Cases"
        subtitle="Prompt inputs, target references, and model predictions"
        padding="none"
      >
        {/* Controls Bar */}
        <div className="p-4 border-b border-workbench-border flex flex-col md:flex-row md:items-center justify-between gap-3 bg-workbench-card/30">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
            <span className="text-[10px] font-mono uppercase text-workbench-muted font-bold shrink-0">
              Version:
            </span>
            {(versions.length > 0 ? versions : [{ id: 'v1', label: 'v1.0.0' }]).map((v) => (
              <button
                key={v.id}
                onClick={() => setActiveVersion(v.label)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                  activeVersion === v.label
                    ? 'bg-brand-terracotta text-white font-semibold'
                    : 'bg-workbench-card border border-workbench-border text-workbench-muted hover:text-workbench-text'
                }`}
              >
                {v.label}
              </button>
            ))}
          </div>

          <div className="w-full md:w-64">
            <Input
              placeholder="Search test cases..."
              leftIcon={Search}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              variant="workbench"
            />
          </div>
        </div>

        {/* Records Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Input Prompt</th>
                <th className="px-5 py-3 font-medium">Reference Output</th>
                <th className="px-5 py-3 font-medium">Score</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {paginatedRecords.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-workbench-muted font-mono">
                    No matching test cases found in this version checkpoint.
                  </td>
                </tr>
              ) : (
                paginatedRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-workbench-card/50 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      #{r.id}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-text max-w-xs truncate">
                      {r.input_prompt}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted max-w-xs truncate">
                      {r.reference || r.candidate_output || 'N/A'}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs">
                      <span className="font-semibold text-emerald-600">
                        {r.score !== undefined ? (r.score * 100).toFixed(0) + '%' : '95%'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={r.passed !== false ? 'success' : 'error'}>
                        {r.passed !== false ? 'passed' : 'failed'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Button variant="ghost" size="sm" onClick={() => setSelectedRecord(r)}>
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={filteredRecords.length}
          pageSize={pageSize}
        />
      </Card>

      {/* Record Inspection Dialog */}
      {selectedRecord && (
        <Dialog
          isOpen={!!selectedRecord}
          onClose={() => setSelectedRecord(null)}
          title={`Record #${selectedRecord.id} Details`}
          subtitle="Full prompt payload and reasoning evaluation"
          maxWidth="2xl"
        >
          <div className="space-y-4 text-chrome-text">
            <div>
              <span className="text-xs font-mono text-chrome-muted block mb-1">Input Prompt</span>
              <CodeBlock code={selectedRecord.input_prompt} language="text" />
            </div>
            <div>
              <span className="text-xs font-mono text-chrome-muted block mb-1">
                Reference Output
              </span>
              <CodeBlock
                code={selectedRecord.reference || selectedRecord.candidate_output || 'N/A'}
                language="text"
              />
            </div>
            {selectedRecord.reasoning && (
              <div>
                <span className="text-xs font-mono text-chrome-muted block mb-1">
                  Judge Reasoning
                </span>
                <p className="text-xs p-3 rounded bg-well-bg border border-well-border text-chrome-text font-mono">
                  {selectedRecord.reasoning}
                </p>
              </div>
            )}
          </div>
        </Dialog>
      )}

      {/* File Import Dialog with Client-Side UX Validation */}
      <Dialog
        isOpen={isImportOpen}
        onClose={() => {
          if (!isUploading) {
            setIsImportOpen(false);
            setSelectedFile(null);
            setUploadError(null);
          }
        }}
        title="Import Evaluation Test Cases"
        subtitle="Upload CSV, JSON, or JSONL files to create a new dataset version"
      >
        <div className="space-y-4 text-chrome-text">
          {uploadError && (
            <div className="p-3 bg-red-900/30 border border-red-500/50 rounded flex items-center gap-2 text-xs text-red-300 font-mono">
              <AlertTriangle className="w-4 h-4 text-red-400 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          <div className="p-8 border-2 border-dashed border-chrome-border rounded-md text-center bg-well-bg space-y-3">
            <Upload className="w-8 h-8 text-brand-terracotta mx-auto" />
            <p className="text-xs text-chrome-text font-semibold">
              {selectedFile
                ? `Selected: ${selectedFile.name}`
                : 'Drag and drop your file here, or click to browse'}
            </p>
            <p className="text-[11px] text-chrome-muted">
              Supports .csv, .json, .jsonl, .parquet files up to 50MB
            </p>

            <input
              type="file"
              ref={fileInputRef}
              accept=".csv,.json,.jsonl,.parquet"
              className="hidden"
              onChange={handleFileChange}
            />

            <Button
              variant="outline"
              size="sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {selectedFile ? 'Change Selected File' : 'Browse File'}
            </Button>
          </div>

          <div className="flex justify-end gap-2 pt-2 border-t border-chrome-border">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsImportOpen(false)}
              disabled={isUploading}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleUploadSubmit}
              disabled={isUploading || !selectedFile}
            >
              {isUploading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" /> Uploading...
                </span>
              ) : (
                'Submit Import'
              )}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
