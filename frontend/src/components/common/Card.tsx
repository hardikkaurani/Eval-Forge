import React from 'react';
import type { HTMLAttributes, ReactNode } from 'react';

export interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  children: ReactNode;
  title?: ReactNode;
  subtitle?: ReactNode;
  action?: ReactNode;
  variant?: 'workbench' | 'chrome';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  action,
  variant = 'workbench',
  padding = 'md',
  className = '',
  ...props
}) => {
  const variantClasses = {
    workbench: 'bg-workbench-card border-workbench-border text-workbench-text shadow-subtle',
    chrome: 'bg-chrome-panel border-chrome-border text-chrome-text shadow-chrome',
  };

  const paddingClasses = {
    none: 'p-0',
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-6',
  };

  return (
    <div
      className={`border rounded-md ${variantClasses[variant]} ${className}`}
      {...props}
    >
      {(title || action) && (
        <div className={`flex items-center justify-between border-b ${variant === 'workbench' ? 'border-workbench-border' : 'border-chrome-border'} px-5 py-3.5`}>
          <div>
            {title && <h3 className="text-sm font-semibold tracking-tight">{title}</h3>}
            {subtitle && <p className={`text-xs ${variant === 'workbench' ? 'text-workbench-muted' : 'text-chrome-muted'} mt-0.5`}>{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={paddingClasses[padding]}>{children}</div>
    </div>
  );
};
