import * as React from 'react';
import { cn } from '@/lib/utils';

const Select = React.forwardRef(({ className, children, ...props }, ref) => (
  <select
    ref={ref}
    className={cn(
      'flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background transition-all focus:outline-none focus:ring-2 focus:ring-ring/20 focus:border-primary disabled:cursor-not-allowed disabled:opacity-50 appearance-none cursor-pointer',
      className
    )}
    {...props}
  >
    {children}
  </select>
));
Select.displayName = 'Select';

export { Select };