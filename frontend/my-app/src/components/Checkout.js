import React, { useContext, useState } from "react";
import { CartContext } from "../context/CartContext";
import axios from "axios";


const CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dtubffjwu/";
const getImageUrl = (url_img) => {
  if (!url_img) return "https://via.placeholder.com/50"; // Ảnh mặc định nếu không có URL
  return url_img.startsWith("http") ? url_img : CLOUDINARY_BASE_URL + url_img;
};

const Checkout = () => {
  const { cartItems, selectedItems, setSelectedItems } = useContext(CartContext);
  const selectedCartItems = cartItems.filter(item => selectedItems.includes(item.dish.id));

  const [shippingInfo, setShippingInfo] = useState({
    name: "",
    phone: "",
    address: "",
    paymentMethod: "cod", // Default: Thanh toán khi nhận hàng
  });

  // Tính toán tổng tiền
  const subtotal = selectedCartItems.reduce((sum, item) => sum + item.dish.price * item.quantity, 0);
  const shippingCost = selectedCartItems.length > 0 ? 5 : 0;
  const grandTotal = subtotal + shippingCost;

  const handleInputChange = (e) => {
    setShippingInfo({ ...shippingInfo, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    const orderData = {
      customer_name: shippingInfo.name,
      phone: shippingInfo.phone,
      address: shippingInfo.address,
      payment_method: shippingInfo.paymentMethod,
      items: selectedCartItems.map((item) => ({
        dish_id: item.dish.id,
        quantity: item.quantity,
      })),
      total_price: grandTotal,
    };
  
    // ✅ Lấy token JWT từ localStorage (hoặc context API)
    const token = localStorage.getItem("access_token");

    console.log("Token được lấy từ localStorage:", token); // ✅ Debug xem có token không

    if (!token) {
      alert("Bạn chưa đăng nhập. Vui lòng đăng nhập để đặt hàng!");
      return;
    }
    try {
      const response = await axios.post("http://127.0.0.1:8000/api/order/place_order/", orderData, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });
    
      console.log("📩 Response status:", response.status);
      console.log("📩 Response data:", response.data);
    
      if (response.status === 201 || response.status === 200) {
        // Nếu chọn thanh toán online, gọi API VNPay
        if (shippingInfo.paymentMethod === "online") {
          try {
            const vnpayRes = await axios.post("http://127.0.0.1:8000/api/vnpay_payment/", {
              order_id: response.data.id || response.data.order_id, // tuỳ backend trả về
              amount: Math.round(grandTotal * 1000)
            }, {
              headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
              },
            });
            if (vnpayRes.data && vnpayRes.data.payment_url) {
              window.location.href = vnpayRes.data.payment_url;
              return;
            } else {
              alert("Không lấy được link thanh toán VNPay");
            }
          } catch (err) {
            alert("Lỗi khi khởi tạo thanh toán VNPay");
            return;
          }
        }
        // Nếu không phải online, xử lý như cũ
        alert("Đặt hàng thành công!");
        setSelectedItems([]); 
      } else {
        alert(`Lỗi đặt hàng: ${response.data.error || "Vui lòng thử lại."}`);
      }
      
    } catch (error) {
      console.error("🚨 Lỗi khi gửi đơn hàng:", error.response ? error.response.data : error);
      alert(`Đặt hàng thất bại: ${error.response ? error.response.data.error : "Không rõ lỗi."}`);
    }
    
  };
  

  return (
    <div className="container mt-5">
      <h2>Checkout</h2>
      <div className="row">
        {/* Danh sách sản phẩm */}
        <div className="col-md-6">
          <h4>Order Summary</h4>
          <ul className="list-group">
            {selectedCartItems.map((item) => (
              <li key={item.dish.id} className="list-group-item d-flex justify-content-between align-items-center">
                <img src={getImageUrl(item.dish.url_img)} alt={item.dish.name} style={{ width: "50px", height: "50px" }} />
                {item.dish.name} (x{item.quantity})
                <span>${(item.dish.price * item.quantity).toFixed(2)}</span>
              </li>
            ))}
          </ul>
          <h5 className="mt-3">Subtotal: ${subtotal.toFixed(2)}</h5>
          <h5>Shipping: ${shippingCost.toFixed(2)}</h5>
          <h4>Total: ${grandTotal.toFixed(2)}</h4>
        </div>

        {/* Form nhập thông tin */}
        <div className="col-md-6">
          <h4>Shipping Information</h4>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input type="text" className="form-control" name="name" value={shippingInfo.name} onChange={handleInputChange} required />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input type="text" className="form-control" name="phone" value={shippingInfo.phone} onChange={handleInputChange} required />
            </div>
            <div className="form-group">
              <label>Address</label>
              <input type="text" className="form-control" name="address" value={shippingInfo.address} onChange={handleInputChange} required />
            </div>

            {/* Chọn phương thức thanh toán */}
            <div className="form-group">
              <label>Payment Method</label>
              <select className="form-control" name="paymentMethod" value={shippingInfo.paymentMethod} onChange={handleInputChange}>
                <option value="cod">Cash on Delivery (COD)</option>
                <option value="online">Online Payment</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary btn-block mt-3">Place Order</button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
