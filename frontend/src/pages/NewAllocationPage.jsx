import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-toastify';
import { CloudUpload, FileText, Play, ArrowRight, Trash2, Users, Home, Loader2, FileSpreadsheet } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';
import { csvAPI, sessionsAPI, usersAPI } from '@/api/endpoints';
import PageHeader from '@/components/PageHeader';
import Loader from '@/components/Loader';

function UploadBox({ label, desc, onUpload, loading, result, error }) {
  const [file, setFile] = useState(null);
  const [name, setName] = useState('');
  const onDrop = useCallback((a) => { if (a.length) { setFile(a[0]); if (!name) setName(a[0].name.replace('.csv', '')); } }, [name]);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { 'text/csv': ['.csv'] }, multiple: false });
  return (
    <div className="mt-4 p-5 bg-muted/50 rounded-2xl border-2 border-dashed border-border">
      <p className="font-bold text-sm mb-2">{label}</p>
      <div className="mb-3"><Label>Name</Label><Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Optional label" className="mt-1" /></div>
      <div {...getRootProps()} className={cn('p-6 rounded-xl border-2 border-dashed text-center cursor-pointer transition-all', file ? 'border-emerald-500 bg-emerald-50/50' : isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50')}>
        <input {...getInputProps()} />
        {file ? <div className="flex flex-col items-center gap-1"><FileText className="h-8 w-8 text-emerald-500" /><p className="font-semibold text-sm">{file.name}</p></div>
          : <div className="flex flex-col items-center gap-1"><CloudUpload className="h-10 w-10 text-muted-foreground" /><p className="text-sm text-muted-foreground">{desc}</p><p className="text-xs text-muted-foreground/60">Drag & drop or click</p></div>}
      </div>
      <Button className="w-full mt-3" onClick={() => onUpload(file, name)} disabled={!file || loading}>{loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Upload & Validate'}</Button>
      {error?.parse_errors?.map((e, i) => <div key={i} className="mt-2 bg-red-50 border-l-4 border-red-500 p-2 rounded text-red-700 text-sm">{e}</div>)}
      {result && <div className="mt-2 bg-emerald-50 border-l-4 border-emerald-500 p-2 rounded text-emerald-700 text-sm">✅ {result.total_students ? `${result.total_students} students` : ''} {result.total_halls ? `${result.total_halls} halls` : ''} parsed</div>}
    </div>
  );
}

export default function NewAllocationPage() {
  const nav = useNavigate();
  const [step, setStep] = useState(0); const [mode, setMode] = useState('separate');
  const [studentCsvs, setStudentCsvs] = useState([]); const [hallCsvs, setHallCsvs] = useState([]); const [combinedCsvs, setCombinedCsvs] = useState([]); const [loadingList, setLoadingList] = useState(true);
  const [selStudentCsv, setSelStudentCsv] = useState(null); const [selHallCsv, setSelHallCsv] = useState(null); const [selCombinedCsv, setSelCombinedCsv] = useState(null);
  const [csvStudents, setCsvStudents] = useState([]); const [classes, setClasses] = useState([]); const [subjects, setSubjects] = useState([]); const [selClasses, setSelClasses] = useState([]); const [selSubjects, setSelSubjects] = useState([]); const [excluded, setExcluded] = useState(new Set()); const [hallsList, setHallsList] = useState([]); const [loadingData, setLoadingData] = useState(false);
  const [sessionName, setSessionName] = useState(''); const [examDate, setExamDate] = useState(''); const [timeFrom, setTimeFrom] = useState(''); const [timeTo, setTimeTo] = useState('');
  const [faculty, setFaculty] = useState([]); const [hallInvigs, setHallInvigs] = useState({}); const [creating, setCreating] = useState(false); const [sessionId, setSessionId] = useState(null); const [allocResult, setAllocResult] = useState(null);
  const [upStuLd, setUpStuLd] = useState(false); const [upStuRes, setUpStuRes] = useState(null); const [upStuErr, setUpStuErr] = useState(null);
  const [upHallLd, setUpHallLd] = useState(false); const [upHallRes, setUpHallRes] = useState(null); const [upHallErr, setUpHallErr] = useState(null);
  const [upCombLd, setUpCombLd] = useState(false); const [upCombRes, setUpCombRes] = useState(null); const [upCombErr, setUpCombErr] = useState(null);

  const loadCsvs = () => { setLoadingList(true); csvAPI.list().then((r) => { setStudentCsvs(r.data.filter((c) => c.csv_type === 'STUDENTS')); setHallCsvs(r.data.filter((c) => c.csv_type === 'HALLS')); setCombinedCsvs(r.data.filter((c) => c.csv_type === 'COMBINED')); }).finally(() => setLoadingList(false)); };
  useEffect(() => { loadCsvs(); usersAPI.faculty().then((r) => setFaculty(r.data)).catch(() => {}); }, []);

  const uploadStudents = async (f, n) => { if (!f) return; setUpStuLd(true); setUpStuErr(null); setUpStuRes(null); try { const r = await csvAPI.uploadStudents(f, n); setUpStuRes(r.data); toast.success('Uploaded!'); loadCsvs(); } catch (e) { setUpStuErr(e.response?.data); toast.error('Failed'); } finally { setUpStuLd(false); } };
  const uploadHalls = async (f, n) => { if (!f) return; setUpHallLd(true); setUpHallErr(null); setUpHallRes(null); try { const r = await csvAPI.uploadHalls(f, n); setUpHallRes(r.data); toast.success('Uploaded!'); loadCsvs(); } catch (e) { setUpHallErr(e.response?.data); toast.error('Failed'); } finally { setUpHallLd(false); } };
  const uploadCombined = async (f, n) => { if (!f) return; setUpCombLd(true); setUpCombErr(null); setUpCombRes(null); try { const r = await csvAPI.uploadCombined(f, n); setUpCombRes(r.data); toast.success('Uploaded!'); loadCsvs(); } catch (e) { setUpCombErr(e.response?.data); toast.error('Failed'); } finally { setUpCombLd(false); } };
  const deleteCsv = async (e, csv) => { e.stopPropagation(); if (!confirm(`Delete "${csv.name}"?`)) return; try { await csvAPI.delete(csv.id); toast.success('Deleted'); loadCsvs(); } catch { toast.error('Failed'); } };

  const goToStep2 = async () => { setLoadingData(true); setStep(1); try { const csvId = mode === 'combined' ? selCombinedCsv.id : selStudentCsv.id; const r = await csvAPI.students(csvId, {}); setCsvStudents(r.data.students); setClasses(r.data.classes); setSubjects(r.data.subjects); setSelClasses([]); setSelSubjects([]); setExcluded(new Set()); const h = mode === 'separate' ? await csvAPI.halls(selHallCsv.id) : await csvAPI.halls(selCombinedCsv.id); setHallsList(h.data.halls || []); setSessionName(mode === 'combined' ? selCombinedCsv.name : selStudentCsv.name); } catch { toast.error('Failed'); setStep(0); } finally { setLoadingData(false); } };

  const filteredStudents = csvStudents.filter((s) => { if (selClasses.length && !selClasses.includes(s.student_class)) return false; if (selSubjects.length && !selSubjects.includes(s.subject_code)) return false; return true; });
  const activeStudents = filteredStudents.filter((s) => !excluded.has(s.student_id));
  const toggleExclude = (sid) => setExcluded((p) => { const n = new Set(p); n.has(sid) ? n.delete(sid) : n.add(sid); return n; });
  const toggleChip = (a, sa, v) => sa((p) => p.includes(v) ? p.filter((x) => x !== v) : [...p, v]);

  const handleCreate = async () => { if (!activeStudents.length) { toast.error('No students'); return; } if (!examDate || !timeFrom || !timeTo) { toast.error('Date & time required'); return; } setCreating(true); try { const body = { mode, name: sessionName, exam_date: examDate, exam_time_from: timeFrom, exam_time_to: timeTo, selected_classes: selClasses.length ? selClasses : undefined, selected_subjects: selSubjects.length ? selSubjects : undefined, excluded_student_ids: [...excluded], hall_invigilators: hallInvigs }; if (mode === 'separate') { body.student_csv_id = selStudentCsv.id; body.hall_csv_id = selHallCsv.id; } else { body.csv_id = selCombinedCsv.id; } const r = await sessionsAPI.create(body); setSessionId(r.data.session_id); setAllocResult(r.data); setStep(3); toast.success(`Allocated ${r.data.allocated} in ${r.data.time_ms}ms!`); } catch (err) { const d = err.response?.data; if (d?.conflicts) d.conflicts.forEach((c) => toast.error(c, { autoClose: 8000 })); else toast.error(d?.error || 'Failed'); } finally { setCreating(false); } };

  const CsvCard = ({ csv, onClick, selected }) => (
    <div onClick={() => onClick(csv)} className={cn('border rounded-2xl p-4 cursor-pointer transition-all hover:border-primary/50 hover:-translate-y-0.5', selected ? 'border-primary bg-primary/5 shadow-md shadow-primary/10' : 'bg-card')}>
      <div className="flex items-center gap-2 mb-1"><FileSpreadsheet className="h-4 w-4 text-primary" /><span className="font-bold text-sm flex-1 truncate">{csv.name}</span><button onClick={(e) => deleteCsv(e, csv)} className="text-muted-foreground hover:text-destructive transition-colors"><Trash2 className="h-3.5 w-3.5" /></button></div>
      <p className="text-xs text-muted-foreground">{csv.filename} · {csv.student_count > 0 ? `${csv.student_count} students` : ''} {csv.hall_count > 0 ? `${csv.hall_count} halls` : ''}</p>
      {csv.subjects?.length > 0 && <div className="flex flex-wrap gap-1 mt-2">{csv.subjects.map((s) => <Badge key={s} variant="outline" className="text-[10px]">{s}</Badge>)}</div>}
    </div>
  );

  const canProceed = mode === 'separate' ? selStudentCsv && selHallCsv : !!selCombinedCsv;
  const steps = ['Select Data', 'Students', 'Schedule', 'Complete'];

  return (
    <div className="p-5 sm:p-8">
      <PageHeader title="New Allocation" subtitle="Create a new exam hall allocation" />
      {/* Stepper */}
      <div className="flex items-center gap-2 mb-8">
        {steps.map((label, i) => (
          <React.Fragment key={i}>
            {i > 0 && <div className={cn('h-0.5 flex-1', step >= i ? 'bg-primary' : 'bg-border')} />}
            <div className="flex items-center gap-2 shrink-0">
              <div className={cn('w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all', step >= i ? 'bg-primary text-white' : 'bg-muted text-muted-foreground')}>{i + 1}</div>
              <span className={cn('text-sm font-semibold hidden sm:block', step >= i ? 'text-foreground' : 'text-muted-foreground')}>{label}</span>
            </div>
          </React.Fragment>
        ))}
      </div>

      {/* Step 1 */}
      {step === 0 && (
        <div className="animate-fade-in space-y-4">
          <Card><CardHeader><CardTitle>Upload Mode</CardTitle></CardHeader><CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[{ val: 'separate', icon: <Users className="h-5 w-5" />, title: 'Students + Halls', desc: 'Two separate CSV files', rec: true }, { val: 'combined', icon: <FileText className="h-5 w-5" />, title: 'Combined CSV', desc: 'Single file with all data' }].map((m) => (
                <button key={m.val} onClick={() => setMode(m.val)} className={cn('flex items-center gap-4 p-5 rounded-2xl border-2 text-left transition-all', mode === m.val ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/30')}>
                  <div className={cn('w-12 h-12 rounded-xl flex items-center justify-center shrink-0', mode === m.val ? 'bg-primary text-white' : 'bg-muted text-muted-foreground')}>{m.icon}</div>
                  <div><p className="font-bold">{m.title}{m.rec && <Badge variant="success" className="ml-2">Recommended</Badge>}</p><p className="text-xs text-muted-foreground">{m.desc}</p></div>
                </button>
              ))}
            </div>
          </CardContent></Card>

          {mode === 'separate' && (<>
            <Card><CardHeader><CardTitle className="flex items-center gap-2"><Users className="h-5 w-5 text-primary" />Students CSV</CardTitle></CardHeader><CardContent>
              {loadingList ? <Loader /> : studentCsvs.length ? <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">{studentCsvs.map((c) => <CsvCard key={c.id} csv={c} onClick={setSelStudentCsv} selected={selStudentCsv?.id === c.id} />)}</div> : <p className="text-muted-foreground">No CSVs yet.</p>}
              <UploadBox label="Upload Students" desc="student_id, name, subject_code, [class]" onUpload={uploadStudents} loading={upStuLd} result={upStuRes} error={upStuErr} />
            </CardContent></Card>
            <Card><CardHeader><CardTitle className="flex items-center gap-2"><Home className="h-5 w-5 text-primary" />Halls CSV</CardTitle></CardHeader><CardContent>
              {loadingList ? <Loader /> : hallCsvs.length ? <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">{hallCsvs.map((c) => <CsvCard key={c.id} csv={c} onClick={setSelHallCsv} selected={selHallCsv?.id === c.id} />)}</div> : <p className="text-muted-foreground">No CSVs yet.</p>}
              <UploadBox label="Upload Halls" desc="hall_id, capacity, [rows, columns]" onUpload={uploadHalls} loading={upHallLd} result={upHallRes} error={upHallErr} />
            </CardContent></Card>
          </>)}

          {mode === 'combined' && (
            <Card><CardHeader><CardTitle>Combined CSV</CardTitle></CardHeader><CardContent>
              {loadingList ? <Loader /> : combinedCsvs.length ? <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">{combinedCsvs.map((c) => <CsvCard key={c.id} csv={c} onClick={setSelCombinedCsv} selected={selCombinedCsv?.id === c.id} />)}</div> : <p className="text-muted-foreground">No CSVs yet.</p>}
              <UploadBox label="Upload Combined" desc="student_id, name, subject_code, hall_id, hall_capacity" onUpload={uploadCombined} loading={upCombLd} result={upCombRes} error={upCombErr} />
            </CardContent></Card>
          )}

          <Button size="xl" className="w-full" onClick={goToStep2} disabled={!canProceed}>Next: Select Students <ArrowRight className="h-4 w-4" /></Button>
        </div>
      )}

      {/* Step 2 */}
      {step === 1 && (
        <Card className="animate-slide-in"><CardHeader className="flex-row items-center justify-between"><CardTitle>Select Students</CardTitle><Button variant="outline" size="sm" onClick={() => setStep(0)}>← Back</Button></CardHeader><CardContent>
          {loadingData ? <Loader /> : (<>
            {hallsList.length > 0 && <div className="bg-sky-50 border-l-4 border-sky-500 p-3 rounded-lg text-sky-700 text-sm mb-4">🏛 {hallsList.length} halls · Capacity: {hallsList.reduce((s, h) => s + h.capacity, 0)}</div>}
            {classes.length > 0 && <div className="mb-4"><p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Classes</p><div className="flex flex-wrap gap-1.5">{classes.map((c) => <button key={c} onClick={() => toggleChip(selClasses, setSelClasses, c)} className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', selClasses.includes(c) ? 'bg-primary text-white' : 'bg-muted text-muted-foreground')}>{c}</button>)}</div></div>}
            <div className="mb-4"><p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Subjects</p><div className="flex flex-wrap gap-1.5">{subjects.map((s) => <button key={s} onClick={() => toggleChip(selSubjects, setSelSubjects, s)} className={cn('px-3 py-1 rounded-lg text-xs font-bold transition-all', selSubjects.includes(s) ? 'bg-primary text-white' : 'bg-muted text-muted-foreground')}>{s}</button>)}</div></div>
            <h4 className="font-bold text-lg mb-3">Students ({activeStudents.length}/{filteredStudents.length})</h4>
            <div className="max-h-96 overflow-auto rounded-xl border"><table className="w-full"><thead><tr className="bg-muted/50 border-b sticky top-0 z-10"><th className="py-2 px-3 w-10">✓</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">ID</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">Name</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">Subject</th><th className="text-left py-2 px-3 text-xs font-bold uppercase text-muted-foreground">Class</th></tr></thead>
              <tbody>{filteredStudents.map((s) => <tr key={s.student_id} className={cn('border-b border-border/50', excluded.has(s.student_id) && 'opacity-30 line-through')}><td className="py-2 px-3"><Checkbox checked={!excluded.has(s.student_id)} onCheckedChange={() => toggleExclude(s.student_id)} /></td><td className="py-2 px-3 font-bold text-sm">{s.student_id}</td><td className="py-2 px-3 text-sm">{s.name}</td><td className="py-2 px-3"><Badge variant="outline">{s.subject_code}</Badge></td><td className="py-2 px-3 text-sm">{s.student_class}</td></tr>)}</tbody></table></div>
            <Button size="xl" className="w-full mt-4" onClick={() => setStep(2)} disabled={!activeStudents.length}>Next: Schedule ({activeStudents.length}) <ArrowRight className="h-4 w-4" /></Button>
          </>)}
        </CardContent></Card>
      )}

      {/* Step 3 */}
      {step === 2 && (
        <Card className="animate-slide-in"><CardHeader className="flex-row items-center justify-between"><CardTitle>Schedule & Invigilators</CardTitle><Button variant="outline" size="sm" onClick={() => setStep(1)}>← Back</Button></CardHeader><CardContent>
          <div className="space-y-3 mb-6"><Label>Session Name</Label><Input value={sessionName} onChange={(e) => setSessionName(e.target.value)} /></div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
            <div><Label>Exam Date *</Label><Input type="date" required value={examDate} onChange={(e) => setExamDate(e.target.value)} className="mt-1" /></div>
            <div><Label>From *</Label><Input type="time" required value={timeFrom} onChange={(e) => setTimeFrom(e.target.value)} className="mt-1" /></div>
            <div><Label>To *</Label><Input type="time" required value={timeTo} onChange={(e) => setTimeTo(e.target.value)} className="mt-1" /></div>
          </div>
          <div className="grid grid-cols-3 gap-3 mb-6">
            {[{ v: activeStudents.length, l: 'Students', c: 'text-primary' }, { v: hallsList.length, l: 'Halls', c: 'text-secondary' }, { v: hallsList.reduce((s, h) => s + h.capacity, 0), l: 'Seats', c: 'text-info' }].map((s) => (
              <div key={s.l} className="text-center p-4 bg-muted rounded-2xl"><p className={cn('text-2xl font-extrabold', s.c)}>{s.v}</p><p className="text-xs font-semibold text-muted-foreground">{s.l}</p></div>
            ))}
          </div>
          <h4 className="font-bold mb-3">Assign Invigilators</h4>
          {hallsList.map((h) => (
            <div key={h.hall_id} className="flex items-start gap-4 p-3 bg-muted/50 rounded-xl mb-2">
              <div className="min-w-[100px]"><p className="font-bold">{h.hall_id}</p><p className="text-xs text-muted-foreground">{h.rows}×{h.columns} · {h.capacity}</p></div>
              <select multiple className="flex-1 min-h-[60px] border rounded-lg p-2 text-sm bg-background" value={hallInvigs[h.hall_id] || []} onChange={(e) => { const v = [...e.target.selectedOptions].map((o) => parseInt(o.value)); setHallInvigs((p) => ({ ...p, [h.hall_id]: v })); }}>
                {faculty.map((f) => <option key={f.id} value={f.id}>{f.name} ({f.department})</option>)}
              </select>
            </div>
          ))}
          {!faculty.length && <p className="text-muted-foreground text-sm">No faculty.</p>}
          <Button size="xl" variant="success" className="w-full mt-6" onClick={handleCreate} disabled={creating}>{creating ? <><Loader2 className="h-5 w-5 animate-spin" />Generating...</> : <><Play className="h-5 w-5" />Allocate & Generate</>}</Button>
        </CardContent></Card>
      )}

      {/* Step 4 */}
      {step === 3 && allocResult && (
        <Card className="animate-scale-in"><CardHeader><CardTitle>✅ Allocation Complete</CardTitle></CardHeader><CardContent>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[{ v: allocResult.allocated, l: 'Allocated', c: 'text-emerald-600 bg-emerald-50' }, { v: allocResult.unallocated, l: 'Unallocated', c: allocResult.unallocated > 0 ? 'text-red-600 bg-red-50' : 'text-emerald-600 bg-emerald-50' }, { v: `${allocResult.time_ms}ms`, l: 'Time', c: 'text-sky-600 bg-sky-50' }].map((s) => (
              <div key={s.l} className={cn('text-center p-4 rounded-2xl', s.c)}><p className="text-2xl font-extrabold">{s.v}</p><p className="text-xs font-semibold">{s.l}</p></div>
            ))}
          </div>
          {allocResult.hall_assignments && Object.keys(allocResult.hall_assignments).length > 0 && (
            <div className="mb-4"><h4 className="font-bold mb-2">Hall Assignments</h4><div className="flex flex-wrap gap-2">{Object.entries(allocResult.hall_assignments).map(([h, c]) => <Badge key={h} variant="outline" className="text-sm">{h}: {c}</Badge>)}</div></div>
          )}
          {allocResult.warnings?.map((w, i) => <div key={i} className="bg-amber-50 border-l-4 border-amber-500 p-2 rounded text-amber-700 text-sm mb-2">⚠️ {w}</div>)}
          <Button size="xl" className="w-full mt-4" onClick={() => nav(`/allocations/${sessionId}`)}>View Seating Layout <ArrowRight className="h-4 w-4" /></Button>
        </CardContent></Card>
      )}
    </div>
  );
}