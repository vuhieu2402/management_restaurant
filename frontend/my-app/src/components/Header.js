import React, { useContext } from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; 
import "bootstrap/dist/css/bootstrap.min.css";

const Header = () => {
  const { user, logout } = useContext(AuthContext);

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
                  <Link className="nav-link" to="/menu">Menu</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/about">About</Link>
                </li>
                <li className="nav-item">
                  <Link className="nav-link" to="/book">Book Table</Link>
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
                    <span className="user_name">{user.name}</span>
                    <Link to="/" className="user_link">
                      <i className="fa fa-user" aria-hidden="true"></i>
                    </Link>
                    <Link to="/cart" className="cart_link">
                      <i className="fa fa-shopping-cart"></i>
                    </Link>
                    <form className="form-inline">
                  <button className="btn nav_search-btn" type="submit">
                    <i className="fa fa-search" aria-hidden="true"></i>
                  </button>
                </form>
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
