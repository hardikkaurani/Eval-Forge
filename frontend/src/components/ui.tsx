import { useEffect, useId, useRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { AlertCircle, ArrowRight, Box, Loader2, X } from 'lucide-react';
import { errorMessage, redactText, type RecordData } from '../services/client';
export function Button({
  children,
  variant = '',
  className = '',
  busy,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: string; busy?: boolean }) {
  return (
    <button
      type="button"
      {...props}
      disabled={props.disabled || busy}
      className={`button ${variant} ${className}`}
      aria-busy={busy || undefined}
    >
      {busy && <Loader2 size={15} className="spin" />}
      {children}
    </button>
  );
}
export function PageHeader({
  title,
  description,
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="actions">{actions}</div>}
    </div>
  );
}
export function Panel({
  title,
  description,
  actions,
  children,
}: {
  title?: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <section className="panel">
      {title && (
        <div className="panel-head">
          <div>
            <h2>{title}</h2>
            {description && <p>{description}</p>}
          </div>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <Loader2 size={18} className="spin" />
      Loading…
    </div>
  );
}
export function ErrorNotice({ error, retry }: { error: unknown; retry?: () => void }) {
  return (
    <div className="notice error" role="alert">
      <AlertCircle size={18} />
      <span>{errorMessage(error)}</span>
      {retry && <Button onClick={retry}>Retry</Button>}
    </div>
  );
}
export function Empty({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Box size={24} />
      </div>
      <h2>{title}</h2>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function Status({ value }: { value: unknown }) {
  const label = String(value ?? 'Unavailable')
    .replace(/_/g, ' ')
    .toLowerCase();
  const tone =
    /completed|active|success|healthy|passed/.test(label) && !/inactive/.test(label)
      ? 'success'
      : /failed|error|revoked/.test(label)
        ? 'danger'
        : /pending|running|queued/.test(label)
          ? 'pending'
          : '';
  return <span className={`badge ${tone}`}>{label.charAt(0).toUpperCase() + label.slice(1)}</span>;
}
export function Field({
  label,
  children,
  hint,
}: {
  label: string;
  children: (id: string) => ReactNode;
  hint?: string;
}) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children(id)}
      {hint && <small>{hint}</small>}
    </div>
  );
}
export function Modal({
  title,
  open,
  close,
  children,
  footer,
}: {
  title: string;
  open: boolean;
  close: () => void;
  children: ReactNode;
  footer?: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const id = useId();
  useEffect(() => {
    const dialog = ref.current;
    const previous = document.activeElement as HTMLElement | null;
    if (open) dialog?.showModal();
    else dialog?.close();
    return () => {
      dialog?.close();
      previous?.focus();
    };
  }, [open]);
  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby={id}
      onKeyDown={(event) => {
        if (event.key !== 'Tab') return;
        const controls = Array.from(
          event.currentTarget.querySelectorAll<HTMLElement>(
            'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [tabindex="0"]'
          )
        ).filter((node) => node.getClientRects().length > 0);
        const first = controls[0],
          last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }}
      onCancel={(e) => {
        e.preventDefault();
        close();
      }}
    >
      <div className="modal-header">
        <h2 id={id}>{title}</h2>
        <Button className="icon-button" variant="quiet" aria-label="Close dialog" onClick={close}>
          <X size={18} />
        </Button>
      </div>
      <div className="modal-body">{children}</div>
      {footer && <div className="modal-footer">{footer}</div>}
    </dialog>
  );
}
export function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'number')
    return value.toLocaleString(undefined, { maximumFractionDigits: 3 });
  if (Array.isArray(value)) return value.map(formatValue).join(', ') || '—';
  if (typeof value === 'object') return JSON.stringify(value);
  return redactText(String(value));
}
export function dateValue(value: unknown) {
  return typeof value !== 'string' || Number.isNaN(Date.parse(value))
    ? '—'
    : new Date(value).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
}
export type Column = { key: string; label: string; render?: (row: RecordData) => ReactNode };
export function DataTable({
  rows,
  columns,
  inspect,
}: {
  rows: RecordData[];
  columns: Column[];
  inspect?: (row: RecordData) => void;
}) {
  return (
    <div className="table-wrap" role="region" aria-label="Results table" tabIndex={0}>
      <table>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} scope="col">
                {c.label}
              </th>
            ))}
            {inspect && (
              <th scope="col">
                <span className="sr-only">Details</span>
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={row.id ?? i}>
              {columns.map((c) => (
                <td key={c.key}>
                  {c.render ? (
                    c.render(row)
                  ) : c.key === 'status' ? (
                    <Status value={row[c.key]} />
                  ) : c.key.endsWith('_at') ? (
                    dateValue(row[c.key])
                  ) : (
                    formatValue(row[c.key])
                  )}
                </td>
              ))}
              {inspect && (
                <td>
                  <Button
                    variant="quiet"
                    onClick={() => inspect(row)}
                    aria-label={`View ${row.name ?? `record ${i + 1}`}`}
                  >
                    <ArrowRight size={16} />
                  </Button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export function RecordDetails({ record }: { record: RecordData }) {
  return (
    <dl className="detail-grid">
      {Object.entries(record)
        .filter(([key]) => !/secret|token|password|api_key|key_hash/i.test(key))
        .map(([key, value]) => (
          <div key={key}>
            <dt>{key.replace(/_/g, ' ')}</dt>
            <dd>
              {typeof value === 'object' && value !== null ? (
                <pre>
                  {JSON.stringify(
                    value,
                    (key, item) =>
                      /secret|token|password|api_key|key_hash|authorization/i.test(key)
                        ? '[redacted]'
                        : item,
                    2
                  )}
                </pre>
              ) : (
                formatValue(value)
              )}
            </dd>
          </div>
        ))}
    </dl>
  );
}
