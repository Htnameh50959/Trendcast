import React, { useState, useEffect } from "react";
import { apiCall } from "../utils/api";
import { 
  TrendingUp, 
  DollarSign, 
  ShoppingCart, 
  Package, 
  ArrowUpRight, 
  ArrowDownRight,
  Loader2
} from "lucide-react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import "./dashboard.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSales: 0,
    totalOrders: 0,
    avgOrderValue: 0,
    growth: 0,
  });
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const data = await apiCall("/api/sales");
      console.log("Dashboard data fetched:", data);
      
      if (data && Array.isArray(data) && data.length > 0) {
        // Calculate basic stats
        const totalSales = data.reduce((sum, item) => sum + (Number(item.weekly_sales || item.Weekly_Sales) || 0), 0);
        const totalOrders = data.length;
        const avgOrderValue = totalSales / totalOrders;
        
        setStats({
          totalSales: totalSales.toLocaleString(undefined, { maximumFractionDigits: 2 }),
          totalOrders: totalOrders.toLocaleString(),
          avgOrderValue: avgOrderValue.toLocaleString(undefined, { maximumFractionDigits: 2 }),
          growth: 12.5 // Placeholder growth
        });

        // Prepare chart data (group by date)
        const sortedData = [...data].sort((a, b) => new Date(a.date || a.Date) - new Date(b.date || b.Date)).slice(-12);
        setChartData({
          labels: sortedData.map(item => item.date || item.Date),
          datasets: [
            {
              label: 'Recent Sales',
              data: sortedData.map(item => item.weekly_sales || item.Weekly_Sales),
              borderColor: 'rgb(99, 102, 241)',
              backgroundColor: 'rgba(99, 102, 241, 0.5)',
              tension: 0.3,
            },
          ],
        });
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      setLoading(false);
    }
  };

  if (loading && false) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="dashboard-container bg-[#f8f9fc] min-h-screen p-6">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard Overview</h1>
          <p className="text-slate-500">Welcome back! Here's what's happening with your sales.</p>
        </div>
        <div className="flex items-center gap-4">
          <button className="p-2 text-slate-400 hover:text-slate-600 relative">
            <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></div>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg>
          </button>
          <div className="w-10 h-10 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center font-semibold border-2 border-white shadow-sm">
            T
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <DollarSign size={24} />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Total Sales</p>
            <h3 className="text-2xl font-bold text-slate-900">₹{stats.totalSales}</h3>
            <div className="flex items-center text-xs font-medium text-emerald-500 mt-1">
              <ArrowUpRight size={14} className="mr-1" /> 12%
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <ShoppingCart size={24} />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Total Orders</p>
            <h3 className="text-2xl font-bold text-slate-900">{stats.totalOrders}</h3>
            <div className="flex items-center text-xs font-medium text-emerald-500 mt-1">
              <ArrowUpRight size={14} className="mr-1" /> 8%
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
            <Package size={24} />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Avg. Order Value</p>
            <h3 className="text-2xl font-bold text-slate-900">₹{stats.avgOrderValue}</h3>
            <div className="flex items-center text-xs font-medium text-rose-500 mt-1">
              <ArrowDownRight size={14} className="mr-1" /> 3%
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <TrendingUp size={24} />
          </div>
          <div>
            <p className="text-sm text-slate-500 font-medium">Growth Rate</p>
            <h3 className="text-2xl font-bold text-slate-900">{stats.growth}%</h3>
            <div className="flex items-center text-xs font-medium text-emerald-500 mt-1">
              <ArrowUpRight size={14} className="mr-1" /> 2%
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 relative overflow-hidden">
        <div className="flex justify-between items-center mb-8">
          <h3 className="text-lg font-bold text-slate-900">Sales Trend (Last 12 Records)</h3>
          <div className="flex bg-slate-50 p-1 rounded-xl">
            <button className="px-4 py-1.5 text-sm font-semibold rounded-lg bg-white text-indigo-600 shadow-sm">Last 12 Records</button>
            <button className="px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-700">Last 6 Months</button>
            <button className="px-4 py-1.5 text-sm font-medium text-slate-500 hover:text-slate-700">Yearly</button>
          </div>
        </div>

        <div className="h-[350px] w-full relative">
          {chartData ? (
            <Line 
              data={chartData} 
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  y: { 
                    beginAtZero: true,
                    grid: { color: '#f1f5f9' },
                    ticks: { color: '#94a3b8', font: { size: 11 } }
                  },
                  x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', font: { size: 11 } }
                  }
                }
              }} 
            />
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 mb-4 opacity-20">
                <TrendingUp size={96} className="text-indigo-200" />
              </div>
              <h4 className="text-lg font-bold text-slate-900 mb-2">No sales data available yet</h4>
              <p className="text-slate-500 mb-6 max-w-xs">Add sales records to see trends and insights here</p>
              <button 
                onClick={() => window.location.hash = "/Sales"}
                className="bg-indigo-600 text-white px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all flex items-center gap-2"
              >
                <span>+</span> Add Sales Data
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
