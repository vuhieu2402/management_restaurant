// import React from "react";
import { Routes, Route } from "react-router-dom";
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

function App() {
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
        </Routes>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
