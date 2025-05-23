import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useAuth } from '../context/AuthContext'; // Import useAuth hook

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const ManagerDashboard = () => {
  const [revenueData, setRevenueData] = useState([]);
  const [userStats, setUserStats] = useState([]);
  const [loading, setLoading] = useState(true);
  // Thêm state cho năm được chọn
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState(currentYear);
  const { authState, loading: authLoading } = useAuth(); // Lấy thông tin từ context

  // Kiểm tra quyền 
  const isManager = authState.user && (authState.user.is_staff || authState.user.is_superuser);

  // Hàm lấy danh sách các năm có trong dữ liệu revenue
  const getAvailableYears = () => {
    const years = new Set();
    revenueData.forEach(item => {
      if (item.month && item.month.length >= 4) {
        years.add(Number(item.month.substring(0, 4)));
      }
    });
    return Array.from(years).sort((a, b) => b - a);
  };

  // Lọc dữ liệu theo năm được chọn
  const filteredRevenueData = revenueData.filter(item =>
    item.month && item.month.startsWith(selectedYear.toString())
  );
  // Nếu userStats cũng có dữ liệu theo năm, có thể lọc tương tự nếu cần


  useEffect(() => {
    // Fetch revenue and user statistics from backend
    const fetchDashboardData = async () => {
      try {
        // Lấy token từ localStorage
        const token = localStorage.getItem('access_token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const [revenueRes, userStatsRes] = await Promise.all([
          axios.get('http://127.0.0.1:8000/api/user/manager/revenue/', { headers }),
          axios.get('http://127.0.0.1:8000/api/user/manager/user-stats/', { headers }),
        ]);
        setRevenueData(revenueRes.data);
        setUserStats(userStatsRes.data);
        // Thêm log để kiểm tra dữ liệu lấy về từ API
        console.log('Revenue Data:', revenueRes.data);
        console.log('User Stats:', userStatsRes.data);
      } catch (error) {
        // handle error
        setRevenueData([]);
        setUserStats([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (authLoading) {
    return <div>Đang tải thông tin người dùng...</div>;
  }

  if (!isManager) {
    return (
      <div style={{ padding: '32px', textAlign: 'center' }}>
        <h2>Bạn không có quyền truy cập trang này</h2>
        <p>Tính năng này chỉ dành cho quản lý. Vui lòng đăng nhập với tài khoản quản lý để tiếp tục.</p>
        <button 
          onClick={() => window.location.href = '/'}
          style={{ padding: '8px 16px', background: '#3498db', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '20px' }}
        >
          Quay lại trang chủ
        </button>
      </div>
    );
  }

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div style={{ padding: '32px' }}>
      <h2>Manager Dashboard</h2>
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <button
          style={{ padding: '8px 16px', fontWeight: 'bold', background: '#1976d2', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
          onClick={() => window.location.href = '/manager/orders'}
        >
          Xem danh sách đơn hàng
        </button>
        <button
          style={{ padding: '8px 16px', fontWeight: 'bold', background: '#2ecc71', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}
          onClick={() => window.location.href = '/admin/chat'}
        >
          Quản lý tin nhắn hỗ trợ
        </button>
      </div>
      <div style={{ marginBottom: 40 }}>
        <h3>Revenue (Last 12 Months)</h3>
        <div style={{ marginBottom: 16 }}>
          <label>Chọn năm: </label>
          <select
            value={selectedYear}
            onChange={e => setSelectedYear(Number(e.target.value))}
          >
            {getAvailableYears().map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={filteredRevenueData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" fill="#8884d8" name="Revenue" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div>
        <h3>User Statistics</h3>
        <ResponsiveContainer width="50%" height={300}>
          <PieChart>
            <Pie
              data={userStats}
              dataKey="count"
              nameKey="role"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label
            >
              {userStats.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ManagerDashboard;
