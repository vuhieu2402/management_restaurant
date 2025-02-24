import React from "react";
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
import ForgotPassword from "./components/Auth/ForgotPassword";  // Thêm import
import ResetPassword from "./components/Auth/ResetPassword";    // Thêm import

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
          <Route path="/auth" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} /> 
          <Route path="/reset-password/:uidb64/:token" element={<ResetPassword />} />
        </Routes>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
