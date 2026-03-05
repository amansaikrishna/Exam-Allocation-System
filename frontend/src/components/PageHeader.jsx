import React from 'react';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useOutletContext } from 'react-router-dom';

export default function PageHeader({ title, subtitle, children }) {
  const context = useOutletContext();
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8 animate-fade-in">
      <div className="flex items-center gap-3">
        {context?.onMenuClick && (
          <Button variant="ghost" size="icon" className="md:hidden" onClick={context.onMenuClick}>
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">{title}</h1>
          {subtitle && <p className="text-sm text-muted-foreground mt-1 max-w-xl">{subtitle}</p>}
        </div>
      </div>
      {children && <div className="flex gap-2 items-center flex-wrap">{children}</div>}
    </div>
  );
}