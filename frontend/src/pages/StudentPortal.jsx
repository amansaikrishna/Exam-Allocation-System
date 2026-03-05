import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogBody } from '@/components/ui/dialog';
import { studentAPI } from '@/api/endpoints';
import StatsCard from '@/components/StatsCard';
import SeatingGrid from '@/components/SeatingGrid';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';

export default function StudentPortal() {
  const [data, setData] = useState(null);
  const [ld, setLd] = useState(true);
  const [viewAlloc, setViewAlloc] = useState(null);
  const [layout, setLayout] = useState(null);
  const [layoutLd, setLayoutLd] = useState(false);

  useEffect(() => {
    studentAPI.myAllocs().then((r) => setData(r.data)).catch(() => toast.error('Failed')).finally(() => setLd(false));
  }, []);

  const openLayout = async (a) => {
    setViewAlloc(a); setLayoutLd(true); setLayout(null);
    try { const r = await studentAPI.hallLayout(a.session_id, a.hall_pk); setLayout(r.data); }
    catch { toast.error('Error'); }
    finally { setLayoutLd(false); }
  };

  if (ld) return <Loader />;

  const portalStats = [
    { icon: '🆔', value: data?.student_id,         label: 'ID',      color: 'indigo' },
    { icon: '👤', value: data?.name || '—',         label: 'Name',    color: 'violet' },
    { icon: '📚', value: data?.subject_code || '—', label: 'Subject', color: 'cyan'   },
    { icon: '🏫', value: data?.student_class || '—',label: 'Class',   color: 'amber'  },
    { icon: '📋', value: data?.allocations?.length || 0, label: 'Exams', color: 'emerald' },
  ];

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="My Allocations" subtitle="View your exam seat assignments" />
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-3 mb-6">
          {portalStats.map((s, i) => (
            <div key={i} className="animate-fade-in" style={{ animationDelay: `${i * 80}ms` }}>
              <StatsCard {...s} />
            </div>
          ))}
        </div>
      )}

      <Card className="animate-fade-in" style={{ animationDelay: '300ms' }}>
        <CardHeader><CardTitle>Seat Assignments</CardTitle></CardHeader>
        <CardContent>
          {data?.allocations?.length ? (
            <div className="overflow-x-auto rounded-xl border">
              <table className="w-full">
                <thead>
                  <tr className="bg-muted/50 border-b-2">
                    {['Exam', 'Date', 'Time', 'Status', 'Hall', 'Row', 'Col', 'Map'].map((h) => (
                      <th key={h} className={`text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground ${h === 'Map' ? 'text-right' : ''}`}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.allocations.map((a, i) => (
                    <tr key={i} className="border-b border-border/50 hover:bg-muted/30">
                      <td className="py-3 px-4 font-bold">{a.session_name}</td>
                      <td className="py-3 px-4 text-sm">{a.exam_date || '—'}</td>
                      <td className="py-3 px-4 text-sm">{a.exam_time || '—'}</td>
                      <td className="py-3 px-4"><Badge variant={a.session_status?.toLowerCase()}>{a.session_status}</Badge></td>
                      <td className="py-3 px-4 font-semibold">{a.hall_id}</td>
                      <td className="py-3 px-4"><span className="text-lg font-extrabold text-primary">{a.row}</span></td>
                      <td className="py-3 px-4"><span className="text-lg font-extrabold text-primary">{a.column}</span></td>
                      <td className="py-3 px-4 text-right"><Button size="sm" onClick={() => openLayout(a)}>🏛️ View</Button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="bg-sky-50 border-l-4 border-sky-500 p-4 rounded-lg text-sky-700">No allocations yet.</div>
          )}
        </CardContent>
      </Card>

      <Dialog open={!!viewAlloc} onOpenChange={(v) => { if (!v) { setViewAlloc(null); setLayout(null); } }}>
        <DialogContent className="max-w-3xl">
          <DialogHeader><DialogTitle>{viewAlloc?.session_name} — Hall {viewAlloc?.hall_id}</DialogTitle></DialogHeader>
          <DialogBody>
            {layoutLd ? <Loader /> : layout ? (
              <div>
                <div className="bg-sky-50 border-l-4 border-sky-500 p-3 rounded-lg text-sky-700 text-sm mb-4">
                  <strong>Your Seat:</strong> Row {viewAlloc?.row}, Column {viewAlloc?.column} — highlighted below
                </div>
                {(viewAlloc?.exam_date || viewAlloc?.exam_time) && (
                  <p className="text-sm text-muted-foreground mb-3">📅 {viewAlloc.exam_date} · 🕐 {viewAlloc.exam_time}</p>
                )}
                <SeatingGrid layout={layout} highlightStudentId={data?.student_id} />
              </div>
            ) : <p className="text-muted-foreground">No layout available.</p>}
          </DialogBody>
        </DialogContent>
      </Dialog>
    </div>
  );
}