import { forwardRef } from 'react';
import type { InputHTMLAttributes, ReactNode } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftIcon?: React.ComponentType<{ className?: string }>;
  rightElement?: ReactNode;
  variant?: 'workbench' | 'chrome';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      error,
      hint,
      leftIcon: LeftIcon,
      rightElement,
      variant = 'workbench',
      className = '',
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    const variantStyles = {
      workbench:
        'bg-white border-workbench-border text-workbench-text placeholder:text-workbench-muted focus:border-brand-sky focus:ring-brand-sky/20',
      chrome:
        'bg-well-bg border-chrome-border text-chrome-text placeholder:text-chrome-muted focus:border-brand-sky focus:ring-brand-sky/20',
    };

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className={`block text-xs font-medium ${
              variant === 'workbench' ? 'text-workbench-text' : 'text-chrome-text'
            }`}
          >
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {LeftIcon && (
            <div className="absolute left-3 pointer-events-none text-chrome-muted">
              <LeftIcon className="w-4 h-4" />
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={`w-full text-xs rounded-md border py-2 px-3 transition-colors focus:outline-none focus:ring-2 ${
              LeftIcon ? 'pl-9' : ''
            } ${rightElement ? 'pr-9' : ''} ${variantStyles[variant]} ${
              error ? 'border-red-500 focus:border-red-500 focus:ring-red-500/20' : ''
            } ${className}`}
            {...props}
          />
          {rightElement && <div className="absolute right-3">{rightElement}</div>}
        </div>
        {error && <p className="text-[11px] text-red-500 font-mono">{error}</p>}
        {hint && !error && (
          <p
            className={`text-[11px] ${
              variant === 'workbench' ? 'text-workbench-muted' : 'text-chrome-muted'
            }`}
          >
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
