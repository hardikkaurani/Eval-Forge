import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
  maxHeight?: string;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'json',
  title,
  maxHeight = 'max-h-80',
  className = '',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`rounded-md bg-well-bg border border-well-border overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-well-border bg-chrome-panel/50 text-[11px] font-mono text-chrome-muted">
        <span>{title || language.toUpperCase()}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-chrome-text transition-colors p-1 rounded"
          aria-label="Copy code to clipboard"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      <pre
        className={`p-4 font-mono text-xs text-chrome-text overflow-x-auto ${maxHeight} leading-relaxed select-all`}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
};
