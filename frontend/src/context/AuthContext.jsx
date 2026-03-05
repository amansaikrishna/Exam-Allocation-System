import React, { createContext, useState, useCallback } from 'react';
import { auth as authAPI } from '@/api/endpoints';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const s = localStorage.getItem('user');
    return s ? JSON.parse(s) : null;
  });

  const login = useCallback(async (username, password) => {
    const r = await authAPI.login({ username, password });
    const u = r.data.user;
    localStorage.setItem('user', JSON.stringify(u));
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(async () => {
    try { await authAPI.logout(); } catch {}
    localStorage.removeItem('user');
    setUser(null);
  }, []);

  const refresh = useCallback(async () => {
    try { const r = await authAPI.me(); const u = r.data; localStorage.setItem('user', JSON.stringify(u)); setUser(u); }
    catch { logout(); }
  }, [logout]);

  return <AuthContext.Provider value={{ user, login, logout, refresh }}>{children}</AuthContext.Provider>;
}