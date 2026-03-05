import * as React from 'react';
import * as TabsPrimitive from '@radix-ui/react-tabs';
import { cn } from '@/lib/utils';

const Tabs = TabsPrimitive.Root;

const TabsList = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.List
    ref={ref}
    className={cn('flex border-b-2 border-border gap-0', className)}
    {...props}
  />
));

const TabsTrigger = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.Trigger
    ref={ref}
    className={cn(
      'inline-flex items-center gap-2 whitespace-nowrap px-5 py-3 text-sm font-semibold text-muted-foreground border-b-2 border-transparent -mb-[2px] transition-all hover:text-foreground data-[state=active]:border-primary data-[state=active]:text-primary',
      className
    )}
    {...props}
  />
));

const TabsContent = React.forwardRef(({ className, ...props }, ref) => (
  <TabsPrimitive.Content ref={ref} className={cn('mt-4 animate-fade-in', className)} {...props} />
));

export { Tabs, TabsList, TabsTrigger, TabsContent };