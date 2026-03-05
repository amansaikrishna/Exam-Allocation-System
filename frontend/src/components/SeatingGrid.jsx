import React, { useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';

const PALETTE = [
  '#0d9488', '#f97316', '#0ea5e9', '#e11d48', '#8b5cf6',
  '#22c55e', '#eab308', '#ec4899', '#06b6d4', '#84cc16',
  '#d946ef', '#f43f5e', '#14b8a6', '#a855f7', '#fb923c',
];

export default function SeatingGrid({ layout, searchId, highlightStudentId, filterSubject, filterClass, highlightSeat }) {
  const foundRef = useRef(null);

  useEffect(() => {
    if (foundRef.current) foundRef.current.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });
  }, [highlightSeat, layout]);

  if (!layout?.grid) {
    return (
      <div className="flex justify-center py-12">
        <p className="text-muted-foreground">Loading layout...</p>
      </div>
    );
  }

  const subjects = new Set();
  layout.grid.forEach((r) => r.forEach((c) => { if (c) subjects.add(c.subject_code); }));
  const sorted = Array.from(subjects).sort();
  const colorMap = {};
  sorted.forEach((s, i) => { colorMap[s] = PALETTE[i % PALETTE.length]; });

  const isFoundSeat = (cell, r, c) =>
    highlightSeat && cell && highlightSeat.student_id === cell.student_id && highlightSeat.row === r && highlightSeat.col === c;

  const isMatch = (cell) => {
    if (!cell) return false;
    if (searchId && cell.student_id.toLowerCase().includes(searchId.toLowerCase())) return true;
    if (highlightStudentId && cell.student_id === highlightStudentId) return true;
    return false;
  };

  const isDimmed = (cell, r, c) => {
    if (isFoundSeat(cell, r, c)) return false;
    if (!searchId && !highlightStudentId && !filterSubject && !filterClass && !highlightSeat) return false;
    if (!cell) return true;
    if (highlightSeat) return !isFoundSeat(cell, r, c);
    if (searchId || highlightStudentId) return !isMatch(cell);
    if (filterSubject && cell.subject_code !== filterSubject) return true;
    if (filterClass && cell.student_class !== filterClass) return true;
    return false;
  };

  const cols = layout.columns;

  // Grid template: row-header + N equal columns that fill 100%
  const gridCols = `48px repeat(${cols}, minmax(0, 1fr))`;

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex flex-wrap gap-2">
        {sorted.map((s) => (
          <span
            key={s}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold text-white shadow-sm"
            style={{ backgroundColor: colorMap[s] }}
          >
            {s}
          </span>
        ))}
        <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 text-slate-400 border border-slate-200">
          Empty
        </span>
      </div>

      {/* Grid - full width */}
      <div className="w-full border-2 border-slate-800 rounded-2xl overflow-hidden shadow-lg">
        {/* Column header row */}
        <div className="grid" style={{ gridTemplateColumns: gridCols }}>
          {/* Corner */}
          <div className="h-10 bg-slate-900" />
          {/* Col headers */}
          {Array.from({ length: cols }, (_, c) => (
            <div
              key={c}
              className="h-10 bg-slate-900 text-slate-400 flex items-center justify-center text-[11px] font-bold border-l border-slate-700/50 select-none"
            >
              C{c + 1}
            </div>
          ))}
        </div>

        {/* Data rows */}
        {layout.grid.map((row, r) => (
          <div key={r} className="grid" style={{ gridTemplateColumns: gridCols }}>
            {/* Row header */}
            <div className="min-h-[72px] bg-slate-800 text-slate-400 flex items-center justify-center text-[11px] font-bold border-t border-slate-700/50 select-none">
              R{r + 1}
            </div>

            {/* Seats */}
            {row.map((cell, c) => {
              const found = isFoundSeat(cell, r, c);
              const matched = isMatch(cell);
              const dimmed = isDimmed(cell, r, c);
              const color = cell ? (colorMap[cell.subject_code] || '#94a3b8') : undefined;

              return (
                <Tooltip key={c}>
                  <TooltipTrigger asChild>
                    <div
                      ref={found ? foundRef : null}
                      className={cn(
                        'min-h-[72px] flex flex-col items-center justify-center border-r border-b transition-all duration-200 relative select-none',
                        cell ? 'border-black/10' : 'border-slate-200 bg-slate-50',
                        dimmed && 'opacity-[0.08] grayscale',
                        matched && 'ring-[3px] ring-white ring-offset-0 z-10 animate-glow',
                        found && 'z-20 scale-110 animate-found-pulse',
                        !dimmed && !found && 'hover:brightness-110 hover:z-10 hover:shadow-lg',
                      )}
                      style={{
                        backgroundColor: found ? '#eab308' : cell ? color : undefined,
                        backgroundImage: cell
                          ? 'linear-gradient(180deg, rgba(255,255,255,0.15) 0%, transparent 50%, rgba(0,0,0,0.08) 100%)'
                          : undefined,
                        ...(matched && {
                          boxShadow: `0 0 0 3px ${color}, 0 0 20px ${color}80`,
                        }),
                        ...(found && {
                          boxShadow: '0 0 0 3px #eab308, 0 0 24px rgba(234,179,8,0.6)',
                          outline: '3px solid white',
                          outlineOffset: '-3px',
                        }),
                      }}
                    >
                      {cell ? (
                        <>
                          <span className="font-extrabold text-[12px] sm:text-[13px] text-white leading-tight drop-shadow-sm truncate max-w-full px-1">
                            {cell.student_id}
                          </span>
                          <span className="text-[10px] sm:text-[11px] text-white/75 font-semibold mt-0.5 drop-shadow-sm truncate max-w-full px-1">
                            {cell.subject_code}
                          </span>
                        </>
                      ) : (
                        <span className="text-slate-300 text-base">—</span>
                      )}
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-xs">
                    {cell ? (
                      <div className="space-y-0.5">
                        <p className="font-bold">{cell.student_id}</p>
                        <p className="text-xs opacity-80">{cell.name}</p>
                        <p className="text-xs opacity-60">
                          {cell.subject_code}
                          {cell.student_class ? ` · ${cell.student_class}` : ''}
                        </p>
                      </div>
                    ) : (
                      'Empty Seat'
                    )}
                  </TooltipContent>
                </Tooltip>
              );
            })}
          </div>
        ))}
      </div>

      {/* Meta */}
      <div className="flex flex-wrap gap-3 items-center text-sm">
        <span className="font-bold text-base">{layout.hall_id}</span>
        <span
          className={cn(
            'inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold text-white',
            layout.occupied === layout.capacity ? 'bg-emerald-500' : 'bg-sky-500',
          )}
        >
          {layout.occupied}/{layout.capacity} occupied
        </span>
        <span className="text-muted-foreground text-xs">
          {layout.rows} rows × {layout.columns} columns
        </span>
        {layout.invigilators?.length > 0 && (
          <span className="text-xs text-muted-foreground">
            Invigilators: <strong>{layout.invigilators.map((i) => i.name).join(', ')}</strong>
          </span>
        )}
      </div>
    </div>
  );
}