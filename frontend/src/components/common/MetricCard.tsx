import React from 'react';
import type { ReactNode } from 'react';
import { Card } from './Card';

export interface MetricCardProps {
  title: string;
  value: ReactNode;
  subtitle?: string;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  icon?: React.ComponentType<{ className?: string }>;
  variant?: 'workbench' | 'chrome';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendDirection = 'up',
  icon: Icon,
  variant = 'workbench',
  className = '',
}) => {
  const trendColors = {
    up: 'text-emerald-600 bg-emerald-500/10 border-emerald-500/20',
    down: 'text-red-600 bg-red-500/10 border-red-500/20',
    neutral: 'text-gray-600 bg-gray-500/10 border-gray-500/20',
  };

  return (
    <Card variant={variant} padding="md" className={className}>
      <div className="flex items-center justify-between mb-2">
        <span
          className={`text-xs font-mono uppercase tracking-wider ${variant === 'workbench' ? 'text-workbench-muted' : 'text-chrome-muted'}`}
        >
          {title}
        </span>
        {Icon && (
          <div className="p-1.5 rounded-md bg-brand-terracotta/10 text-brand-terracotta border border-brand-terracotta/20">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold tracking-tight">{value}</div>
        {trend && (
          <span
            className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${trendColors[trendDirection]}`}
          >
            {trend}
          </span>
        )}
      </div>

      {subtitle && (
        <p
          className={`text-[11px] mt-1.5 ${variant === 'workbench' ? 'text-workbench-muted' : 'text-chrome-muted'}`}
        >
          {subtitle}
        </p>
      )}
    </Card>
  );
};
