import React, { useState } from 'react';
import { toast } from 'react-toastify';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { profileAPI } from '@/api/endpoints';
import PageHeader from '@/components/PageHeader';
import useAuth from '@/hooks/useAuth';

const ROLE_COLORS = { ADMIN: 'bg-red-500', FACULTY: 'bg-sky-500', STUDENT: 'bg-emerald-500' };

export default function ProfilePage() {
  const { user, refresh } = useAuth();
  const [form, setForm] = useState({ email: user?.email || '', first_name: user?.first_name || '', last_name: user?.last_name || '', phone: user?.phone || '', department: user?.department || '', bio: user?.bio || '' });
  const [pw, setPw] = useState({ old_password: '', new_password: '', confirm: '' });
  const [saving, setSaving] = useState(false);

  const savePf = async (e) => { e.preventDefault(); setSaving(true); try { await profileAPI.update(form); await refresh(); toast.success('Saved!'); } catch { toast.error('Failed'); } finally { setSaving(false); } };
  const changePw = async (e) => { e.preventDefault(); if (pw.new_password !== pw.confirm) { toast.error('Passwords do not match'); return; } try { await profileAPI.changePw({ old_password: pw.old_password, new_password: pw.new_password }); toast.success('Changed!'); setPw({ old_password: '', new_password: '', confirm: '' }); } catch (err) { toast.error(err.response?.data?.old_password?.[0] || 'Failed'); } };

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="Profile" subtitle="Manage your account settings" />
      <div className="max-w-3xl">
        <Card className="mb-5 animate-fade-in"><CardContent className="py-7">
          <div className="flex items-center gap-4">
            <div className={cn('w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-extrabold shadow-lg', ROLE_COLORS[user?.role])}>
              {(user?.first_name || user?.username)?.[0]?.toUpperCase()}
            </div>
            <div><h3 className="text-xl font-bold">{user?.first_name} {user?.last_name}</h3><p className="text-sm text-muted-foreground">@{user?.username}</p><Badge variant={user?.role?.toLowerCase()} className="mt-1">{user?.role}</Badge></div>
          </div>
        </CardContent></Card>

        <Card className="mb-5 animate-fade-in" style={{ animationDelay: '100ms' }}><CardHeader><CardTitle>Edit Profile</CardTitle></CardHeader><CardContent>
          <form onSubmit={savePf} className="space-y-4">
            <div className="grid grid-cols-2 gap-4"><div><Label>First Name</Label><Input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="mt-1" /></div><div><Label>Last Name</Label><Input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="mt-1" /></div></div>
            <div className="grid grid-cols-2 gap-4"><div><Label>Email</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1" /></div><div><Label>Phone</Label><Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} className="mt-1" /></div></div>
            <div><Label>Department</Label><Input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} className="mt-1" /></div>
            <div><Label>Bio</Label><textarea rows={3} className="flex w-full rounded-lg border border-input bg-background px-4 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/20 focus-visible:border-primary mt-1" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} /></div>
            <Button type="submit" disabled={saving}>{saving ? 'Saving...' : 'Save Changes'}</Button>
          </form>
        </CardContent></Card>

        <Card className="animate-fade-in" style={{ animationDelay: '200ms' }}><CardHeader><CardTitle>Change Password</CardTitle></CardHeader><CardContent>
          <form onSubmit={changePw} className="space-y-4">
            <div><Label>Current Password</Label><Input type="password" required value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} className="mt-1" /></div>
            <div className="grid grid-cols-2 gap-4"><div><Label>New Password</Label><Input type="password" required minLength={4} value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} className="mt-1" /></div><div><Label>Confirm</Label><Input type="password" required value={pw.confirm} onChange={(e) => setPw({ ...pw, confirm: e.target.value })} className="mt-1" /></div></div>
            <Button variant="warning" type="submit">Change Password</Button>
          </form>
        </CardContent></Card>
      </div>
    </div>
  );
}