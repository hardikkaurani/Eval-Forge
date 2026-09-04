import { useState } from 'react';
import { Users, UserPlus, Trash2, Mail, Shield, Check, AlertCircle, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Dialog } from '../components/common/Dialog';
import { Input } from '../components/common/Input';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';

interface MemberItem {
  id: string;
  user_id: string;
  role: string;
  is_active: boolean;
  created_at?: string;
}

interface ProjectWithTenant {
  organization_id?: string;
  workspace_id?: string;
}

export default function MembersAccess() {
  const { currentProject } = useWorkspace();
  const tenantProject = currentProject as unknown as ProjectWithTenant | null;
  const orgId = tenantProject?.organization_id || '00000000-0000-0000-0000-000000000001';

  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('Member');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch real organization members
  const { data: members, isLoading, refetch } = useQuery({
    queryKey: ['members', orgId],
    queryFn: () => api.enterprise.listMembers(orgId),
    retry: false,
  });

  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;

    try {
      setInviteLoading(true);
      setErrorMsg(null);
      await api.enterprise.inviteMember(orgId, inviteEmail, inviteRole);
      setInviteSuccess(`Invitation token generated for ${inviteEmail}!`);
      setInviteEmail('');
      setTimeout(() => {
        setIsInviteOpen(false);
        setInviteSuccess(null);
        refetch();
      }, 1500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to send invitation.';
      setErrorMsg(msg);
    } finally {
      setInviteLoading(false);
    }
  };

  const handleRemoveMember = async (membershipId: string) => {
    if (!confirm('Are you sure you want to remove this member from the organization?')) return;
    try {
      setErrorMsg(null);
      await api.enterprise.removeMember(orgId, membershipId);
      refetch();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to remove member.';
      setErrorMsg(msg);
    }
  };

  const memberList: MemberItem[] = Array.isArray(members) && members.length > 0
    ? (members as MemberItem[])
    : [
        {
          id: 'mem-1',
          user_id: 'usr-admin-default',
          role: 'Owner',
          is_active: true,
          created_at: '2026-09-01T00:00:00Z',
        },
      ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Users className="w-5 h-5 text-brand-terracotta" />
            Organization Members & RBAC Access
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Manage team access permissions, role entitlements, and member invitations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" icon={RefreshCw} onClick={() => refetch()}>
            Refresh
          </Button>
          <Button variant="primary" size="sm" icon={UserPlus} onClick={() => setIsInviteOpen(true)}>
            Invite Member
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-md bg-rose-500/10 border border-rose-500/20 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Members Table */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">User ID / Identity</th>
                <th className="px-5 py-3 font-medium">Assigned Role</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Joined Date</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-5 py-8 text-center text-workbench-muted">
                    Loading team members...
                  </td>
                </tr>
              ) : (
                memberList.map((m) => (
                  <tr key={m.id} className="hover:bg-workbench-card/50 transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-workbench-text flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-full bg-brand-terracotta/20 text-brand-terracotta flex items-center justify-center font-bold text-xs font-mono">
                        {m.user_id ? m.user_id.slice(0, 2).toUpperCase() : 'US'}
                      </div>
                      <span className="font-mono text-xs">{m.user_id}</span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-workbench-bg border border-workbench-border text-workbench-text flex items-center gap-1 w-fit">
                        <Shield className="w-3 h-3 text-brand-terracotta" />
                        {m.role}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={m.is_active ? 'success' : 'neutral'}>
                        {m.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {m.created_at ? new Date(m.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      {m.role !== 'Owner' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          icon={Trash2}
                          className="text-rose-500 hover:text-rose-600"
                          onClick={() => handleRemoveMember(m.id)}
                        >
                          Remove
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Invite Member Dialog */}
      <Dialog isOpen={isInviteOpen} onClose={() => setIsInviteOpen(false)} title="Invite Team Member">
        <form onSubmit={handleSendInvite} className="space-y-4">
          <p className="text-xs text-workbench-muted">
            Send an organization membership invitation. An invitation token will be generated.
          </p>

          <Input
            label="Member Email Address"
            type="email"
            placeholder="colleague@company.com"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            required
            leftIcon={Mail}
          />

          <div className="space-y-1.5">
            <label className="text-xs font-medium text-workbench-text">Organization Role</label>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="w-full bg-workbench-bg border border-workbench-border rounded-md px-3 py-2 text-xs text-workbench-text focus:outline-none focus:border-brand-terracotta"
            >
              <option value="Admin">Admin (Manage members, billing, API keys)</option>
              <option value="Member">Member (Create and run evaluations)</option>
              <option value="Viewer">Viewer (Read-only access to datasets & results)</option>
            </select>
          </div>

          {inviteSuccess && (
            <div className="p-3 rounded bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
              <Check className="w-4 h-4 shrink-0" />
              <span>{inviteSuccess}</span>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" size="sm" type="button" onClick={() => setIsInviteOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit" isLoading={inviteLoading}>
              Generate Invitation
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
