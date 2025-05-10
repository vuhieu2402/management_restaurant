import React, { useEffect, useState } from "react";
import axios from "axios";

const OrderHistory = () => {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/order/history/", {
          headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        });
        setOrders(response.data);
      } catch (error) {
        console.error("Error fetching orders:", error);
      }
    };
    

    fetchOrders();
  }, []);

  return (
    <div className="container">
      <h2>Order History</h2>
      {orders.map((order) => (
        <React.Fragment key={order.id}>
          <div className="order">
            <p>Status: {order.status ? "Đã thanh toán" : "Chưa thanh toán"}</p>
            <p>Total: {order.total_price} VNĐ</p>
            <p>Ngày đặt: {new Date(order.order_date).toLocaleDateString('vi-VN')}</p>
            <p>Địa chỉ: {order.address}</p>
          </div>
          <hr style={{border: '1.5px solid #aaa', margin: '18px 0'}} />
        </React.Fragment>
      ))}
    </div>
  );
};

export default OrderHistory;
