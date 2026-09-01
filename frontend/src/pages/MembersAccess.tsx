import { useState } from 'react';
import { Users, UserPlus, Trash2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Dialog } from '../components/common/Dialog';
import { Input } from '../components/common/Input';

export default function MembersAccess() {
  const [isInviteOpen, setIsInviteOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('Admin');

  const members = [
    {
      id: '1',
      name: 'Hardik Kaurani',
      email: 'hardikkaurani1@gmail.com',
      role: 'Owner',
      status: 'active',
    },
    {
      id: '2',
      name: 'Eval-Forge Lead Architect',
      email: 'architect@evalforge.ai',
      role: 'Admin',
      status: 'active',
    },
    {
      id: '3',
      name: 'QA Benchmark Automation',
      email: 'qa-bot@evalforge.ai',
      role: 'Member',
      status: 'active',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Users className="w-5 h-5 text-brand-terracotta" />
            Members & RBAC Access Control
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Manage organization members, workspace role permissions, and user invites.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={UserPlus} onClick={() => setIsInviteOpen(true)}>
          Invite Team Member
        </Button>
      </div>

      {/* Members Table */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">User Member</th>
                <th className="px-5 py-3 font-medium">Email Address</th>
                <th className="px-5 py-3 font-medium">Assigned Role</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {members.map((m) => (
                <tr key={m.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-semibold text-workbench-text flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-full bg-brand-terracotta/20 text-brand-terracotta flex items-center justify-center font-bold text-xs">
                      {m.name[0]}
                    </div>
                    <span>{m.name}</span>
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                    {m.email}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-workbench-bg border border-workbench-border text-workbench-text">
                      {m.role}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge variant="success">{m.status}</Badge>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button variant="ghost" size="sm" icon={Trash2}>
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Invite Modal */}
      <Dialog
        isOpen={isInviteOpen}
        onClose={() => setIsInviteOpen(false)}
        title="Invite Team Member"
        subtitle="Send an email invitation link to join this workspace"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setIsInviteOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={() => setIsInviteOpen(false)}>
              Send Invitation
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-chrome-text">
          <Input
            label="Email Address"
            placeholder="colleague@company.com"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            variant="chrome"
          />
          <div className="space-y-1.5">
            <label className="block text-xs font-medium text-chrome-text">Role Permission</label>
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="w-full text-xs rounded-md border border-chrome-border bg-well-bg p-2.5 text-chrome-text focus:outline-none"
            >
              <option value="Admin">Admin (Full workspace access)</option>
              <option value="Member">Member (Read/Write datasets & runs)</option>
              <option value="Viewer">Viewer (Read-only metrics access)</option>
            </select>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
