import React from 'react';
import type { ReactNode } from 'react';
import { Inbox } from 'lucide-react';

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: React.ComponentType<{ className?: string }>;
  action?: ReactNode;
  variant?: 'workbench' | 'chrome';
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = Inbox,
  action,
  variant = 'workbench',
  className = '',
}) => {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center rounded-md border ${
        variant === 'workbench'
          ? 'bg-workbench-card border-workbench-border text-workbench-text'
          : 'bg-chrome-panel border-chrome-border text-chrome-text'
      } ${className}`}
    >
      <div className="w-12 h-12 rounded-full bg-brand-terracotta/10 text-brand-terracotta flex items-center justify-center mb-4 border border-brand-terracotta/20">
        <Icon className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold tracking-tight mb-1">{title}</h3>
      <p
        className={`text-xs max-w-sm ${variant === 'workbench' ? 'text-workbench-muted' : 'text-chrome-muted'} mb-5`}
      >
        {description}
      </p>
      {action && <div>{action}</div>}
    </div>
  );
};
