import React from 'react';
import { cn } from '@/lib/utils';

const COLOR_MAP = {
  indigo:  { bg: 'bg-indigo-100',  text: 'text-indigo-600',  ring: 'ring-indigo-500/20'  },
  emerald: { bg: 'bg-emerald-100', text: 'text-emerald-600', ring: 'ring-emerald-500/20' },
  violet:  { bg: 'bg-violet-100',  text: 'text-violet-600',  ring: 'ring-violet-500/20'  },
  pink:    { bg: 'bg-pink-100',    text: 'text-pink-600',    ring: 'ring-pink-500/20'    },
  cyan:    { bg: 'bg-cyan-100',    text: 'text-cyan-600',    ring: 'ring-cyan-500/20'    },
  amber:   { bg: 'bg-amber-100',   text: 'text-amber-600',   ring: 'ring-amber-500/20'   },
  red:     { bg: 'bg-red-100',     text: 'text-red-600',     ring: 'ring-red-500/20'     },
  sky:     { bg: 'bg-sky-100',     text: 'text-sky-600',     ring: 'ring-sky-500/20'     },
  teal:    { bg: 'bg-teal-100',    text: 'text-teal-600',    ring: 'ring-teal-500/20'    },
  orange:  { bg: 'bg-orange-100',  text: 'text-orange-600',  ring: 'ring-orange-500/20'  },
  blue:    { bg: 'bg-blue-100',    text: 'text-blue-600',    ring: 'ring-blue-500/20'    },
};

const DEFAULT_COLOR = { bg: 'bg-slate-100', text: 'text-slate-500', ring: 'ring-slate-500/20' };

export default function StatsCard({ icon, value, label, color = 'indigo', onClick, className }) {
  const c = COLOR_MAP[color] || DEFAULT_COLOR;

  return (
    <div
      onClick={onClick}
      className={cn(
        'group relative bg-card border rounded-2xl p-6 text-center transition-all duration-300 hover:shadow-lg hover:-translate-y-1',
        onClick && 'cursor-pointer hover:border-primary/30',
        className,
      )}
    >
      <div
        className={cn(
          'mx-auto mb-3 w-12 h-12 rounded-xl flex items-center justify-center ring-4 transition-transform group-hover:scale-110',
          c.bg,
          c.text,
          c.ring,
        )}
      >
        {icon}
      </div>
      <div className="text-2xl font-extrabold tracking-tight">{value}</div>
      <div className="text-[11px] font-semibold text-muted-foreground mt-1 uppercase tracking-wider">{label}</div>
    </div>
  );
}