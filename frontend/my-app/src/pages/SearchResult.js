import React, { useEffect, useState, useContext } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import { CartContext } from "../context/CartContext";

const CLOUDINARY_BASE_URL = "https://res.cloudinary.com/dtubffjwu/";

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const SearchResult = () => {
  const query = useQuery();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const searchTerm = query.get("q") || "";
  const { addToCart } = useContext(CartContext);

  useEffect(() => {
    if (!searchTerm) return;
    setLoading(true);
    axios
      .get(`http://127.0.0.1:8000/api/dishes/?search=${encodeURIComponent(searchTerm)}`)
      .then((res) => {
        setResults(res.data);
        setError("");
      })
      .catch(() => setError("Có lỗi xảy ra khi tìm kiếm"))
      .finally(() => setLoading(false));
  }, [searchTerm]);

  return (
    <div className="container mt-4">
      <h2>Kết quả tìm kiếm cho: <em>{searchTerm}</em></h2>
      {loading && <p>Đang tải...</p>}
      {error && <div className="alert alert-danger">{error}</div>}
      {!loading && !error && results.length === 0 && (
        <div className="alert alert-warning">Không tìm thấy kết quả phù hợp.</div>
      )}
      <div className="row">
        {results.map((dish) => (
          <div className="col-md-4 mb-3" key={dish.id}>
            <div className="card h-100">
              {/* Xử lý đường dẫn ảnh giống FoodItem */}
              <img
                src={dish.url_img && dish.url_img.startsWith('http') ? dish.url_img : CLOUDINARY_BASE_URL + (dish.url_img || '')}
                className="card-img-top"
                alt={dish.name}
                style={{ maxHeight: 180, objectFit: 'cover', background: '#f1f2f3' }}
              />
              <div className="card-body">
                <h5 className="card-title">{dish.name}</h5>
                <p className="card-text">{dish.description}</p>
                <p className="card-text"><strong>Giá:</strong> {dish.price} VNĐ</p>
                <button
                  className="btn btn-primary mt-2"
                  onClick={() => addToCart(dish.id)}
                >
                  <i className="fa fa-shopping-cart mr-1"></i> Thêm vào giỏ hàng
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResult;
