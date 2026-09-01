import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './Button';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems?: number;
  pageSize?: number;
  variant?: 'workbench' | 'chrome';
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
  pageSize,
  variant = 'workbench',
  className = '',
}) => {
  if (totalPages <= 1) return null;

  return (
    <div
      className={`flex items-center justify-between px-4 py-3 border-t ${
        variant === 'workbench'
          ? 'border-workbench-border text-workbench-muted'
          : 'border-chrome-border text-chrome-muted'
      } text-xs ${className}`}
    >
      <div className="font-mono text-[11px]">
        {totalItems !== undefined && pageSize !== undefined ? (
          <span>
            Showing{' '}
            <strong
              className={variant === 'workbench' ? 'text-workbench-text' : 'text-chrome-text'}
            >
              {(currentPage - 1) * pageSize + 1}
            </strong>{' '}
            to{' '}
            <strong
              className={variant === 'workbench' ? 'text-workbench-text' : 'text-chrome-text'}
            >
              {Math.min(currentPage * pageSize, totalItems)}
            </strong>{' '}
            of{' '}
            <strong
              className={variant === 'workbench' ? 'text-workbench-text' : 'text-chrome-text'}
            >
              {totalItems}
            </strong>{' '}
            items
          </span>
        ) : (
          <span>
            Page {currentPage} of {totalPages}
          </span>
        )}
      </div>

      <div className="flex items-center gap-1.5">
        <Button
          variant={variant === 'workbench' ? 'outline' : 'secondary'}
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          aria-label="Previous page"
        >
          <ChevronLeft className="w-3.5 h-3.5" />
          <span>Prev</span>
        </Button>
        <Button
          variant={variant === 'workbench' ? 'outline' : 'secondary'}
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          aria-label="Next page"
        >
          <span>Next</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
};
