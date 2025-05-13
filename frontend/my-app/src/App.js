// import React from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import Header from "./components/Header";
import AboutSection from "./components/AboutSection";
import FoodSection from "./components/FoodSection";
import BookSection from "./components/BookSection";
import ClientSection from "./components/ClientSection";
import OfferSection from "./components/OfferSection";
import Footer from "./components/Footer";
import Cart from "./components/Cart";
import Login from "./components/Auth/Login";
import ForgotPassword from "./components/Auth/ForgotPassword";
import ResetPassword from "./components/Auth/ResetPassword";
import Checkout from "./components/Checkout";  // Thêm tuyến đường Checkout
import OrderHistory from "./components/OrderHistory";  // Thêm tuyến đường lịch sử đơn hàng
import BookTablePage from "./pages/BookTablePage";
import Profile from "./pages/Profile";
import SearchResult from "./pages/SearchResult";
import ManagerDashboard from "./pages/ManagerDashboard";
import ManagerOrders from "./pages/ManagerOrders";
import ChatBot from './components/ChatBot';
import LiveChatWidget from './components/LiveChatWidget';
import LiveChatAdmin from './components/LiveChatAdmin';
import { useEffect } from 'react';
import axios from 'axios';

// Thiết lập axios interceptor
// Dùng một hàm riêng thay vì trong phần render
const setupAxiosInterceptors = () => {
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // Kiểm tra và chuẩn hóa URL để tránh trùng lặp /api/
      if (config.url && config.url.includes('/api/api/')) {
        config.url = config.url.replace('/api/api/', '/api/');
        console.log('Normalized URL:', config.url);
      }
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );
  
  // Thêm interceptor để xử lý lỗi 401 (Unauthorized)
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        // Xóa token và chuyển hướng đến trang đăng nhập
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        if (!window.location.pathname.includes('/auth')) {
          window.location.href = '/auth';
        }
      }
      return Promise.reject(error);
    }
  );
};

function App() {
  const location = useLocation();
  
  // Kiểm tra xem có phải trang quản lý không
  const isManagerPage = location.pathname.includes('/manager') || location.pathname.includes('/admin');
  
  // Thiết lập interceptor khi app khởi chạy
  useEffect(() => {
    setupAxiosInterceptors();
  }, []);
  
  return (
    <AuthProvider>
      <CartProvider>
        <Routes>
          <Route path="/" element={
            <>
              <Header />
              <OfferSection />
              <FoodSection />
              <AboutSection />
              <BookSection />
              <ClientSection />
              <Footer />
            </>
          } />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />  {/* Thêm tuyến đường */}
          <Route path="/order-history" element={<OrderHistory />} /> {/* Thêm tuyến đường */}
          <Route path="/auth" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password/:uidb64/:token" element={<ResetPassword />} />
          <Route path="/book-table" element={<BookTablePage />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/search" element={<SearchResult />} />
          <Route path="/manager" element={<ManagerDashboard />} />
          <Route path="/manager/orders" element={<ManagerOrders />} />
          <Route path="/admin/chat" element={<LiveChatAdmin />} />
        </Routes>
        {/* Đặt cả hai component với z-index khác nhau để tránh đè lên nhau */}
        {!isManagerPage && <ChatBot />}
        {!isManagerPage && <LiveChatWidget />}
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
