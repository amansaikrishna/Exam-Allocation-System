import React, { useState, useEffect, useMemo, Fragment } from 'react';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { Search, ChevronDown, ChevronRight, ArrowUpDown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogBody } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { studentsAPI, csvAPI } from '@/api/endpoints';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';

export default function StudentsPage() {
  const nav = useNavigate();
  const [list, setList] = useState([]); const [total, setTotal] = useState(0); const [page, setPage] = useState(1);
  const [search, setSearch] = useState(''); const [csvFilter, setCsvFilter] = useState(''); const [csvList, setCsvList] = useState([]); const [ld, setLd] = useState(true);
  const [showSearch, setShowSearch] = useState(false); const [sq, setSq] = useState(''); const [sr, setSr] = useState(null);
  const [expanded, setExpanded] = useState(new Set());
  const [sortCol, setSortCol] = useState('student_id'); const [sortDir, setSortDir] = useState('asc');
  const [filterSubject, setFilterSubject] = useState(''); const [filterClass, setFilterClass] = useState('');

  useEffect(() => { csvAPI.list().then((r) => setCsvList(r.data.filter((c) => c.csv_type !== 'HALLS'))).catch(() => {}); }, []);
  const load = (p = page, s = search, c = csvFilter) => { setLd(true); studentsAPI.list({ page: p, per_page: 50, search: s || undefined, csv_id: c || undefined }).then((r) => { setList(r.data.results); setTotal(r.data.total); }).catch(() => toast.error('Failed')).finally(() => setLd(false)); };
  useEffect(() => { load(); }, [page, csvFilter]);
  const doSearch = (e) => { e.preventDefault(); setPage(1); load(1, search, csvFilter); };
  const doAllocSearch = async () => { if (!sq.trim()) return; try { const r = await studentsAPI.search(sq.trim()); setSr(r.data); } catch (err) { toast.error(err.response?.data?.error || 'Not found'); setSr(null); } };
  const toggleExpand = (sid) => { setExpanded((p) => { const n = new Set(p); n.has(sid) ? n.delete(sid) : n.add(sid); return n; }); };
  const handleSort = (col) => { if (sortCol === col) setSortDir((d) => d === 'asc' ? 'desc' : 'asc'); else { setSortCol(col); setSortDir('asc'); } };

  const allSubjects = useMemo(() => [...new Set(list.map((s) => s.subject_code))].sort(), [list]);
  const allClasses = useMemo(() => [...new Set(list.map((s) => s.student_class).filter(Boolean))].sort(), [list]);

  const processed = useMemo(() => {
    let d = [...list];
    if (filterSubject) d = d.filter((s) => s.subject_code === filterSubject);
    if (filterClass) d = d.filter((s) => s.student_class === filterClass);
    d.sort((a, b) => { if (sortCol === 'alloc_count') return sortDir === 'asc' ? (a.allocations?.length || 0) - (b.allocations?.length || 0) : (b.allocations?.length || 0) - (a.allocations?.length || 0); const cmp = String(a[sortCol] || '').localeCompare(String(b[sortCol] || '')); return sortDir === 'asc' ? cmp : -cmp; });
    return d;
  }, [list, filterSubject, filterClass, sortCol, sortDir]);

  const SortTh = ({ col, children }) => <th className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground cursor-pointer hover:text-foreground transition-colors select-none" onClick={() => handleSort(col)}><span className="inline-flex items-center gap-1">{children}{sortCol === col && <ArrowUpDown className="h-3 w-3" />}</span></th>;

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="Students" subtitle={`${total} students across all sources`}>
        <Button onClick={() => setShowSearch(true)}><Search className="h-4 w-4" />Search Allocations</Button>
      </PageHeader>
      <Card className="animate-fade-in"><CardContent className="pt-7">
        <div className="flex flex-wrap gap-3 mb-4">
          <form onSubmit={doSearch} className="flex gap-2 flex-1 min-w-[220px]"><Input placeholder="Search ID or name..." value={search} onChange={(e) => setSearch(e.target.value)} /><Button type="submit" size="sm">Search</Button></form>
          <Select value={csvFilter} onChange={(e) => { setCsvFilter(e.target.value); setPage(1); }} className="w-52"><option value="">All Sources</option>{csvList.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.student_count})</option>)}</Select>
        </div>
        <div className="flex flex-wrap gap-3 mb-4 items-center">
          <Select value={filterSubject} onChange={(e) => setFilterSubject(e.target.value)} className="w-36"><option value="">All Subjects</option>{allSubjects.map((s) => <option key={s} value={s}>{s}</option>)}</Select>
          <Select value={filterClass} onChange={(e) => setFilterClass(e.target.value)} className="w-36"><option value="">All Classes</option>{allClasses.map((c) => <option key={c} value={c}>{c}</option>)}</Select>
          {(filterSubject || filterClass) && <Button variant="outline" size="sm" onClick={() => { setFilterSubject(''); setFilterClass(''); }}>Clear</Button>}
          <span className="ml-auto text-sm text-muted-foreground font-semibold">{processed.length} shown</span>
        </div>
        {ld ? <Loader /> : (<>
          <div className="overflow-x-auto rounded-xl border"><table className="w-full">
            <thead><tr className="bg-muted/50 border-b-2"><th className="w-10 py-3 px-3" /><SortTh col="student_id">ID</SortTh><SortTh col="name">Name</SortTh><SortTh col="subject_code">Subject</SortTh><SortTh col="student_class">Class</SortTh><SortTh col="csv_name">Source</SortTh><SortTh col="alloc_count">Allocations</SortTh></tr></thead>
            <tbody>{processed.map((s) => { const hasA = s.allocations?.length > 0; const isE = expanded.has(s.student_id); return (
              <Fragment key={s.id}>
                <tr className={cn('border-b border-border/50 hover:bg-muted/30 transition-colors', hasA && 'cursor-pointer')} onClick={() => hasA && toggleExpand(s.student_id)}>
                  <td className="py-3 px-3 text-center">{hasA && (isE ? <ChevronDown className="h-4 w-4 inline" /> : <ChevronRight className="h-4 w-4 inline" />)}</td>
                  <td className="py-3 px-4 font-bold">{s.student_id}</td><td className="py-3 px-4 text-sm">{s.name}</td>
                  <td className="py-3 px-4"><Badge variant="outline">{s.subject_code}</Badge></td><td className="py-3 px-4 text-sm">{s.student_class}</td>
                  <td className="py-3 px-4"><Badge variant="outline" className="bg-muted">{s.csv_name}</Badge></td>
                  <td className="py-3 px-4">{hasA ? <Badge variant="info">{s.allocations.length} exam{s.allocations.length > 1 ? 's' : ''}</Badge> : <span className="text-muted-foreground">—</span>}</td>
                </tr>
                {isE && s.allocations?.map((a, i) => <tr key={`${s.student_id}-${i}`} className="bg-primary/[0.02] border-b border-border/30 hover:bg-primary/[0.04] cursor-pointer" onClick={(e) => { e.stopPropagation(); nav(`/allocations/${a.session_id}`); }}>
                  <td /><td colSpan={2} className="py-2 px-4 text-sm pl-10">↳ {a.session_name}</td><td className="py-2 px-4"><Badge variant={a.status?.toLowerCase()}>{a.status}</Badge></td>
                  <td className="py-2 px-4 text-sm"><strong>{a.hall_id}</strong> — R{a.row}, C{a.column}</td><td className="py-2 px-4 text-xs">{a.exam_date || '—'}</td><td className="py-2 px-4 text-xs">{a.exam_time || '—'}</td>
                </tr>)}
              </Fragment>
            ); })}</tbody>
          </table></div>
          <div className="flex justify-center items-center gap-4 mt-4">
            <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>← Prev</Button>
            <span className="text-sm text-muted-foreground font-semibold">Page {page}/{Math.ceil(total / 50) || 1}</span>
            <Button variant="outline" size="sm" disabled={list.length < 50} onClick={() => setPage(page + 1)}>Next →</Button>
          </div>
        </>)}
      </CardContent></Card>

      <Dialog open={showSearch} onOpenChange={(v) => { if (!v) { setShowSearch(false); setSr(null); setSq(''); } }}>
        <DialogContent className="max-w-2xl"><DialogHeader><DialogTitle>Search Student Allocations</DialogTitle></DialogHeader><DialogBody>
          <div className="flex gap-2 mb-4"><Input placeholder="Enter roll number..." value={sq} onChange={(e) => setSq(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && doAllocSearch()} /><Button onClick={doAllocSearch}>Search</Button></div>
          {sr?.exact_match && (<div><div className="p-4 bg-muted rounded-xl mb-3"><p className="font-bold">{sr.student.student_id} — {sr.student.name}</p><p className="text-xs text-muted-foreground">{sr.student.subject_code} · {sr.student.student_class} · {sr.student.csv_name}</p></div>
            {sr.allocations?.length ? <div className="rounded-xl border overflow-hidden"><table className="w-full"><thead><tr className="bg-muted/50 border-b">{['Session', 'Status', 'Hall', 'Row', 'Col', 'Date', 'Time'].map((h) => <th key={h} className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">{h}</th>)}</tr></thead>
              <tbody>{sr.allocations.map((a, i) => <tr key={i} className="border-b border-border/50 hover:bg-muted/30 cursor-pointer" onClick={() => { setShowSearch(false); nav(`/allocations/${a.session_id}`); }}><td className="py-2 px-3 text-sm">{a.session_name}</td><td className="py-2 px-3"><Badge variant={a.status?.toLowerCase()}>{a.status}</Badge></td><td className="py-2 px-3 text-sm">{a.hall_id}</td><td className="py-2 px-3">{a.row}</td><td className="py-2 px-3">{a.column}</td><td className="py-2 px-3 text-xs">{a.exam_date || '—'}</td><td className="py-2 px-3 text-xs">{a.exam_time || '—'}</td></tr>)}</tbody></table></div>
              : <p className="text-muted-foreground">No allocations.</p>}</div>)}
          {sr && !sr.exact_match && (<div><p className="mb-2 font-semibold">Suggestions:</p><div className="rounded-xl border overflow-hidden"><table className="w-full"><thead><tr className="bg-muted/50 border-b"><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">ID</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">Name</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">Subject</th></tr></thead>
            <tbody>{sr.suggestions?.map((s) => <tr key={s.id} className="border-b hover:bg-muted/30 cursor-pointer" onClick={() => setSq(s.student_id)}><td className="py-2 px-3 text-sm">{s.student_id}</td><td className="py-2 px-3 text-sm">{s.name}</td><td className="py-2 px-3 text-sm">{s.subject_code}</td></tr>)}</tbody></table></div></div>)}
        </DialogBody></DialogContent>
      </Dialog>
    </div>
  );
}