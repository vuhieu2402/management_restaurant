// import React, { useContext } from "react";
// import { CartContext } from "../context/CartContext";


// const CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dtubffjwu/";

// const Cart = () => {
//   const { cartItems, removeFromCart, updateQuantity } = useContext(CartContext);

//   return (
//     <div className="container">
//       <h2>Shopping Cart</h2>
//       <table className="table">
//         <thead>
//           <tr>
//             <th>Product</th>
//             <th>Quantity</th>
//             <th className="text-center">Price</th>
//             <th className="text-center">Total</th>
//             <th>Action</th>
//           </tr>
//         </thead>
//         <tbody>
//           {Array.isArray(cartItems) && cartItems.length > 0 ? (
//             cartItems.map((item) => {
//               const dish = item.dish || {}; // Đảm bảo dish luôn là object
//               const price = parseFloat(dish.price) || 0;   // Chuyển đổi giá thành số
//               const total = price * item.quantity; // Tính tổng


//               const imageUrl = dish.url_img.startsWith("http") 
//               ? dish.url_img 
//               : CLOUDINARY_BASE_URL + dish.url_img;

//               return (
//                 <tr key={item.id}>
//                   <td className="col-sm-8 col-md-6">
//                     <div className="media">
//                       <a className="thumbnail pull-left" href="#">
//                         <img
//                           className="media-object"
//                           src={imageUrl}
//                           alt={dish.name}
//                           style={{ width: "72px", height: "72px" }}
//                         />
//                       </a>
//                       <div className="media-body">
//                         <h4 className="media-heading">
//                           <a href="#">{dish.name || "Unknown"}</a>
//                         </h4>
                
//                         <span>Status: </span>
//                         {dish.in_stock ? (
//                           <span className="text-success"><strong>In Stock</strong></span>
//                         ) : (
//                           <span className="text-danger"><strong>Out of Stock</strong></span>
//                         )}
//                       </div>
//                     </div>
//                   </td>
                  
//                   <td>
//                     <button className="btn btn-secondary btn-sm" onClick={() => updateQuantity(dish.id, item.quantity - 1)}>
//                       -
//                     </button>
//                     <span className="mx-2">{item.quantity}</span>
//                     <button className="btn btn-secondary btn-sm" onClick={() => updateQuantity(dish.id, item.quantity + 1)}>
//                       +
//                     </button>
//                   </td>
//                   <td className="text-center">${price.toFixed(2)}</td>
//                   <td className="text-center">${total.toFixed(2)}</td>
//                   <td>
//                     <button className="btn btn-danger" onClick={() => removeFromCart(dish.id)}>
//                       Remove
//                     </button>
//                   </td>
//                 </tr>
//               );
//             })
//           ) : (
//             <tr>
//               <td colSpan="5" className="text-center">Your cart is empty.</td>
//             </tr>
//           )}
//         </tbody>
//       </table>
//     </div>
//   );
// };

// export default Cart;




import React, { useContext, useState } from "react";
import { CartContext } from "../context/CartContext";

const CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dtubffjwu/";

const Cart = () => {
  const { cartItems, removeFromCart, updateQuantity } = useContext(CartContext);
  const [selectedItems, setSelectedItems] = useState([]);

  // Xử lý chọn món ăn
  const toggleSelectItem = (dishId) => {
    setSelectedItems((prevSelected) =>
      prevSelected.includes(dishId)
        ? prevSelected.filter((id) => id !== dishId)
        : [...prevSelected, dishId]
    );
  };

  // Tính toán tổng tiền của các món đã chọn
  const selectedCartItems = cartItems.filter((item) => selectedItems.includes(item.dish.id));
  const subtotal = selectedCartItems.reduce((sum, item) => sum + item.dish.price * item.quantity, 0);
  const shippingCost = selectedCartItems.length > 0 ? 5 : 0; // Ví dụ phí ship $5 nếu có ít nhất 1 món
  const grandTotal = subtotal + shippingCost;

  return (
    <div className="container">
      <h2>Shopping Cart</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Select</th>
            <th>Product</th>
            <th>Quantity</th>
            <th className="text-center">Price</th>
            <th className="text-center">Total</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(cartItems) && cartItems.length > 0 ? (
            cartItems.map((item) => {
              const dish = item.dish || {};
              const price = parseFloat(dish.price) || 0;
              const total = price * item.quantity;
              const imageUrl = dish.url_img.startsWith("http")
                ? dish.url_img
                : CLOUDINARY_BASE_URL + dish.url_img;

              return (
                <tr key={item.id}>
                  {/* Checkbox chọn món */}
                  <td>
                    <input
                      type="checkbox"
                      checked={selectedItems.includes(dish.id)}
                      onChange={() => toggleSelectItem(dish.id)}
                    />
                  </td>

                  {/* Cột Product */}
                  <td className="col-sm-6 col-md-4">
                    <div className="media">
                      <a className="thumbnail pull-left" href="#">
                        <img className="media-object" src={imageUrl} alt={dish.name} style={{ width: "72px", height: "72px" }} />
                      </a>
                      <div className="media-body">
                        <h4 className="media-heading"><a href="#">{dish.name || "Unknown"}</a></h4>
                        <h5 className="media-heading">by <a href="#">Brand name</a></h5>
                        <span>Status: </span>
                        {dish.in_stock ? (
                          <span className="text-success"><strong>In Stock</strong></span>
                        ) : (
                          <span className="text-danger"><strong>Out of Stock</strong></span>
                        )}
                      </div>
                    </div>
                  </td>

                  {/* Cột số lượng với nút +/- */}
                  <td>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => updateQuantity(dish.id, item.quantity - 1)}
                      disabled={item.quantity <= 1}
                    >
                      -
                    </button>
                    <span className="mx-2">{item.quantity}</span>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => updateQuantity(dish.id, item.quantity + 1)}
                      disabled={!dish.in_stock}
                    >
                      +
                    </button>
                  </td>

                  {/* Giá & Tổng tiền */}
                  <td className="text-center">${price.toFixed(2)}</td>
                  <td className="text-center">${total.toFixed(2)}</td>

                  {/* Nút xóa */}
                  <td>
                    <button className="btn btn-danger" onClick={() => removeFromCart(dish.id)}>
                      Remove
                    </button>
                  </td>
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan="6" className="text-center">Your cart is empty.</td>
            </tr>
          )}
        </tbody>

        {/* Tổng tiền thanh toán */}
        {cartItems.length > 0 && (
          <tfoot>
            <tr>
              <td colSpan="3"></td>
              <td><h5>Subtotal</h5></td>
              <td className="text-right"><h5><strong>${subtotal.toFixed(2)}</strong></h5></td>
            </tr>
            <tr>
              <td colSpan="3"></td>
              <td><h5>Estimated shipping</h5></td>
              <td className="text-right"><h5><strong>${shippingCost.toFixed(2)}</strong></h5></td>
            </tr>
            <tr>
              <td colSpan="3"></td>
              <td><h3>Total</h3></td>
              <td className="text-right"><h3><strong>${grandTotal.toFixed(2)}</strong></h3></td>
            </tr>
            <tr>
              <td colSpan="3"></td>
              <td>
                <a href="/" className="btn btn-default">
                  <span className="glyphicon glyphicon-shopping-cart"></span> Continue Shopping
                </a>
              </td>
              <td>
                <a href="/checkout" className="btn btn-success">
                  Checkout <span className="glyphicon glyphicon-play"></span>
                </a>
              </td>
              <td>
                <a href="/order-history" className="btn btn-default">
                  <span className="glyphicon glyphicon-time"></span> Order History
                </a>
              </td>
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
};

export default Cart;
