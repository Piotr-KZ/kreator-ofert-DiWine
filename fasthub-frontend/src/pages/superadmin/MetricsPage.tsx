import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import { superadminApi } from "../../api/superadmin";
import { SectionCard, StatusBadge } from "@/components/ui";

const COLORS = ["#4F46E5", "#10B981", "#F59E0B", "#EF4444"];

export default function MetricsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<any>(null);
  const [recentUsers, setRecentUsers] = useState<any[]>([]);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, usersRes] = await Promise.all([
        superadminApi.getMetrics(),
        superadminApi.getRecentUsers(),
      ]);
      setStats(statsRes.data);
      setRecentUsers(usersRes.data || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load metrics");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl">
        <p className="font-medium">Error</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  const growthData = [
    { month: "Jan", users: 400, orgs: 240, revenue: 2400 },
    { month: "Feb", users: 300, orgs: 139, revenue: 2210 },
    { month: "Mar", users: 200, orgs: 980, revenue: 2290 },
    { month: "Apr", users: 278, orgs: 390, revenue: 2000 },
    { month: "May", users: 189, orgs: 480, revenue: 2181 },
    { month: "Jun", users: 239, orgs: 380, revenue: 2500 },
  ];

  const planDistribution = [
    { name: "Free", value: 400 },
    { name: "Pro", value: 300 },
    { name: "Enterprise", value: 100 },
  ];

  const revenueUp = stats?.revenue_this_month > stats?.revenue_last_month;
  const revenuePercent = stats?.revenue_last_month
    ? ((stats.revenue_this_month - stats.revenue_last_month) / stats.revenue_last_month * 100).toFixed(1)
    : 0;

  const statCards = [
    {
      label: "Total Users",
      value: stats?.total_users || 0,
      color: "text-green-600",
      icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
    },
    {
      label: "Organizations",
      value: stats?.total_organizations || 0,
      color: "text-indigo-600",
      icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
    },
    {
      label: "Active Subscriptions",
      value: `${stats?.active_subscriptions || 0} / ${stats?.total_subscriptions || 0}`,
      color: "text-red-600",
      icon: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z",
    },
    {
      label: "Revenue This Month",
      value: `${stats?.revenue_this_month || 0} PLN`,
      color: revenueUp ? "text-green-600" : "text-red-600",
      sub: `${revenueUp ? "+" : ""}${revenuePercent}% from last month`,
      icon: revenueUp
        ? "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
        : "M13 17h8m0 0V9m0 8l-8-8-4 4-6-6",
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900">System Metrics</h1>
      <p className="text-sm text-gray-500 mt-1 mb-6">
        Overview of system-wide statistics and performance
      </p>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {statCards.map((card) => (
          <div key={card.label} className="bg-white border-2 border-gray-200 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-2">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={card.icon} />
              </svg>
              <span className="text-sm text-gray-500">{card.label}</span>
            </div>
            <p className={`text-2xl font-bold ${card.color}`}>{card.value}</p>
            {card.sub && <p className="text-xs text-gray-400 mt-1">{card.sub}</p>}
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <SectionCard title="Growth Trends" className="lg:col-span-2">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="users" stroke="#4F46E5" name="Users" />
              <Line type="monotone" dataKey="orgs" stroke="#10B981" name="Organizations" />
            </LineChart>
          </ResponsiveContainer>
        </SectionCard>

        <SectionCard title="Plan Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={planDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {planDistribution.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </SectionCard>
      </div>

      {/* Revenue Chart */}
      <SectionCard title="Monthly Revenue" className="mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={growthData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" fill="#10B981" name="Revenue (PLN)" />
          </BarChart>
        </ResponsiveContainer>
      </SectionCard>

      {/* Recent Users */}
      <SectionCard title="Recent Users">
        <div className="overflow-x-auto -mx-6 -mb-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-3 font-medium text-gray-600">User</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Role</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Created</th>
              </tr>
            </thead>
            <tbody>
              {recentUsers.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-400">
                    No recent users
                  </td>
                </tr>
              ) : (
                recentUsers.map((u: any) => (
                  <tr key={u.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{u.full_name || "N/A"}</div>
                      <div className="text-xs text-gray-400">{u.email}</div>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant="info">{u.role?.toUpperCase()}</StatusBadge>
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge variant={u.is_active ? "success" : "error"}>
                        {u.is_active ? "Active" : "Inactive"}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-3 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  );
}
