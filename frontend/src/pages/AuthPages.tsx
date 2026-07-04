import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Lock,
  Mail,
  User,
  ArrowLeft,
  CheckCircle,
  Save,
  BellRing
} from 'lucide-react';

/* ----------------- LOGIN PAGE ----------------- */
export function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Redirect straight to dashboard for preview purposes
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#050816] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm bg-[#111827] border border-[#2A3352] rounded-xl p-8 shadow-2xl space-y-6"
      >
        <div className="text-center space-y-2">
          <h2 className="font-heading font-bold text-2xl text-white">Welcome back</h2>
          <p className="text-xs text-gray-400">Sign in to your EvalForge developer console.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@evalforge.ai"
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Password</label>
              <Link to="/forgot-password" className="text-[10px] text-primary hover:underline font-semibold">Forgot?</Link>
            </div>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition mt-6"
          >
            Sign In
          </button>
        </form>

        <div className="text-center text-xs text-gray-400 pt-2 border-t border-[#2A3352]/40">
          New developer? <Link to="/register" className="text-primary hover:underline font-semibold">Create account</Link>
        </div>
      </motion.div>
    </div>
  );
}

/* ----------------- REGISTER PAGE ----------------- */
export function Register() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-[#050816] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm bg-[#111827] border border-[#2A3352] rounded-xl p-8 shadow-2xl space-y-6"
      >
        <div className="text-center space-y-2">
          <h2 className="font-heading font-bold text-2xl text-white">Create Developer Account</h2>
          <p className="text-xs text-gray-400">Launch standard validation test suites instantly.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Hardik Kaurani"
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@evalforge.ai"
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition mt-6"
          >
            Create Account
          </button>
        </form>

        <div className="text-center text-xs text-gray-400 pt-2 border-t border-[#2A3352]/40">
          Have an account? <Link to="/login" className="text-primary hover:underline font-semibold">Sign in</Link>
        </div>
      </motion.div>
    </div>
  );
}

/* ----------------- FORGOT PASSWORD ----------------- */
export function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-[#050816] flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm bg-[#111827] border border-[#2A3352] rounded-xl p-8 shadow-2xl space-y-6"
      >
        <div className="space-y-2">
          <Link to="/login" className="text-gray-500 hover:text-white text-xs flex items-center gap-1.5 transition">
            <ArrowLeft size={12} /> Back to Sign In
          </Link>
          <h2 className="font-heading font-bold text-2xl text-white">Reset Password</h2>
          <p className="text-xs text-gray-400">Request password validation credentials.</p>
        </div>

        {submitted ? (
          <div className="space-y-4 text-center">
            <CheckCircle className="text-emerald-400 mx-auto" size={36} />
            <p className="text-sm text-gray-300">If registered, a recovery link will arrive in your email shortly.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-2.5 text-gray-500 w-4.5 h-4.5" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="developer@evalforge.ai"
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg pl-10 pr-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition mt-4"
            >
              Send Reset Link
            </button>
          </form>
        )}
      </motion.div>
    </div>
  );
}

/* ----------------- PROFILE MANAGEMENT PAGE ----------------- */
export function Profile() {
  const [name, setName] = useState('Hardik Kaurani');
  const [email, setEmail] = useState('hardikkaurani1@gmail.com');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 max-w-2xl mx-auto"
    >
      <div>
        <h1 className="font-heading font-bold text-3xl text-white font-bold">Developer Profile</h1>
        <p className="text-gray-400 text-sm mt-1">Configure profile notifications, check credentials and security tokens.</p>
      </div>

      <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6">
        <form onSubmit={handleSave} className="space-y-5">
          <div className="flex items-center gap-4 border-b border-[#2A3352] pb-5">
            <div className="w-16 h-16 bg-gradient-to-tr from-primary to-accent rounded-xl flex items-center justify-center font-bold text-white text-2xl">
              HK
            </div>
            <div>
              <h3 className="font-heading font-bold text-lg text-white">Personal Account</h3>
              <p className="text-xs text-gray-500 font-mono">Workspace Role: Administrator</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Full Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          {/* Preferences Checkboxes */}
          <div className="space-y-3.5 pt-4 border-t border-[#2A3352]/40">
            <h4 className="font-semibold text-sm text-gray-300 flex items-center gap-2">
              <BellRing size={16} className="text-primary" /> Notification Settings
            </h4>
            <div className="space-y-2">
              <label className="flex items-center gap-3 text-xs text-gray-400 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded border-[#2A3352] text-primary bg-[#050816]" />
                <span>Email me weekly pipeline stats and evaluation summaries.</span>
              </label>
              <label className="flex items-center gap-3 text-xs text-gray-400 cursor-pointer">
                <input type="checkbox" defaultChecked className="rounded border-[#2A3352] text-primary bg-[#050816]" />
                <span>Notify me immediately when judicial score slips below 70%.</span>
              </label>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-[#2A3352]/40">
            {saved ? (
              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                <CheckCircle size={14} /> Profile updated successfully
              </span>
            ) : (
              <span />
            )}
            <button
              type="submit"
              className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-medium px-4 py-2 rounded-lg text-sm transition"
            >
              <Save size={14} /> Save Profile
            </button>
          </div>
        </form>
      </div>
    </motion.div>
  );
}
