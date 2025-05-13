import React, { useEffect, useState } from 'react';
import axios from 'axios';
import config from '../config';
import { useAuth } from '../context/AuthContext'; // Import useAuth hook

const ManagerOrders = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [year, setYear] = useState('');
  const [month, setMonth] = useState('');
  const [error, setError] = useState('');
  // Thêm state cho phân trang
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalOrders, setTotalOrders] = useState(0);
  // Thêm state cho export báo cáo
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(null);
  const [exportFileId, setExportFileId] = useState(null);
  const { authState, loading: authLoading } = useAuth(); // Lấy thông tin từ context

  // Kiểm tra quyền
  const isManager = authState.user && (authState.user.is_staff || authState.user.is_superuser);

  // Lấy năm hiện tại
  const currentYear = new Date().getFullYear();
  // Danh sách tháng
  const months = [
    '', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'
  ];

  const fetchOrders = async () => {
    setLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      let url = `${config.apiUrl}/order/manager-list/`;
      const params = [];
      if (year) params.push(`year=${year}`);
      if (month) params.push(`month=${month}`);
      if (page) params.push(`page=${page}`);
      if (params.length > 0) url += '?' + params.join('&');
      console.log('Calling API:', url);
      const res = await axios.get(url, { headers });
      console.log('API response:', res.data);
      
      // Cập nhật xử lý dữ liệu cho phù hợp với response từ Django DRF
      setOrders(res.data.results || []);
      // Tính tổng số trang dựa trên count và page_size (mặc định 10)
      const pageSize = 10;
      const totalPagesCount = Math.ceil((res.data.count || 0) / pageSize);
      setTotalPages(totalPagesCount);
      setTotalOrders(res.data.count || 0);
    } catch (err) {
      console.error('Error fetching orders:', err);
      setError('Lỗi khi lấy danh sách đơn hàng!');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  // Hàm xuất báo cáo
  const exportReport = async () => {
    setExporting(true);
    setExportSuccess(null);
    setExportFileId(null);
    try {
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const data = {};
      if (year) data.year = year;
      if (month) data.month = month;
      
      const response = await axios.post(`${config.apiUrl}/exports/files/export_orders/`, data, { headers });
      console.log('Export response:', response.data);
      
      setExportSuccess(true);
      setExportFileId(response.data.id);
    } catch (err) {
      console.error('Error exporting report:', err);
      setExportSuccess(false);
    } finally {
      setExporting(false);
    }
  };

  // Hàm tải xuống báo cáo
  const downloadReport = async () => {
    if (!exportFileId) return;
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Đảm bảo token được định dạng đúng
      if (!token) {
        alert('Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn!');
        return;
      }
      
      const headers = { Authorization: `Bearer ${token}` };
      
      // Gọi API kiểm tra trạng thái file
      const checkResponse = await axios.get(`${config.apiUrl}/exports/files/${exportFileId}/`, { headers });
      
      if (checkResponse.data.status !== 'completed') {
        alert('Báo cáo đang được tạo, vui lòng đợi...');
        return;
      }
      
      console.log('Downloading file with token:', token);
      
      // Thay đổi cách tải file - sử dụng axios trực tiếp với token xác thực
      const downloadUrl = `${config.apiUrl}/exports/files/${exportFileId}/download/`;
      console.log('Download URL:', downloadUrl);
      
      axios({
        url: downloadUrl,
        method: 'GET',
        responseType: 'blob',
        headers: headers
      })
      .then(response => {
        console.log('Download response:', response);
        
        // Tạo blob URL từ response data
        const url = window.URL.createObjectURL(new Blob([response.data]));
        
        // Tạo một thẻ a ẩn để tải xuống
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        
        // Lấy tên file từ response header hoặc dùng tên mặc định
        const contentDisposition = response.headers['content-disposition'];
        let filename = checkResponse.data.file_name || `order_report_${new Date().getTime()}.csv`;
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="(.+)"/);
          if (filenameMatch && filenameMatch.length === 2) {
            filename = filenameMatch[1];
          }
        }
        
        console.log('Filename:', filename);
        a.download = filename;
        
        // Thêm thẻ a vào body, nhấp vào nó và sau đó xóa nó
        document.body.appendChild(a);
        a.click();
        
        // Xóa thẻ và giải phóng Object URL
        window.setTimeout(() => {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 100);
      })
      .catch(err => {
        console.error('Error downloading file:', err);
        alert('Không thể tải xuống báo cáo. Vui lòng thử lại sau.');
      });
      
    } catch (err) {
      console.error('Error downloading report:', err);
      alert('Không thể tải xuống báo cáo. Vui lòng thử lại sau.');
    }
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line
  }, [year, month, page]);

  // Lấy danh sách năm từ dữ liệu đơn hàng (nếu có), mặc định là 3 năm gần nhất
  const getYearOptions = () => {
    const now = new Date().getFullYear();
    return ['', now, now - 1, now - 2];
  };

  // Render kiểm tra quyền truy cập
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

  return (
    <div style={{ padding: 24 }}>
      <h2>Danh sách đơn hàng đã bán</h2>
      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center' }}>
        <div>
          <label>Chọn năm: </label>
          <select value={year} onChange={e => setYear(e.target.value)}>
            {getYearOptions().map(y => (
              <option key={y} value={y}>{y === '' ? 'Tất cả' : y}</option>
            ))}
          </select>
          <label style={{ marginLeft: 16 }}>Chọn tháng: </label>
          <select value={month} onChange={e => setMonth(e.target.value)}>
            {months.map((m, idx) => (
              <option key={m} value={m}>{m === '' ? 'Tất cả' : m}</option>
            ))}
          </select>
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <button 
            onClick={exportReport} 
            disabled={exporting}
            style={{ 
              padding: '8px 16px', 
              backgroundColor: '#4CAF50', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: exporting ? 'not-allowed' : 'pointer' 
            }}
          >
            {exporting ? 'Đang xuất...' : 'Xuất báo cáo CSV'}
          </button>
          
          {exportSuccess === true && (
            <button 
              onClick={downloadReport}
              style={{ 
                marginLeft: '8px',
                padding: '8px 16px', 
                backgroundColor: '#2196F3', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer' 
              }}
            >
              Tải xuống báo cáo
            </button>
          )}
        </div>
      </div>
      
      {exportSuccess === true && (
        <div style={{ marginBottom: 16, padding: 10, backgroundColor: '#dff0d8', color: '#3c763d', borderRadius: 4 }}>
          Báo cáo đã được tạo thành công! Nhấn "Tải xuống báo cáo" để tải xuống.
        </div>
      )}
      
      {exportSuccess === false && (
        <div style={{ marginBottom: 16, padding: 10, backgroundColor: '#f2dede', color: '#a94442', borderRadius: 4 }}>
          Có lỗi xảy ra khi tạo báo cáo. Vui lòng thử lại.
        </div>
      )}
      
      {loading ? (
        <div>Đang tải dữ liệu...</div>
      ) : error ? (
        <div style={{ color: 'red' }}>{error}</div>
      ) : (
        <>
          <div style={{ marginBottom: 8, fontWeight: 'bold' }}>
            Tổng số đơn hàng: {totalOrders}
          </div>
          <table border="1" cellPadding="8" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Ngày đặt</th>
                <th>Địa chỉ</th>
                <th>Tổng tiền</th>
                <th>Trạng thái</th>
                <th>Chi tiết món</th>
              </tr>
            </thead>
            <tbody>
              {orders.length === 0 ? (
                <tr><td colSpan="6">Không có đơn hàng nào.</td></tr>
              ) : orders.map(order => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{order.order_date ? new Date(order.order_date).toLocaleString() : ''}</td>
                  <td>{order.address}</td>
                  <td>{order.total_price}</td>
                  <td>{order.status ? 'Đã thanh toán' : 'Chưa thanh toán'}</td>
                  <td>
                    <ul style={{ paddingLeft: 16 }}>
                      {order.details && order.details.length > 0 ? order.details.map((d, idx) => (
                        <li key={idx}>{d.dish_name} x {d.quantity} ({d.unit_price}₫)</li>
                      )) : <li>Không có</li>}
                    </ul>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* Phân trang */}
          <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 8 }}>
            <button onClick={() => setPage(page - 1)} disabled={page === 1}>Trước</button>
            <span>Trang {page} / {totalPages}</span>
            <button onClick={() => setPage(page + 1)} disabled={page === totalPages}>Sau</button>
          </div>
        </>
      )}
    </div>
  );
};

export default ManagerOrders;
