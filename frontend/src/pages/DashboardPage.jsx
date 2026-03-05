import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckCircle, Users, Home, Award, Database } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { dashboardAPI } from '@/api/endpoints';
import StatsCard from '@/components/StatsCard';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';
import useAuth from '@/hooks/useAuth';

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const nav = useNavigate();
  const { user } = useAuth();

  useEffect(() => {
    dashboardAPI.get().then((r) => setData(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;
  if (!data)
    return (
      <div className="p-8">
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg text-red-700">
          Failed to load dashboard.
        </div>
      </div>
    );

  if (user?.role === 'FACULTY')
    return (
      <div className="p-5 sm:p-8">
        <PageHeader title="My Invigilation" subtitle="View your assigned exam invigilation duties" />
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
          <StatsCard icon={<FileText className="h-5 w-5" />} value={data.total_assigned} label="Assigned" color="indigo" onClick={() => nav('/allocations')} />
          <StatsCard icon={<CheckCircle className="h-5 w-5" />} value={data.allocated} label="Active" color="emerald" onClick={() => nav('/allocations')} />
          <StatsCard icon={<Award className="h-5 w-5" />} value={data.completed} label="Completed" color="violet" onClick={() => nav('/allocations')} />
        </div>
        {data.duties?.length > 0 ? (
          <Card>
            <CardHeader><CardTitle>My Duties</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-border">
                      {['Session', 'Status', 'Hall', 'Date', 'Time', ''].map((h) => (
                        <th key={h} className="text-left py-3 px-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.duties.map((dt, i) => (
                      <tr key={i} className="border-b border-border/50 hover:bg-muted/50 cursor-pointer transition-colors" onClick={() => nav(`/allocations/${dt.session_id}`)}>
                        <td className="py-3 px-4 font-semibold">{dt.session_name}</td>
                        <td className="py-3 px-4"><Badge variant={dt.session_status?.toLowerCase()}>{dt.session_status}</Badge></td>
                        <td className="py-3 px-4">{dt.hall_id} ({dt.hall_capacity})</td>
                        <td className="py-3 px-4 text-sm">{dt.exam_date || '—'}</td>
                        <td className="py-3 px-4 text-sm">{dt.exam_time || '—'}</td>
                        <td className="py-3 px-4"><Button size="sm">View</Button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="bg-sky-50 border-l-4 border-sky-500 p-4 rounded-lg text-sky-700">
            No duties assigned yet.
          </div>
        )}
      </div>
    );

  const stats = [
    { icon: <FileText className="h-5 w-5" />, value: data.total_sessions, label: 'Allocations', to: '/allocations', color: 'indigo' },
    { icon: <CheckCircle className="h-5 w-5" />, value: data.allocated, label: 'Active', to: '/allocations', color: 'emerald' },
    { icon: <Award className="h-5 w-5" />, value: data.completed, label: 'Completed', to: '/allocations', color: 'violet' },
    { icon: <Users className="h-5 w-5" />, value: data.total_students, label: 'Students', to: '/students', color: 'pink' },
    { icon: <Database className="h-5 w-5" />, value: data.total_csvs, label: 'CSVs', to: '/new', color: 'cyan' },
    { icon: <Home className="h-5 w-5" />, value: data.faculty_count, label: 'Faculty', to: '/users', color: 'amber' },
  ];

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="Dashboard" subtitle="Overview of examination hall allocations" />
      <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4">
        {stats.map((s, i) => (
          <div key={i} className="animate-fade-in" style={{ animationDelay: `${i * 80}ms` }}>
            <StatsCard {...s} onClick={() => nav(s.to)} />
          </div>
        ))}
      </div>
    </div>
  );
}