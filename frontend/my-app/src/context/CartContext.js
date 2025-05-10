// import { createContext, useState, useEffect } from "react";
// import axios from "axios";

// export const CartContext = createContext();

// export const CartProvider = ({ children }) => {
//   const [cartItems, setCartItems] = useState([]);
//   const [selectedItems, setSelectedItems] = useState([]);

//   // Hàm lấy token từ localStorage
//   const getAccessToken = () => localStorage.getItem("access_token");
//   const getRefreshToken = () => localStorage.getItem("refresh_token");

//   // Hàm refresh token khi access token hết hạn
//   const refreshAccessToken = async () => {
//     const refreshToken = getRefreshToken();
//     if (!refreshToken) {
//       console.warn("No refresh token found! User might need to log in again.");
//       return null;
//     }

//     try {
//       const response = await axios.post("http://127.0.0.1:8000/api/token/refresh/", {
//         refresh: refreshToken,
//       });

//       const newAccessToken = response.data.access;
//       localStorage.setItem("access_token", newAccessToken);
//       return newAccessToken;
//     } catch (error) {
//       console.error("Error refreshing token:", error.response?.data || error.message);
//       return null;
//     }
//   };

//   // Hàm gọi API có kiểm tra & làm mới access token
//   const authRequest = async (url, method = "get", data = null) => {
//     let token = getAccessToken();
//     if (!token) {
//       console.warn("No access token found!");
//       return null;
//     }

//     let headers = { Authorization: `Bearer ${token}` };

//     try {
//       const response = await axios({ url, method, data, headers });
//       return response.data;
//     } catch (error) {
//       if (error.response?.status === 401) {
//         console.warn("Access token expired, refreshing...");

//         // Refresh token
//         token = await refreshAccessToken();
//         if (!token) return null;

//         headers = { Authorization: `Bearer ${token}` };

//         try {
//           const response = await axios({ url, method, data, headers });
//           return response.data;
//         } catch (retryError) {
//           console.error("Error after retry:", retryError.response?.data || retryError.message);
//           return null;
//         }
//       } else {
//         console.error("API error:", error.response?.data || error.message);
//         return null;
//       }
//     }
//   };

//   // Hàm lấy giỏ hàng
//   const fetchCart = async () => {
//     const data = await authRequest("http://127.0.0.1:8000/api/cart/");
//     if (data) setCartItems(data.items || []);
//   };

//   // Hàm thêm sản phẩm vào giỏ hàng
//   const addToCart = async (dishId) => {
//     const success = await authRequest("http://127.0.0.1:8000/api/cart/add_to_cart/", "post", { dish_id: dishId, quantity: 1 });
//     if (success) fetchCart(); // Cập nhật giỏ hàng sau khi thêm món
//   };

//   const removeFromCart = async (dishId) => {
//     const success = await authRequest("http://127.0.0.1:8000/api/cart/remove_from_cart/", "post", { dish_id: dishId });
//     if (success) fetchCart(); // Cập nhật giỏ hàng sau khi xóa
//   };


//   const updateQuantity = async (dishId, quantity) => {
//     const success = await authRequest(
//       "http://127.0.0.1:8000/api/cart/update_quantity/",
//       "post",
//       { dish_id: dishId, quantity }
//     );
//     if (success) fetchCart(); // Cập nhật giỏ hàng sau khi thay đổi số lượng
//   };


//   useEffect(() => {
//     fetchCart();
//   }, []);

//   return (
//     <CartContext.Provider value={{ cartItems, addToCart, removeFromCart, updateQuantity }}>
//       {children}
//     </CartContext.Provider>
//   );
// };



import { createContext, useState, useEffect } from "react";
import axios from "axios";

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cartItems, setCartItems] = useState([]);
  const [selectedItems, setSelectedItems] = useState(
    JSON.parse(localStorage.getItem("selectedItems")) || []
  ); // Thêm selectedItems

  // Hàm lấy token từ localStorage
  const getAccessToken = () => localStorage.getItem("access_token");
  const getRefreshToken = () => localStorage.getItem("refresh_token");

  // Hàm refresh token khi access token hết hạn
  const refreshAccessToken = async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
      console.warn("No refresh token found! User might need to log in again.");
      return null;
    }

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/token/refresh/", {
        refresh: refreshToken,
      });

      const newAccessToken = response.data.access;
      localStorage.setItem("access_token", newAccessToken);
      return newAccessToken;
    } catch (error) {
      console.error("Error refreshing token:", error.response?.data || error.message);
      return null;
    }
  };

  // Hàm gọi API có kiểm tra & làm mới access token
  const authRequest = async (url, method = "get", data = null) => {
    let token = getAccessToken();
    if (!token) {
      console.warn("No access token found!");
      return null;
    }

    let headers = { Authorization: `Bearer ${token}` };

    try {
      const response = await axios({ url, method, data, headers });
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        console.warn("Access token expired, refreshing...");

        // Refresh token
        token = await refreshAccessToken();
        if (!token) return null;

        headers = { Authorization: `Bearer ${token}` };

        try {
          const response = await axios({ url, method, data, headers });
          return response.data;
        } catch (retryError) {
          console.error("Error after retry:", retryError.response?.data || retryError.message);
          return null;
        }
      } else {
        console.error("API error:", error.response?.data || error.message);
        return null;
      }
    }
  };

  useEffect(() => {
    localStorage.setItem("selectedItems", JSON.stringify(selectedItems));
  }, [selectedItems]); // Cập nhật mỗi khi thay đổi

  // Hàm lấy giỏ hàng
  const fetchCart = async () => {
    const data = await authRequest("http://127.0.0.1:8000/api/cart/");
    if (data) setCartItems(data.items || []);
  };

  useEffect(() => {
    fetchCart();
  }, []);

  // Hàm thêm sản phẩm vào giỏ hàng
  const addToCart = async (dishId) => {
    const success = await authRequest("http://127.0.0.1:8000/api/cart/add_to_cart/", "post", { dish_id: dishId, quantity: 1 });
    if (success) fetchCart();
  };

  const removeFromCart = async (dishId) => {
    const success = await authRequest("http://127.0.0.1:8000/api/cart/remove_from_cart/", "post", { dish_id: dishId });
    if (success) fetchCart();
  };

  const updateQuantity = async (dishId, quantity) => {
    const success = await authRequest(
      "http://127.0.0.1:8000/api/cart/update_quantity/",
      "post",
      { dish_id: dishId, quantity }
    );
    if (success) fetchCart();
  };

  useEffect(() => {
    fetchCart();
  }, []);

  return (
    <CartContext.Provider value={{ cartItems, selectedItems, setSelectedItems, addToCart, removeFromCart, updateQuantity }}>
      {children}
    </CartContext.Provider>
  );
};
