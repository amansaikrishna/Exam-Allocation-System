import React from 'react';
import { Loader2 } from 'lucide-react';

export default function Loader({ text = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 animate-fade-in">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <p className="text-sm text-muted-foreground font-medium">{text}</p>
    </div>
  );
}