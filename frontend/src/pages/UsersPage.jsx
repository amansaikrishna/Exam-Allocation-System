import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { UserPlus, Trash2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogBody } from '@/components/ui/dialog';
import { usersAPI } from '@/api/endpoints';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';

export default function UsersPage() {
  const [list, setList] = useState([]); const [ld, setLd] = useState(true); const [tab, setTab] = useState('FACULTY'); const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ username: '', password: '', first_name: '', last_name: '', email: '', department: '', role: 'FACULTY' });

  const load = () => { setLd(true); usersAPI.list({ role: tab }).then((r) => setList(r.data)).catch(() => toast.error('Failed')).finally(() => setLd(false)); };
  useEffect(() => { load(); }, [tab]);
  const submit = async (e) => { e.preventDefault(); try { await usersAPI.create(form); toast.success('Created!'); setShowAdd(false); setForm({ username: '', password: '', first_name: '', last_name: '', email: '', department: '', role: 'FACULTY' }); load(); } catch (err) { toast.error(err.response?.data?.error || 'Failed'); } };
  const del = (id, u) => { if (!confirm(`Delete ${u}?`)) return; usersAPI.delete(id).then(() => { toast.success('Deleted'); load(); }).catch((e) => toast.error(e.response?.data?.error || 'Failed')); };

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="Users" subtitle="Manage faculty, students, and admin accounts">
        <Button onClick={() => setShowAdd(true)}><UserPlus className="h-4 w-4" />Add User</Button>
      </PageHeader>
      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>{['FACULTY', 'STUDENT', 'ADMIN'].map((r) => <TabsTrigger key={r} value={r}>{r}</TabsTrigger>)}</TabsList>
        {['FACULTY', 'STUDENT', 'ADMIN'].map((r) => <TabsContent key={r} value={r}>
          <Card><CardContent className="pt-7">{ld ? <Loader /> : <div className="overflow-x-auto rounded-xl border"><table className="w-full">
            <thead><tr className="bg-muted/50 border-b-2">{['Username', 'Name', 'Email', 'Dept', 'Role', 'Actions'].map((h) => <th key={h} className={`text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground ${h === 'Actions' ? 'text-right' : ''}`}>{h}</th>)}</tr></thead>
            <tbody>{list.map((u) => <tr key={u.id} className="border-b border-border/50 hover:bg-muted/30"><td className="py-3 px-4 font-bold">{u.username}</td><td className="py-3 px-4 text-sm">{u.first_name} {u.last_name}</td><td className="py-3 px-4 text-sm">{u.email}</td><td className="py-3 px-4 text-sm">{u.department}</td><td className="py-3 px-4"><Badge variant={u.role.toLowerCase()}>{u.role}</Badge></td><td className="py-3 px-4 text-right"><Button size="icon-sm" variant="ghost" className="text-destructive hover:bg-destructive/10" onClick={() => del(u.id, u.username)}><Trash2 className="h-4 w-4" /></Button></td></tr>)}</tbody>
          </table></div>}</CardContent></Card>
        </TabsContent>)}
      </Tabs>

      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent><DialogHeader><DialogTitle>Create New User</DialogTitle></DialogHeader><DialogBody>
          <form onSubmit={submit} className="space-y-4">
            <div><Label>Role</Label><Select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} className="mt-1"><option value="FACULTY">Faculty</option><option value="ADMIN">Admin</option></Select></div>
            <div className="grid grid-cols-2 gap-3"><div><Label>Username *</Label><Input required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} className="mt-1" /></div><div><Label>Password *</Label><Input required type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} className="mt-1" /></div></div>
            <div className="grid grid-cols-2 gap-3"><div><Label>First Name</Label><Input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="mt-1" /></div><div><Label>Last Name</Label><Input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="mt-1" /></div></div>
            <div className="grid grid-cols-2 gap-3"><div><Label>Email</Label><Input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="mt-1" /></div><div><Label>Department</Label><Input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} className="mt-1" /></div></div>
            <Button variant="success" size="lg" className="w-full" type="submit">Create User</Button>
          </form>
        </DialogBody></DialogContent>
      </Dialog>
    </div>
  );
}