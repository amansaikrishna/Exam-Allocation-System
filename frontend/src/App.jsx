import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { TooltipProvider } from '@/components/ui/tooltip';
import { AuthProvider } from '@/context/AuthContext';
import useAuth from '@/hooks/useAuth';
import DashboardLayout from '@/layouts/DashboardLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import NewAllocationPage from '@/pages/NewAllocationPage';
import SessionDetailPage from '@/pages/SessionDetailPage';
import AllocationsPage from '@/pages/AllocationsPage';
import StudentsPage from '@/pages/StudentsPage';
import UsersPage from '@/pages/UsersPage';
import ProfilePage from '@/pages/ProfilePage';
import StudentPortal from '@/pages/StudentPortal';

function AppRoutes() {
  const { user } = useAuth();
  const home = user?.role === 'STUDENT' ? '/my-allocations' : '/';
  return (
    <>
      <Routes>
        <Route path="/login" element={user ? <Navigate to={home} /> : <LoginPage />} />
        <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
          <Route path="/" element={<ProtectedRoute roles={['ADMIN', 'FACULTY']}><DashboardPage /></ProtectedRoute>} />
          <Route path="/new" element={<ProtectedRoute roles={['ADMIN']}><NewAllocationPage /></ProtectedRoute>} />
          <Route path="/allocations" element={<ProtectedRoute roles={['ADMIN', 'FACULTY']}><AllocationsPage /></ProtectedRoute>} />
          <Route path="/allocations/:id" element={<ProtectedRoute roles={['ADMIN', 'FACULTY']}><SessionDetailPage /></ProtectedRoute>} />
          <Route path="/students" element={<ProtectedRoute roles={['ADMIN', 'FACULTY']}><StudentsPage /></ProtectedRoute>} />
          <Route path="/users" element={<ProtectedRoute roles={['ADMIN']}><UsersPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/my-allocations" element={<ProtectedRoute roles={['STUDENT']}><StudentPortal /></ProtectedRoute>} />
        </Route>
        <Route path="*" element={<Navigate to={user ? home : '/login'} replace />} />
      </Routes>
      <ToastContainer position="top-center" autoClose={3000} hideProgressBar={false} newestOnTop theme="light"
        toastStyle={{ borderRadius: 14, fontFamily: '"DM Sans",sans-serif', fontSize: '0.875rem', fontWeight: 500, boxShadow: '0 8px 32px rgba(0,0,0,0.12)' }} />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <TooltipProvider delayDuration={200}>
          <AppRoutes />
        </TooltipProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}