import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; 
import "bootstrap/dist/css/bootstrap.min.css";

import axios from "axios";
// import { useNavigate } from "react-router-dom";

const Header = () => {
  const { user, logout } = useContext(AuthContext);
const [searchTerm, setSearchTerm] = React.useState("");
const [suggestions, setSuggestions] = React.useState([]);
const [showSuggestions, setShowSuggestions] = React.useState(false);
const searchTimeout = React.useRef(null);

const handleSearchChange = (e) => {
  const value = e.target.value;
  setSearchTerm(value);
  if (searchTimeout.current) clearTimeout(searchTimeout.current);
  if (value.trim() === "") {
    setSuggestions([]);
    setShowSuggestions(false);
    return;
  }
  searchTimeout.current = setTimeout(async () => {
    try {
      // Gọi API lấy gợi ý
      const res = await axios.get(`http://127.0.0.1:8000/api/dishes/?search=${encodeURIComponent(value)}`);
      // Lọc lại trên frontend (nếu backend trả về quá nhiều)
      const keywords = value
        .toLowerCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .split(/\s+/)
        .filter(Boolean);
      const filtered = res.data.filter(item => {
        const name = item.name.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        return keywords.every(kw => name.includes(kw));
      });
      setSuggestions(filtered);
      setShowSuggestions(true);
    } catch (err) {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, 350); // debounce 350ms
};

const handleSuggestionClick = (item) => {
  setSearchTerm(item.name);
  setShowSuggestions(false);
  // Điều hướng đến trang kết quả tìm kiếm với query param q
  window.location.href = `/search?q=${encodeURIComponent(item.name)}`;
};

const handleSearchKeyDown = (e) => {
  if (e.key === "Enter") {
    setShowSuggestions(false);
    window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
  }
};

  const scrollToMenu = (e) => {
    e.preventDefault();
    const menuSection = document.getElementById('menu');
    if (menuSection) {
      menuSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToAbout = (e) => {
    e.preventDefault();
    const aboutSection = document.getElementById('about');
    if (aboutSection) {
      aboutSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="hero_area">
      <div className="bg-box">
        <img src="images/hero-bg.jpg" alt="Hero Background" />
      </div>

      <header className="header_section">
        <div className="container">
          <nav className="navbar navbar-expand-lg custom_nav-container">
            <Link className="navbar-brand" to="/">
              <span>Feane</span>
            </Link>

            <button
              className="navbar-toggler"
              type="button"
              data-toggle="collapse"
              data-target="#navbarSupportedContent"
              aria-controls="navbarSupportedContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className=""> </span>
            </button>

            <div className="collapse navbar-collapse" id="navbarSupportedContent">
              <ul className="navbar-nav mx-auto">
                <li className="nav-item active">
                  <Link className="nav-link" to="/">
                    Home <span className="sr-only">(current)</span>
                  </Link>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="#menu" onClick={scrollToMenu}>
                    Menu
                  </a>
                </li>
                <li className="nav-item">
                  <a className="nav-link" href="#about" onClick={scrollToAbout}>
                    About
                  </a>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/book-table">Book Table</Link>
                </li>
              </ul>

              <div className="user_option">
                {/* Kiểm tra nếu chưa đăng nhập thì hiển thị Sign in / Sign up */}
                {!user ? (
                  <>
                    <Link to="/auth" className="btn btn-primary mx-2">Sign in</Link>
                    <Link to="/auth" className="btn btn-secondary">Sign up</Link>
                  </>
                ) : (
                  <>
                    <Link to="/profile" className="user_link" title="Thông tin cá nhân">
  <i className="fa fa-user" aria-hidden="true"></i>
</Link>
<span className="user_name">{user.name}</span>
                    <Link to="/cart" className="cart_link">
                      <i className="fa fa-shopping-cart"></i>
                    </Link>
                    <div style={{ position: 'relative', minWidth: 200 }}>
  <input
    type="text"
    className="form-control"
    placeholder="Tìm kiếm món ăn..."
    value={searchTerm}
    onChange={handleSearchChange}
    onKeyDown={handleSearchKeyDown}
    style={{ paddingRight: 32 }}
  />
  <i className="fa fa-search" style={{ position: 'absolute', right: 10, top: 10, color: '#aaa' }}></i>
  {showSuggestions && suggestions.length > 0 && (
    <ul className="list-group" style={{ position: 'absolute', zIndex: 1000, width: '100%', top: 38 }}>
      {suggestions.map((item, idx) => (
        <li
          key={item.id}
          className="list-group-item list-group-item-action"
          style={{ cursor: 'pointer' }}
          onClick={() => handleSuggestionClick(item)}
        >
          {item.name}
        </li>
      ))}
    </ul>
  )}
</div>
                    <a href="/" className="order_online">Order Online</a>
                    <button className="btn btn-danger mx-2" onClick={logout}>
                      Logout
                    </button>
                  </>
                )}
              </div>
            </div>
          </nav>
        </div>
      </header>
    </div>
  );
};

export default Header;
