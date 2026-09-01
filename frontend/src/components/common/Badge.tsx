import React from 'react';
import type { ReactNode } from 'react';

export type BadgeVariant = 'success' | 'warning' | 'error' | 'running' | 'neutral' | 'sky';

export interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  showDot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  showDot = true,
  className = '',
}) => {
  const variantStyles: Record<
    BadgeVariant,
    { bg: string; text: string; border: string; dot: string }
  > = {
    success: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-700 dark:text-emerald-400',
      border: 'border-emerald-500/20',
      dot: 'bg-emerald-500',
    },
    warning: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-700 dark:text-amber-400',
      border: 'border-amber-500/20',
      dot: 'bg-amber-500',
    },
    error: {
      bg: 'bg-red-500/10',
      text: 'text-red-700 dark:text-red-400',
      border: 'border-red-500/20',
      dot: 'bg-red-500',
    },
    running: {
      bg: 'bg-brand-indigo/10',
      text: 'text-brand-indigo dark:text-indigo-400',
      border: 'border-brand-indigo/20',
      dot: 'bg-brand-indigo animate-pulse',
    },
    sky: {
      bg: 'bg-brand-sky/10',
      text: 'text-sky-700 dark:text-brand-sky',
      border: 'border-brand-sky/20',
      dot: 'bg-brand-sky',
    },
    neutral: {
      bg: 'bg-gray-500/10',
      text: 'text-gray-700 dark:text-gray-300',
      border: 'border-gray-500/20',
      dot: 'bg-gray-400',
    },
  };

  const style = variantStyles[variant];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium border ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {showDot && <span className={`w-1.5 h-1.5 rounded-full ${style.dot} shrink-0`} />}
      <span className="uppercase tracking-wider">{children}</span>
    </span>
  );
};
