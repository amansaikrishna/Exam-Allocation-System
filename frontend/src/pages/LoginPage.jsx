import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { GraduationCap, Eye, EyeOff, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import useAuth from '@/hooks/useAuth';

export default function LoginPage() {
  const [username, setUsername] = useState(''); const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false); const [showPw, setShowPw] = useState(false);
  const { login } = useAuth(); const nav = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true);
    try {
      const u = await login(username, password);
      toast.success(`Welcome back, ${u.first_name || u.username}!`);
      nav(u.role === 'STUDENT' ? '/my-allocations' : '/');
    } catch (err) { toast.error(err.response?.data?.non_field_errors?.[0] || 'Invalid credentials'); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 relative overflow-hidden">
      <div className="absolute top-[-200px] right-[-200px] w-[600px] h-[600px] rounded-full bg-teal-500/10 blur-3xl" />
      <div className="absolute bottom-[-150px] left-[-100px] w-[400px] h-[400px] rounded-full bg-orange-500/8 blur-3xl" />

      <div className="relative z-10 w-full max-w-md animate-scale-in">
        <Card className="border-0 shadow-2xl shadow-black/20">
          <CardContent className="p-8 sm:p-10">
            <div className="text-center mb-8">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-600 flex items-center justify-center mx-auto mb-4 shadow-xl shadow-teal-500/30">
                <GraduationCap className="h-10 w-10 text-white" />
              </div>
              <h1 className="text-3xl font-extrabold tracking-tight">ExamAlloc</h1>
              <p className="text-muted-foreground mt-1">Examination Hall Allocation System</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input id="username" value={username} onChange={e => setUsername(e.target.value)} required autoFocus placeholder="Enter username" className="h-12 text-base" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input id="password" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} required placeholder="Enter password" className="h-12 text-base pr-12" />
                  <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors">
                    {showPw ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>
              <Button type="submit" size="xl" className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 shadow-lg shadow-teal-600/30 text-base" disabled={loading}>
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : 'Sign In'}
              </Button>
            </form>

            <div className="mt-8 pt-5 border-t">
              <div className="bg-muted rounded-xl p-4 text-center space-y-1">
                <p className="text-xs font-mono"><strong>Admin:</strong> admin / admin123</p>
                <p className="text-xs font-mono"><strong>Students:</strong> rollno (lowercase) / rollno@first4lettersofname</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}