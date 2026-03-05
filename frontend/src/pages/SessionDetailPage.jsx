import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Download, Search, CheckCircle, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { sessionsAPI, exportsAPI } from '@/api/endpoints';
import SeatingGrid from '@/components/SeatingGrid';
import StatsCard from '@/components/StatsCard';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';
import useAuth from '@/hooks/useAuth';

export default function SessionDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [s, setS] = useState(null);
  const [ld, setLd] = useState(true);
  const [layouts, setLayouts] = useState({});
  const [selHall, setSelHall] = useState(null);
  const [searchId, setSearchId] = useState('');
  const [filterSubject, setFilterSubject] = useState('');
  const [filterClass, setFilterClass] = useState('');
  const [completing, setCompleting] = useState(false);
  const [searchResult, setSearchResult] = useState(null);

  const load = useCallback(() => {
    setLd(true);
    sessionsAPI.detail(id).then((r) => {
      setS(r.data);
      if (r.data.halls?.length && !selHall) setSelHall(r.data.halls[0]);
    }).catch(() => toast.error('Failed')).finally(() => setLd(false));
  }, [id]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (selHall && !layouts[selHall.id])
      sessionsAPI.hallLayout(id, selHall.id).then((r) => setLayouts((p) => ({ ...p, [selHall.id]: r.data }))).catch(() => {});
  }, [selHall, id]);

  useEffect(() => {
    if (s?.halls) s.halls.forEach((h) => {
      if (!layouts[h.id]) sessionsAPI.hallLayout(id, h.id).then((r) => setLayouts((p) => ({ ...p, [h.id]: r.data }))).catch(() => {});
    });
  }, [s]);

  const handleSearch = (val) => {
    setSearchId(val);
    setSearchResult(null);
    if (!val.trim() || !s) return;
    const q = val.trim().toLowerCase();
    const m = (s.allocations || []).find((a) => a.student_id.toLowerCase().includes(q));
    if (m) {
      const th = s.halls.find((h) => h.hall_id === m.hall_id);
      if (th) {
        setSelHall(th);
        setSearchResult({ hall_id: m.hall_id, student_id: m.student_id, row: m.row, col: m.column });
        setFilterSubject('');
        setFilterClass('');
      }
    }
  };

  const dl = (p, f) => {
    p.then((r) => {
      const a = document.createElement('a');
      a.href = window.URL.createObjectURL(new Blob([r.data]));
      a.download = f;
      a.click();
    }).catch(() => toast.error('Failed'));
  };

  const handleComplete = async () => {
    setCompleting(true);
    try { await sessionsAPI.complete(id); toast.success('Completed!'); load(); }
    catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
    finally { setCompleting(false); }
  };

  if (ld) return <Loader />;
  if (!s) return <div className="p-8 text-red-500">Not found.</div>;

  const allSubjects = [...new Set((s.allocations || []).map((a) => a.subject_code))].sort();
  const allClasses = [...new Set((s.allocations || []).map((a) => a.student_class).filter(Boolean))].sort();
  const unalloc = (s.violations || []).filter((v) => v.violation_type === 'UNALLOCATED');
  const dist = {};
  (s.allocations || []).forEach((a) => {
    if (!dist[a.hall_id]) dist[a.hall_id] = {};
    dist[a.hall_id][a.subject_code] = (dist[a.hall_id][a.subject_code] || 0) + 1;
  });

  const detailStats = [
    { icon: '👥', value: s.total_students,   label: 'Students',    color: 'violet' },
    { icon: '🏛',  value: s.total_halls,      label: 'Halls',       color: 'indigo' },
    { icon: '✅', value: s.allocated_count,   label: 'Allocated',   color: 'emerald' },
    { icon: '❌', value: s.unallocated_count, label: 'Unallocated', color: s.unallocated_count > 0 ? 'red' : 'emerald' },
    { icon: '💺', value: s.total_capacity,    label: 'Seats',       color: 'sky' },
    { icon: '⚡', value: s.allocation_time_ms ? `${s.allocation_time_ms}ms` : '—', label: 'Time', color: 'cyan' },
  ];

  return (
    <div className="p-5 sm:p-8">
      <PageHeader
        title={s.name}
        subtitle={`📅 ${s.exam_date_str}  ·  🕐 ${s.exam_time_str}${s.student_csv_name && s.student_csv_name !== '—' ? `  ·  👥 ${s.student_csv_name}` : ''}${s.hall_csv_name && s.hall_csv_name !== '—' ? `  ·  🏛 ${s.hall_csv_name}` : ''}`}
      >
        <Badge variant={s.status.toLowerCase()} className="text-sm px-4 py-1.5">{s.status}</Badge>
        {user?.role === 'ADMIN' && s.status === 'ALLOCATED' && (
          <Button variant="success" onClick={handleComplete} disabled={completing}>
            {completing ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />} Mark Completed
          </Button>
        )}
        <Button variant="outline" onClick={() => dl(exportsAPI.csv(id), `alloc_${id}.csv`)}><Download className="h-4 w-4" /> CSV</Button>
        <Button variant="outline" onClick={() => dl(exportsAPI.pdf(id), `seat_${id}.pdf`)}><Download className="h-4 w-4" /> PDF</Button>
      </PageHeader>

      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3 mb-6">
        {detailStats.map((st, i) => (
          <div key={i} className="animate-fade-in" style={{ animationDelay: `${i * 60}ms` }}>
            <StatsCard {...st} />
          </div>
        ))}
      </div>

      {s.warnings?.map((w, i) => (
        <div key={i} className="bg-amber-50 border-l-4 border-amber-500 p-3 rounded-lg text-amber-700 text-sm mb-2">⚠️ {w}</div>
      ))}
      {s.unallocated_count > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-lg text-red-700 text-sm mb-4">
          ❌ {s.unallocated_count} student(s) could not be seated
        </div>
      )}

      <Tabs defaultValue="layout">
        <TabsList>
          <TabsTrigger value="layout">🏛️ Layout</TabsTrigger>
          <TabsTrigger value="list">📋 List ({s.allocated_count})</TabsTrigger>
          <TabsTrigger value="dist">📊 Distribution</TabsTrigger>
          <TabsTrigger value="unalloc">
            ❌ Unallocated
            {unalloc.length > 0 && <Badge variant="destructive" className="ml-1.5 text-[10px] px-1.5">{unalloc.length}</Badge>}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="layout">
          <Card>
            <CardHeader className="flex-row items-center justify-between flex-wrap gap-3">
              <CardTitle>Seating Layout</CardTitle>
              <div className="flex gap-2 items-center flex-wrap">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search roll no..." value={searchId} onChange={(e) => handleSearch(e.target.value)} className="pl-9 w-56" />
                </div>
                <Select value={selHall?.id || ''} onChange={(e) => { setSelHall(s.halls.find((h) => h.id === +e.target.value)); setSearchResult(null); }} className="w-64">
                  {s.halls?.map((h) => (
                    <option key={h.id} value={h.id}>{h.hall_id} ({h.rows}×{h.columns}, Cap:{h.capacity})</option>
                  ))}
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {searchResult && (
                <div className="bg-sky-50 border-l-4 border-sky-500 p-3 rounded-lg text-sky-700 text-sm mb-3">
                  🔍 Found <strong>{searchResult.student_id}</strong> in <strong>{searchResult.hall_id}</strong> — Row {searchResult.row + 1}, Col {searchResult.col + 1}
                </div>
              )}
              {searchId && !searchResult && searchId.length >= 3 && (
                <div className="bg-amber-50 border-l-4 border-amber-500 p-3 rounded-lg text-amber-700 text-sm mb-3">
                  No match for "{searchId}"
                </div>
              )}

              <div className="flex flex-wrap gap-1.5 mb-3">
                <button
                  onClick={() => { setFilterSubject(''); setSearchId(''); setSearchResult(null); }}
                  className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', !filterSubject ? 'bg-primary text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80')}
                >
                  All Subjects
                </button>
                {allSubjects.map((sub) => (
                  <button
                    key={sub}
                    onClick={() => { setFilterSubject(sub); setFilterClass(''); setSearchId(''); setSearchResult(null); }}
                    className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', filterSubject === sub ? 'bg-primary text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80')}
                  >
                    {sub}
                  </button>
                ))}
              </div>
              {allClasses.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-4">
                  <button
                    onClick={() => { setFilterClass(''); setSearchId(''); setSearchResult(null); }}
                    className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', !filterClass ? 'bg-primary text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80')}
                  >
                    All Classes
                  </button>
                  {allClasses.map((c) => (
                    <button
                      key={c}
                      onClick={() => { setFilterClass(c); setFilterSubject(''); setSearchId(''); setSearchResult(null); }}
                      className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', filterClass === c ? 'bg-primary text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80')}
                    >
                      {c}
                    </button>
                  ))}
                </div>
              )}

              <SeatingGrid layout={selHall ? layouts[selHall.id] : null} searchId={searchId} filterSubject={filterSubject} filterClass={filterClass} highlightSeat={searchResult} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="list">
          <Card>
            <CardHeader><CardTitle>Full List ({s.allocations?.length})</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto rounded-xl border">
                <table className="w-full">
                  <thead>
                    <tr className="bg-muted/50 border-b-2">
                      {['ID', 'Name', 'Subject', 'Class', 'Hall', 'Row', 'Col'].map((h) => (
                        <th key={h} className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {(s.allocations || []).map((a, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-muted/30">
                        <td className="py-3 px-4 font-bold text-sm">{a.student_id}</td>
                        <td className="py-3 px-4 text-sm">{a.student_name}</td>
                        <td className="py-3 px-4"><Badge variant="outline">{a.subject_code}</Badge></td>
                        <td className="py-3 px-4 text-sm">{a.student_class}</td>
                        <td className="py-3 px-4 text-sm">{a.hall_id}</td>
                        <td className="py-3 px-4">{a.row + 1}</td>
                        <td className="py-3 px-4">{a.column + 1}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dist">
          <Card>
            <CardHeader><CardTitle>Subject Distribution</CardTitle></CardHeader>
            <CardContent>
              {Object.entries(dist).map(([hall, subs]) => (
                <div key={hall} className="mb-6">
                  <h4 className="font-bold text-lg mb-2">{hall}</h4>
                  <div className="rounded-xl border overflow-hidden">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-muted/50 border-b">
                          <th className="text-left py-2.5 px-4 text-xs font-bold uppercase text-muted-foreground">Subject</th>
                          <th className="text-left py-2.5 px-4 text-xs font-bold uppercase text-muted-foreground">Count</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(subs).map(([sub, c]) => (
                          <tr key={sub} className="border-b border-border/50">
                            <td className="py-2.5 px-4"><Badge variant="outline">{sub}</Badge></td>
                            <td className="py-2.5 px-4 font-bold">{c}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="unalloc">
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>Unallocated ({unalloc.length})</CardTitle>
              {unalloc.length > 0 && <Badge variant="destructive">⚠️ Action Needed</Badge>}
            </CardHeader>
            <CardContent>
              {unalloc.length > 0 ? (
                <div className="rounded-xl border overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-muted/50 border-b">
                        <th className="text-left py-3 px-4 text-xs font-bold uppercase text-muted-foreground">Student ID</th>
                        <th className="text-left py-3 px-4 text-xs font-bold uppercase text-muted-foreground">Reason</th>
                      </tr>
                    </thead>
                    <tbody>
                      {unalloc.map((v, i) => (
                        <tr key={i} className="border-b border-border/50 bg-red-50/50">
                          <td className="py-3 px-4 font-bold">{v.student_id_ref}</td>
                          <td className="py-3 px-4 text-sm">{v.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="bg-emerald-50 border-l-4 border-emerald-500 p-4 rounded-lg text-emerald-700">
                  ✅ All students successfully seated!
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}