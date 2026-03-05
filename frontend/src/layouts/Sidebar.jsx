import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Plus, List, Users, UserPlus, User, LogOut, BookOpen, GraduationCap, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import useAuth from '@/hooks/useAuth';

const ROLE_COLORS = { ADMIN: 'bg-red-500', FACULTY: 'bg-sky-500', STUDENT: 'bg-emerald-500' };

function NavItem({ to, icon: Icon, label, end }) {
  const location = useLocation();
  const isActive = end ? location.pathname === to : location.pathname.startsWith(to);
  return (
    <NavLink
      to={to} end={end}
      className={cn(
        'flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group',
        isActive
          ? 'bg-white/10 text-white shadow-sm backdrop-blur-sm'
          : 'text-slate-400 hover:text-white hover:bg-white/5'
      )}
    >
      <Icon className={cn('h-[18px] w-[18px] transition-transform group-hover:scale-110', isActive && 'text-teal-400')} />
      <span>{label}</span>
      {isActive && <div className="ml-auto w-1 h-5 rounded-full bg-teal-400" />}
    </NavLink>
  );
}

function SectionLabel({ children }) {
  return <p className="px-4 pt-6 pb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500">{children}</p>;
}

export default function Sidebar({ mobileOpen, onClose }) {
  const { user, logout } = useAuth();
  if (!user) return null;

  const isAdmin = user.role === 'ADMIN';
  const isAF = ['ADMIN', 'FACULTY'].includes(user.role);
  const isStudent = user.role === 'STUDENT';

  const content = (
    <div className="h-full flex flex-col bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
      <div className="absolute top-0 left-0 right-0 h-48 bg-gradient-to-br from-teal-600/10 to-orange-500/5 pointer-events-none" />

      {/* Brand */}
      <div className="relative z-10 px-5 py-5 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center shadow-lg shadow-teal-500/25">
          <GraduationCap className="h-6 w-6 text-white" />
        </div>
        <div>
          <h2 className="text-white font-extrabold text-lg leading-tight tracking-tight">ExamAlloc</h2>
          <p className="text-[10px] text-slate-500 font-semibold tracking-[0.1em] uppercase">Hall Management</p>
        </div>
        {mobileOpen && (
          <button onClick={onClose} className="ml-auto text-slate-400 hover:text-white md:hidden">
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <Separator className="bg-white/5 mx-4" />

      {/* User */}
      <div className="px-5 py-3 flex items-center gap-3">
        <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center text-white text-sm font-bold ring-2 ring-offset-1 ring-offset-slate-800', ROLE_COLORS[user.role], `ring-${ROLE_COLORS[user.role]?.replace('bg-', '')}/30`)}>
          {(user.first_name || user.username)?.[0]?.toUpperCase()}
        </div>
        <div className="overflow-hidden">
          <p className="text-white text-sm font-semibold truncate">{user.first_name || user.username}</p>
          <p className={cn('text-[10px] font-bold uppercase tracking-wider', user.role === 'ADMIN' ? 'text-red-400' : user.role === 'FACULTY' ? 'text-sky-400' : 'text-emerald-400')}>
            {user.role}
          </p>
        </div>
      </div>

      <Separator className="bg-white/5 mx-4" />

      {/* Nav */}
      <nav className="flex-1 overflow-auto py-2 px-3 space-y-0.5 relative z-10">
        {isAF && (<>
          <SectionLabel>{isAdmin ? 'Management' : 'Overview'}</SectionLabel>
          <NavItem to="/" icon={LayoutDashboard} label="Dashboard" end />
          {isAdmin && <NavItem to="/new" icon={Plus} label="New Allocation" />}
          <NavItem to="/allocations" icon={List} label="Allocations" />
          <SectionLabel>Data</SectionLabel>
          <NavItem to="/students" icon={Users} label="Students" />
          {isAdmin && <NavItem to="/users" icon={UserPlus} label="Faculty / Users" />}
        </>)}
        {isStudent && (<>
          <SectionLabel>Portal</SectionLabel>
          <NavItem to="/my-allocations" icon={BookOpen} label="My Allocations" />
        </>)}
        <SectionLabel>Account</SectionLabel>
        <NavItem to="/profile" icon={User} label="Profile" />
      </nav>

      {/* Logout */}
      <div className="p-3">
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-semibold text-red-400 bg-red-500/5 border border-red-500/10 hover:bg-red-500/10 transition-all"
        >
          <LogOut className="h-[18px] w-[18px]" />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop */}
      <aside className="hidden md:block fixed inset-y-0 left-0 z-30 w-72 shadow-xl shadow-black/10">
        {content}
      </aside>
      {/* Mobile */}
      <aside className={cn('md:hidden fixed inset-y-0 left-0 z-50 w-72 transition-transform duration-300', mobileOpen ? 'translate-x-0' : '-translate-x-full')}>
        {content}
      </aside>
    </>
  );
}