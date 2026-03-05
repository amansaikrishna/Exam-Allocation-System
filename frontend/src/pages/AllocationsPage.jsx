import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Trash2, ArrowUpDown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { sessionsAPI } from '@/api/endpoints';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';
import useAuth from '@/hooks/useAuth';

export default function AllocationsPage() {
  const [list, setList] = useState([]);
  const [ld, setLd] = useState(true);
  const nav = useNavigate();
  const { user } = useAuth();
  const [sortCol, setSortCol] = useState('created_at');
  const [sortDir, setSortDir] = useState('desc');
  const [filterStatus, setFilterStatus] = useState('');
  const [searchName, setSearchName] = useState('');

  const load = () => {
    setLd(true);
    sessionsAPI.list().then((r) => setList(r.data)).catch(() => toast.error('Failed')).finally(() => setLd(false));
  };
  useEffect(() => { load(); }, []);

  const handleDelete = (e, id, name) => {
    e.stopPropagation();
    if (!confirm(`Delete "${name}"?`)) return;
    sessionsAPI.delete(id).then(() => { toast.success('Deleted'); load(); }).catch(() => toast.error('Failed'));
  };

  const handleSort = (col) => {
    if (sortCol === col) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else { setSortCol(col); setSortDir('asc'); }
  };

  const allStatuses = useMemo(() => [...new Set(list.map((s) => s.status))].sort(), [list]);

  const processed = useMemo(() => {
    let d = [...list];
    if (filterStatus) d = d.filter((s) => s.status === filterStatus);
    if (searchName) d = d.filter((s) => s.name.toLowerCase().includes(searchName.toLowerCase()));
    const num = ['allocated_count', 'total_halls', 'total_capacity', 'allocation_time_ms'];
    d.sort((a, b) => {
      if (num.includes(sortCol)) return sortDir === 'asc' ? (a[sortCol] || 0) - (b[sortCol] || 0) : (b[sortCol] || 0) - (a[sortCol] || 0);
      const cmp = String(a[sortCol] || '').localeCompare(String(b[sortCol] || ''));
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return d;
  }, [list, filterStatus, searchName, sortCol, sortDir]);

  if (ld) return <Loader />;

  const SortTh = ({ col, children }) => (
    <th
      className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground cursor-pointer hover:text-foreground transition-colors select-none"
      onClick={() => handleSort(col)}
    >
      <span className="inline-flex items-center gap-1">
        {children}
        {sortCol === col && <ArrowUpDown className="h-3 w-3" />}
      </span>
    </th>
  );

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="Allocations" subtitle={`${list.length} total exam sessions`} />

      {!list.length ? (
        <div className="bg-sky-50 border-l-4 border-sky-500 p-4 rounded-lg text-sky-700">No allocations yet.</div>
      ) : (
        <Card className="animate-fade-in">
          <CardContent className="pt-7">
            <div className="flex flex-wrap gap-3 mb-5">
              <Input placeholder="Search session name..." value={searchName} onChange={(e) => setSearchName(e.target.value)} className="flex-1 min-w-[200px]" />
              <Select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="w-44">
                <option value="">All Statuses</option>
                {allStatuses.map((s) => <option key={s} value={s}>{s}</option>)}
              </Select>
              {(filterStatus || searchName) && (
                <Button variant="outline" size="sm" onClick={() => { setFilterStatus(''); setSearchName(''); }}>Clear</Button>
              )}
              <span className="ml-auto text-sm text-muted-foreground self-center font-semibold">
                {processed.length} of {list.length}
              </span>
            </div>
            <div className="overflow-x-auto rounded-xl border">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted/50 border-b-2 border-border">
                    <SortTh col="name">Name</SortTh>
                    <SortTh col="exam_date">Date</SortTh>
                    <SortTh col="status">Status</SortTh>
                    <SortTh col="allocated_count">Seated</SortTh>
                    <SortTh col="total_halls">Halls</SortTh>
                    <SortTh col="total_capacity">Capacity</SortTh>
                    <SortTh col="allocation_time_ms">Time</SortTh>
                    <th className="py-3 px-4 text-right text-xs font-bold uppercase tracking-wider text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {processed.map((s, i) => (
                    <tr
                      key={s.id}
                      className="border-b border-border/50 hover:bg-primary/[0.02] cursor-pointer transition-colors animate-slide-in"
                      style={{ animationDelay: `${i * 30}ms` }}
                      onClick={() => nav(`/allocations/${s.id}`)}
                    >
                      <td className="py-3.5 px-4 font-bold">{s.name}</td>
                      <td className="py-3.5 px-4 text-sm">{s.exam_date_str || '—'}</td>
                      <td className="py-3.5 px-4"><Badge variant={s.status.toLowerCase()}>{s.status}</Badge></td>
                      <td className="py-3.5 px-4">
                        <span className="font-bold">{s.allocated_count}/{s.total_students}</span>
                        {s.unallocated_count > 0 && (
                          <Badge variant="destructive" className="ml-2 text-[10px]">⚠ {s.unallocated_count}</Badge>
                        )}
                      </td>
                      <td className="py-3.5 px-4">{s.total_halls}</td>
                      <td className="py-3.5 px-4">{s.total_capacity}</td>
                      <td className="py-3.5 px-4 text-sm font-medium">{s.allocation_time_ms ? `${s.allocation_time_ms}ms` : '—'}</td>
                      <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex gap-1.5 justify-end">
                          <Button size="sm" onClick={() => nav(`/allocations/${s.id}`)}>View</Button>
                          {user?.role === 'ADMIN' && (
                            <Button size="icon-sm" variant="ghost" className="text-destructive hover:bg-destructive/10" onClick={(e) => handleDelete(e, s.id, s.name)}>
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}