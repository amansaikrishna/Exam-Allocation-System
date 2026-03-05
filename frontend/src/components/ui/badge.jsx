import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-lg px-3 py-1 text-xs font-bold transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary/10 text-primary',
        secondary: 'bg-secondary/10 text-secondary',
        destructive: 'bg-destructive/10 text-destructive',
        success: 'bg-emerald-100 text-emerald-700',
        warning: 'bg-amber-100 text-amber-700',
        info: 'bg-sky-100 text-sky-700',
        outline: 'border border-border text-foreground',
        draft: 'bg-slate-100 text-slate-600',
        uploaded: 'bg-blue-100 text-blue-700',
        allocated: 'bg-emerald-100 text-emerald-700',
        approved: 'bg-amber-100 text-amber-700',
        failed: 'bg-red-100 text-red-700',
        completed: 'bg-violet-100 text-violet-700',
        admin: 'bg-red-100 text-red-700',
        faculty: 'bg-sky-100 text-sky-700',
        student: 'bg-emerald-100 text-emerald-700',
      },
    },
    defaultVariants: { variant: 'default' },
  }
);

function Badge({ className, variant, ...props }) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };