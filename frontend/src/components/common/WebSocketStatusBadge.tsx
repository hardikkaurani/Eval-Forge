import React from 'react';
import { Radio, RefreshCw, WifiOff } from 'lucide-react';
import type { ConnectionStatus } from '../../hooks/useJobWebSocket';

interface Props {
  status: ConnectionStatus;
  onReconnect?: () => void;
}

export const WebSocketStatusBadge: React.FC<Props> = ({ status, onReconnect }) => {
  if (status === 'connected') {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-400 text-xs font-medium shadow-sm shadow-emerald-500/10">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <Radio size={13} className="text-emerald-400" />
        <span>Live WS Stream Active</span>
      </div>
    );
  }

  if (status === 'connecting') {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/10 border border-amber-500/30 rounded-full text-amber-400 text-xs font-medium">
        <RefreshCw size={13} className="animate-spin text-amber-400" />
        <span>Connecting WS Stream...</span>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onReconnect}
      className="inline-flex items-center gap-2 px-3 py-1 bg-gray-800 border border-gray-700 hover:border-gray-600 rounded-full text-gray-400 hover:text-white text-xs font-medium transition cursor-pointer"
      title="Click to reconnect WebSocket"
    >
      <WifiOff size={13} className="text-gray-500" />
      <span>WS Disconnected (Click to Retry)</span>
    </button>
  );
};
