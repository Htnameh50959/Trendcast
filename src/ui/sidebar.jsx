import React from 'react'
import { Link, useLocation } from "wouter";
import {
  LayoutDashboard,
  TrendingUp,
  Database,
  LineChart,
  Trash2,
  Loader2,
  Sparkles,
  LogOut,
  User,
  LogIn,
} from "lucide-react";
import { useAuth } from "../page/AuthModal";
import "./ui.css";

const path = [
  { label: "Dashboard", icon: LayoutDashboard, href: "/" },
  { label: "Sales Data", icon: Database, href: "/Sales" },
  { label: "Forecasts", icon: TrendingUp, href: "/Forecasts" }
];

export function Sidebar({ onLoginClick }) {
  const [location] = useLocation();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="sidebar w-72 h-screen bg-white border-r border-slate-100 flex flex-col p-6 shadow-sm">
      <div className="sidebar-logo flex items-center gap-3 mb-12 px-2">
        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
          <TrendingUp className="text-white" size={24} />
        </div>
        <span className="text-xl font-bold text-slate-900 tracking-tight">Trendcast</span>
      </div>

      <nav className="flex-1 space-y-2">
        {path.map((item) => {
          const isActive = location === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <a className={`
                flex items-center justify-between px-4 py-3.5 rounded-2xl transition-all duration-200 group
                ${isActive 
                  ? "bg-indigo-50 text-indigo-600 shadow-sm" 
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"}
              `}>
                <div className="flex items-center gap-3">
                  <item.icon size={20} className={isActive ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600"} />
                  <span className="font-semibold text-[15px]">{item.label}</span>
                </div>
                {isActive && <div className="w-1.5 h-1.5 rounded-full bg-indigo-600" />}
              </a>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6 border-t border-slate-50">
        {!user ? (
          <button 
            onClick={onLoginClick}
            className="w-full flex items-center gap-3 px-4 py-3.5 text-slate-500 font-semibold hover:text-indigo-600 hover:bg-indigo-50 rounded-2xl transition-all group"
          >
            <LogIn size={20} className="group-hover:text-indigo-600" />
            <span>Login</span>
          </button>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-3 px-2">
              <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-600">
                <User size={20} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-slate-900 truncate">{user?.full_name || user?.email}</p>
                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
              </div>
            </div>
            <button 
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-4 py-3.5 text-slate-500 font-semibold hover:text-rose-600 hover:bg-rose-50 rounded-2xl transition-all group"
            >
              <LogOut size={20} className="group-hover:text-rose-600" />
              <span>Logout</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
